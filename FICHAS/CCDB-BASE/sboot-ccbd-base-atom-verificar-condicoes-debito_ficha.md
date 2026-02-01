# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-atom-verificar-condicoes-debito** é um microserviço atômico desenvolvido em Java com Spring Boot, pertencente ao domínio CCBD (Cartão de Crédito e Débito) do Banco Votorantim. Seu objetivo principal é verificar e consultar condições de transações de débito em cartão, permitindo consultas por NSU (Número Sequencial Único), identificador de transação ou parâmetros específicos da bandeira Visa. O sistema também gerencia um checklist de recebimento de arquivos relacionados às transações e fornece consultas completas de informações transacionais.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **VerificarCondicoesDebitoController** | Controlador REST que expõe os endpoints da API |
| **VerificarCondicoesDebitoServiceImpl** | Implementação da lógica de negócio para consultas e atualizações |
| **CCBDRepositoryImpl** | Implementação do repositório com acesso ao banco de dados via JDBI |
| **VerificarCondicoesDebitoValidator** | Validador de regras de entrada e conversão de datas |
| **CheckListMapper** | Mapeador para conversão entre objetos de domínio e representação |
| **VerificarCondicoesDebitoMapper** | Mapeador para conversão de respostas de consulta |
| **DataBaseConfiguration** | Configuração do JDBI e datasource |
| **VerificarCondicoesDebitoConfiguration** | Configuração de beans do domínio |
| **CheckList** | Entidade de domínio representando o checklist de arquivos |
| **ConsultarCondicoesResponse** | Entidade de resposta para consultas de condições |
| **ConsultaInfoTransacaoCompleta** | Entidade com informações completas de transação |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJ9)
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação JWT)
- **JDBI 3.9.1** (acesso a dados)
- **Microsoft SQL Server** (banco de dados)
- **StringTemplate4** (templates SQL dinâmicos)
- **Lombok** (redução de boilerplate)
- **Spring Actuator** (monitoramento e métricas)
- **Prometheus/Grafana** (observabilidade)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)
- **OpenAPI 3.0** (documentação de API)
- **Logback** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/verificar-condicoes-debito/consultar` | VerificarCondicoesDebitoController | Consulta condições de débito por NSU ou identificador de transação |
| GET | `/v1/verificar-condicoes-debito/visa-consultar` | VerificarCondicoesDebitoController | Consulta condições de débito específicas da bandeira Visa por autorizador, data e valor |
| PUT | `/v1/update-check-list` | VerificarCondicoesDebitoController | Atualiza o checklist de recebimento de arquivos |
| GET | `/v1/consulta/transacao` | VerificarCondicoesDebitoController | Consulta informações completas de transações por conta e período |

---

## 5. Principais Regras de Negócio

1. **Validação de Entrada**: Ao consultar condições, pelo menos um dos parâmetros (NSU ou identificador de transação) deve ser informado
2. **Consulta Visa**: Para transações Visa, realiza busca por valor, data e tipo de transação, filtrando pelos últimos 6 dígitos do autorizador
3. **Filtro de Status**: Consultas Visa consideram apenas transações com status '00' (aprovada)
4. **Conversão de Datas**: Datas são convertidas para intervalos completos (início: 00:00:00, fim: 23:59:59)
5. **Atualização Dinâmica**: O checklist é atualizado dinamicamente apenas com os campos informados, usando templates SQL condicionais
6. **Busca Hierárquica**: Após encontrar transação Visa por filtros, busca detalhes completos pelo NSU
7. **Consulta por Período**: Permite consultas com ou sem filtro de período de datas

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **CheckList**: Representa o checklist de recebimento de arquivos relacionados a transações (advice, TIF, bandeira, etc.)
  - Relaciona-se com transações aprovadas e de estorno
  - Contém timestamps de recebimento de diversos tipos de arquivos

- **ConsultarCondicoesResponse**: Representa dados básicos de uma transação de cartão
  - Contém informações de controle, valores, status e identificadores

- **ConsultaInfoTransacaoCompleta**: Estende ConsultarCondicoesResponse incluindo dados do checklist
  - Relacionamento: uma transação possui um checklist associado

**Relacionamentos:**
- CheckList ↔ TbControleTransacaoCartao (1:1 via cdControleTransacaoCartaoAprovado)
- TbControleTransacaoCartao ↔ TbCheckListTransacaoArquivo (1:1)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDTransacaoCartaoDebito.TbControleTransacaoCartao | Tabela | SELECT | Tabela principal de controle de transações de cartão de débito |
| DBCCBD.CCBDTransacaoCartaoDebito.TbCheckListTransacaoArquivo | Tabela | SELECT | Tabela de checklist de recebimento de arquivos relacionados às transações |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCCBD.CCBDTransacaoCartaoDebito.TbCheckListTransacaoArquivo | Tabela | UPDATE | Atualização do checklist de recebimento de arquivos (advice, TIF, bandeira, etc.) |

---

## 9. Arquivos Lidos e Gravados

não se aplica

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Gateway BV | Autenticação | Validação de tokens JWT via JWKS (ambientes DES, UAT, PRD) |
| SQL Server (SQLDES35/SQLUAT35/SQLPRD35) | Banco de Dados | Acesso ao banco DBCCBD para consulta e atualização de transações |
| Prometheus/Grafana | Observabilidade | Exportação de métricas via Spring Actuator |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository, mapper)
- Uso adequado de padrões como Repository e Service
- Configuração externalizada por profiles (local, des, uat, prd)
- Uso de JDBI com SQL externalizado em arquivos .sql
- Documentação OpenAPI bem estruturada
- Uso de Lombok para reduzir boilerplate
- Implementação de segurança com OAuth2/JWT

**Pontos de Melhoria:**
- Tratamento de exceções genérico (catch Exception) em alguns métodos
- Falta de testes unitários incluídos na análise
- Código comentado no pom.xml deveria ser removido
- Validações poderiam ser mais robustas (uso de Bean Validation)
- Alguns métodos com lógica complexa poderiam ser refatorados (ex: consultarVisaCondicoes)
- Falta de documentação JavaDoc nas classes
- Uso de Optional.ofNullable().isEmpty() poderia ser simplificado
- Logs poderiam ser mais estruturados e informativos

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema está configurado para 4 ambientes (local, des, uat, prd) com credenciais gerenciadas por cofre de senhas
2. **Segurança**: Todos os endpoints são protegidos por autenticação Bearer JWT, exceto endpoints públicos (swagger, actuator)
3. **Monitoramento**: Exposição de métricas via Actuator na porta 9090 (separada da porta de aplicação 8080)
4. **SQL Dinâmico**: Uso de StringTemplate4 para construção dinâmica de queries SQL com condicionais
5. **Containerização**: Aplicação preparada para execução em container Docker com OpenJ9 JVM
6. **Infraestrutura como Código**: Configuração de infraestrutura via arquivo infra.yml para deploy automatizado
7. **Banco de Dados**: Utiliza SQL Server com schema CCBDTransacaoCartaoDebito
8. **Padrão de Nomenclatura**: Prefixos consistentes (cd=código, nu=número, st=status, dt=data, vr=valor)
9. **Parent POM**: Herda de pom-atle-base-sboot-atom-parent versão 2.1.2 (padrão Atlante do Banco Votorantim)
10. **Limitações**: Não há implementação de cache, o que pode impactar performance em consultas frequentes