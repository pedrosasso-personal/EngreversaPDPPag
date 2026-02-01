# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-sitp-base-transacoes** é um serviço REST desenvolvido em Spring Boot que realiza consultas de protocolos de transações financeiras. O sistema atua como intermediário entre clientes e duas fontes de dados: um banco de dados Sybase (DBITP) e um serviço externo SPAG (Sistema de Pagamentos). Ele oferece três versões de API (v1, v2 e v3) para consulta de protocolos, validando informações como tipo de movimento (débito/crédito/entrada), data de movimentação e status de protocolos. O sistema implementa lógica de fallback, consultando primeiro o banco local e, caso não encontre informações, recorre ao serviço SPAG.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot |
| **ConsultaAPI.java** | Controller REST que expõe os endpoints de consulta (v1, v2, v3) |
| **ConsultaService.java** | Serviço principal contendo a lógica de negócio para consulta de protocolos |
| **ConsultaSpagService.java** | Serviço responsável pela integração com o sistema SPAG |
| **SITPGestaoFintechRepository.java** | Repositório para acesso ao banco de dados Sybase (DBITP) |
| **ConsultaProtocoloSpagRepository.java** | Repositório para chamadas REST ao serviço SPAG |
| **ConsultaServiceUtil.java** | Utilitário para validações e conversões de protocolos |
| **RequestSpagConverter.java** | Conversor de requisições entre versões de API |
| **ResponseEntityUtil.java** | Utilitário para chamadas HTTP via RestTemplate |
| **AppConfiguration.java** | Configuração de beans da aplicação (ObjectMapper) |
| **RestTemplateConfiguration.java** | Configuração de RestTemplates com autenticação |
| **ConsultaProtocoloSpagProperties.java** | Propriedades de configuração para integração SPAG |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring JDBC** - Para acesso a banco de dados
- **Sybase jConnect 4 (7.07-ESD-5)** - Driver JDBC para Sybase
- **Gradle** - Gerenciamento de dependências e build
- **Lombok** - Redução de código boilerplate
- **Swagger/Springfox 2.8.0** - Documentação de API
- **Jackson** - Serialização/deserialização JSON
- **JaCoCo** - Cobertura de testes
- **SonarQube** - Análise de qualidade de código
- **Docker** - Containerização
- **LDAP** - Autenticação (ambientes não-local)
- **springboot-arqt-base-trilha-auditoria-web** - Biblioteca de auditoria Votorantim
- **springboot-arqt-base-security-basic** - Biblioteca de segurança Votorantim

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /consultar/v1/protocolos | ConsultaAPI | Consulta de múltiplos protocolos (versão 1) |
| POST | /consultar/v2/protocolo | ConsultaAPI | Consulta de protocolo individual com dados detalhados (versão 2) |
| POST | /consultar/v3/protocolo | ConsultaAPI | Consulta de protocolo individual incluindo número de controle SPB (versão 3) |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Movimento**: O sistema determina se uma transação é de ENTRADA, DÉBITO ou CRÉDITO comparando o CNPJ solicitante com os documentos do remetente e favorecido.

2. **Validação de Data de Movimento**: Verifica se o protocolo pertence à data de movimento informada na requisição.

3. **Rejeição de Protocolos de Entrada**: Protocolos identificados como "ENTRADA" para o CNPJ solicitante são rejeitados com erro específico (ECX01/ECX02).

4. **Fallback para SPAG**: Quando o protocolo não é encontrado no banco local ou há inconsistências, o sistema tenta consultar no serviço SPAG externo.

5. **Consulta por Protocolo ou NSU**: O sistema permite consulta tanto por número de protocolo quanto por NSU (Número Sequencial Único) do parceiro.

6. **Conversão de Protocolos ITP/SPAG**: Identifica e converte protocolos no formato ITP (apenas números) e SPAG (com hífen).

7. **Limitação de Consulta**: Na versão v1, permite apenas a consulta de um protocolo por vez.

8. **Enriquecimento de Status**: Traduz códigos de status numéricos para descrições textuais legíveis.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **CaixaEntradaDB**: Representa um protocolo de transação armazenado no banco de dados, contendo informações completas sobre a movimentação financeira.

- **ConsultaProtocolosRequest/Response (v1)**: Request contém lista de protocolos, CNPJ solicitante e data de movimento. Response retorna lista de protocolos com status e dados da transação.

- **ConsultaProtocoloV2Request/ConsultaProtocoloResponse (v2/v3)**: Request contém protocolo individual, NSU, CNPJ e data. Response estruturado em três seções: DadosProtocolo, DadosMovimentacao, Beneficiario e Remetente.

**Relacionamentos:**
- Um protocolo pode ter um **protocoloDevolucao** (referência a outro protocolo)
- Um protocolo pode ter um **protocoloOriginal** (referência ao protocolo que originou uma devolução)
- Cada protocolo está associado a um **remetente** e um **beneficiário**

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Tabela principal de protocolos de entrada SPB |
| DBPGF_TES..TBL_LANCAMENTO | Tabela | SELECT | Tabela de lançamentos da tesouraria |
| DBPGF_TES..TbProcessamentoRoboPGFT | Tabela | SELECT | Processamento de robô PGFT |
| DBPGF_TES..tbSituacaoLancamentoRobo | Tabela | SELECT | Situação de lançamentos processados por robô |
| DBINTEGRACAOITP..TbIntegracaoItpVolta | Tabela | SELECT | Erros de integração ITP |
| DBITP..TBL_STATUS_UNICO_SPB | Tabela | SELECT | Status únicos SPB |
| dbispb..tb_movi_movimento | Tabela | SELECT | Movimentos SPB |
| dbispb..tb_erms_erro_mensagem | Tabela | SELECT | Mensagens de erro SPB |
| dbispb..tb_cder_codigo_erro | Tabela | SELECT | Códigos de erro SPB |

**Stored Procedures:**
- **DBPGF_TES..PrConsultarProtocolo** - Consulta protocolo por código
- **DBPGF_TES..PrConsultarProtocoloV2** - Consulta protocolo por código e NSU

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log/ | Configuração de logs da aplicação |
| sitpgestaofintechrepository-sql.xml | leitura | resources/database/ | Queries SQL para consultas ao banco |
| application.yml | leitura | resources/ | Configurações da aplicação |
| application-local.yml | leitura | resources/ | Configurações para ambiente local |
| roles/local.yml | leitura | resources/roles/ | Configuração de roles para ambiente local |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| **SPAG (Sistema de Pagamentos)** | API REST | Sistema externo de consulta de protocolos de conta fintech. Possui três endpoints (v1, v2, v3) consumidos via RestTemplate com autenticação básica. URLs configuráveis por ambiente. |
| **LDAP BVNet** | Serviço de Autenticação | Autenticação de usuários via LDAP em ambientes não-locais (des, qa, uat, prd). |
| **Banco Sybase (DBITP)** | Banco de Dados | Banco de dados principal contendo informações de protocolos, lançamentos e integrações. |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre camadas (controller, service, repository)
- Uso adequado de anotações Lombok reduzindo boilerplate
- Implementação de versionamento de API (v1, v2, v3)
- Documentação Swagger configurada
- Tratamento de exceções presente
- Uso de properties externalizadas
- Logs estruturados com SLF4J

**Pontos de Melhoria:**
- Código comentado em várias partes (ex: `//consultarProtocoloNoSpag = true;`)
- Lógica de negócio complexa em métodos longos (ex: `consultarProtocolosV1`, `consultarProtocoloV2`)
- Duplicação de código entre `consultarProtocoloV2` e `consultarProtocoloV3`
- Falta de testes unitários incluídos na análise
- Mensagens de erro hardcoded em português misturadas com códigos (ECX01, E01, E02, E03)
- Uso de `Boolean.TRUE.equals()` desnecessário em alguns pontos
- Queries SQL embutidas em XML ao invés de usar JPA/Hibernate
- Falta de validação mais robusta de entrada em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura de Fallback**: O sistema implementa uma estratégia interessante de fallback, consultando primeiro o banco local e, em caso de falha ou não localização, recorrendo ao serviço SPAG.

2. **Múltiplas Versões de API**: O sistema mantém três versões de API simultaneamente, sendo que v2 e v3 são praticamente idênticas, diferindo apenas no retorno do campo `nuControleSPB`.

3. **Dependências Legadas**: Utiliza bibliotecas proprietárias da Votorantim (`br.com.votorantim.arqt.base`) que podem dificultar manutenção fora do contexto organizacional.

4. **Banco de Dados Sybase**: Uso de banco de dados Sybase, que é menos comum atualmente, com stored procedures específicas.

5. **Ambientes Múltiplos**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd) com diferentes configurações de segurança.

6. **Autenticação Dual**: Sistema suporta autenticação in-memory para ambiente local e LDAP para ambientes corporativos.

7. **Containerização**: Projeto preparado para deploy em containers Docker com configurações específicas de infraestrutura como código (infra.yml).

8. **Timeout Configurável**: Integração com SPAG possui timeout de 30 segundos configurado.