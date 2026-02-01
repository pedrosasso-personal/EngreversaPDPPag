# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-integracao-ltr** é um serviço atômico desenvolvido em Spring Boot para integração com o sistema LTR (Liquidação de Títulos e Registros) do SPB (Sistema de Pagamentos Brasileiro). O sistema é responsável por:

- Consultar mensagens LTR de diversos tipos (LTR0001, LTR0002, LTR0004, LTR0007, LTR0008, SLC0005, etc.)
- Integrar novas mensagens LTR (LTR0002, LTR0004, LTR0008)
- Gerenciar o status e controle de mensagens processadas
- Consultar erros relacionados às mensagens LTR
- Realizar operações de atualização e desativação de mensagens

O sistema atua como intermediário entre aplicações internas do Banco Votorantim e o sistema LTR do Banco Central, facilitando o processamento de operações de liquidação e transferência de recursos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **IntegracaoLtrController** | Controlador REST que expõe os endpoints da API |
| **ConsultaLtrService** | Serviço de domínio para consulta de mensagens LTR |
| **IntegracaoLtrService** | Serviço de domínio para integração de novas mensagens LTR |
| **OperacoesLtrService** | Serviço de domínio para operações de atualização e desativação |
| **IntegracaoLtrRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao banco |
| **IntegracaoLtrMapper** | Mapper para conversão entre representations e objetos de domínio |
| **MensagensSPBMapper** | Mapper para conversão de mensagens SPB para objetos LTR específicos |
| **IntegracaoSpagMapper** | Mapper para conversão de objetos LTR para LTRProc |
| **DataHoraUtil** | Utilitário para manipulação e validação de datas/horas |
| **ExceptionControllerHandler** | Handler centralizado para tratamento de exceções |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring Security OAuth2** - Segurança e autenticação JWT
- **JDBI 3.9.1** - Framework de acesso a dados
- **Microsoft SQL Server** - Banco de dados (driver 7.4.0.jre11)
- **Swagger/Springfox 3.0.0** - Documentação de API
- **Lombok** - Redução de código boilerplate
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Framework de logging
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Rest Assured** - Testes funcionais de API
- **Pact** - Testes de contrato
- **Maven** - Gerenciamento de dependências e build
- **Docker** - Containerização
- **Grafana/Prometheus** - Observabilidade

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/mensagensLTR/{codigoMensagem} | IntegracaoLtrController | Consulta mensagens LTR por tipo, data ou número de controle |
| GET | /v1/mensagensLTR/erro/{codigoMensagem} | IntegracaoLtrController | Consulta mensagens de erro LTR |
| PUT | /v1/mensagensLTR/desativarStatus | IntegracaoLtrController | Desativa o status de uma mensagem |
| PUT | /v1/mensagensLTR/numeroControleIF | IntegracaoLtrController | Atualiza o número de controle IF de uma mensagem |
| POST | /v1/mensagensLTR0002 | IntegracaoLtrController | Integra uma nova mensagem LTR0002 |
| POST | /v1/mensagensLTR0004 | IntegracaoLtrController | Integra uma nova mensagem LTR0004 |
| POST | /v1/mensagensLTR0008 | IntegracaoLtrController | Integra uma nova mensagem LTR0008 |

---

## 5. Principais Regras de Negócio

1. **Validação de Período de Consulta**: O intervalo entre data inicial e final não pode ultrapassar 24 horas
2. **Validação de Datas**: A data inicial não pode ser posterior à data final
3. **Obrigatoriedade de Parâmetros**: Para consultas, é obrigatório informar ou o número de controle IF ou o período (data inicial e final)
4. **Conversão de Tipos de Mensagem**: O sistema converte diferentes tipos de mensagens LTR (LTR0001, LTR0002, LTR0004, LTR0007, LTR0008, etc.) para formatos específicos
5. **Tratamento de Erros**: Mensagens de erro são consultadas separadamente e associadas ao número de controle IF
6. **Status de Mensagens**: Mensagens podem ser desativadas (flag FlAtivo = 'N') mas não são excluídas fisicamente
7. **Auditoria**: Todas as operações registram data/hora de inclusão e alteração, além do login do usuário
8. **Integração com Stored Procedure**: A integração de novas mensagens é realizada através da procedure `PrIncluirMensagemLTR`
9. **Validação de Retorno**: A integração valida se o código de processamento LTR foi gerado com sucesso
10. **Formatação de Datas**: Datas são formatadas no padrão ISO 8601 (yyyy-MM-dd'T'HH:mm:ss) para entrada e saída

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MensagemSPB**: Entidade principal que representa uma mensagem do SPB armazenada na tabela TbProcessamentoLTR
- **IdentificacaoErro**: Representa erros associados a uma mensagem, armazenados na TbProcessamentoLTRErro
- **LTRProc**: Objeto de transferência usado para integração com a stored procedure
- **LTR0001, LTR0002, LTR0004, LTR0007, LTR0008, SLC0005**: Representações específicas de cada tipo de mensagem LTR

**Relacionamentos:**

- MensagemSPB (1) ←→ (N) IdentificacaoErro: Uma mensagem pode ter múltiplos erros associados
- MensagemSPB é mapeada a partir de diferentes tipos de mensagens LTR através dos mappers
- Todas as mensagens compartilham campos comuns como número de controle, ISPB, datas, etc.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessamentoLTR | Tabela | SELECT | Tabela principal que armazena todas as mensagens LTR processadas |
| TbProcessamentoLTRErro | Tabela | SELECT | Tabela que armazena os erros associados às mensagens LTR |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbProcessamentoLTR | Tabela | UPDATE | Atualização do número de controle IF e flag de ativo |
| TbProcessamentoLTR | Tabela | INSERT | Inserção de novas mensagens LTR via stored procedure |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | /usr/etc/log | Arquivo de configuração de logs, varia por ambiente (des/qa/uat/prd) |
| application.yml | Leitura | Classpath resources | Arquivo de configuração da aplicação Spring Boot |
| *.sql | Leitura | Classpath resources | Arquivos SQL usados pelo JDBI para queries (consultarMensagens, consultarErros, etc.) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal onde são armazenadas as mensagens LTR e erros |
| OAuth2/JWT Provider | Autenticação | Serviço de autenticação para validação de tokens JWT (apigateway.bvnet.bv) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |
| Sistema LTR (indireto) | Sistema Externo | Sistema do Banco Central para liquidação de títulos (integração via banco de dados) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo princípios de Clean Architecture (separação em camadas: domain, application, common)
- Uso adequado de padrões de projeto (Repository, Service, Mapper)
- Boa cobertura de testes unitários e estrutura para testes de integração e funcionais
- Tratamento centralizado de exceções
- Uso de DTOs e separação clara entre objetos de domínio e representações
- Configuração adequada de segurança com OAuth2/JWT
- Documentação de API com Swagger
- Uso de Lombok para redução de boilerplate
- Configuração de observabilidade (Prometheus/Grafana)

**Pontos de Melhoria:**
- Alguns métodos poderiam ser mais granulares (ex: métodos de mapper muito extensos)
- Falta de documentação JavaDoc em algumas classes importantes
- Alguns magic numbers e strings hardcoded poderiam ser constantes
- Validações de negócio poderiam estar mais centralizadas
- Alguns métodos de teste poderiam ter nomes mais descritivos

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está dividido em três módulos Maven (common, domain, application), facilitando a manutenção e evolução
2. **Múltiplos Ambientes**: Configuração preparada para múltiplos ambientes (local, des, qa, uat, prd)
3. **Stored Procedure**: A integração principal utiliza uma stored procedure SQL Server (`PrIncluirMensagemLTR`) com 47 parâmetros
4. **Tipos de Mensagem**: O sistema suporta 14 tipos diferentes de mensagens LTR (LTR0001, LTR0002, LTR0004, LTR0007, LTR0008, LTR0008R1, LTR0002R1, LTR0004R1, LTR0005R2, LTR0006R2, LTR0008E, LTR0004E, LTR0002E, SLC0005)
5. **Formato de Data**: Sistema trabalha com formato ISO 8601 e realiza conversões específicas para consultas no banco
6. **Auditoria**: Todas as operações registram usuário (dsLogin) e timestamps de inclusão/alteração
7. **Soft Delete**: O sistema utiliza soft delete através da flag FlAtivo ao invés de exclusão física
8. **Containerização**: Projeto preparado para execução em containers Docker/OpenShift
9. **CI/CD**: Configuração Jenkins presente para pipeline de integração contínua
10. **Segurança**: Endpoints protegidos por OAuth2, exceto Swagger UI