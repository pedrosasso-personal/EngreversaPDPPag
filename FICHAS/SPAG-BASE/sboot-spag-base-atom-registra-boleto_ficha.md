# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema atômico responsável pelo registro de boletos e lançamentos no contexto de pagamentos. O sistema oferece funcionalidades para registrar boletos de baixa operacional CIP, registrar lançamentos financeiros, buscar informações de registros e obter dados de boletos. Atua como um serviço de integração entre sistemas de pagamento e bases de dados legadas (Sybase).

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `RegistraBoletoController` | Controller REST para registro de boletos |
| `RegistraLancamentoController` | Controller REST para registro de lançamentos |
| `BuscaRegistroController` | Controller REST para busca de registros |
| `BuscaDadosBoletoController` | Controller REST para busca de dados de boletos |
| `RegistraBoletoServiceImpl` | Implementação da lógica de negócio para registro de boletos |
| `RegistraLancamentoServiceImpl` | Implementação da lógica de negócio para registro de lançamentos |
| `BuscaRegistroServiceImpl` | Implementação da lógica de busca de registros |
| `BuscaDadosBoletoServiceImpl` | Implementação da lógica de busca de dados de boletos |
| `JdbiRegistraBoletoRepository` | Repositório JDBI para operações de registro de boleto |
| `JdbiRegistraLancamentoRepository` | Repositório JDBI para operações de lançamento |
| `JdbiBuscaRegistroRepository` | Repositório JDBI para busca de registros |
| `JdbiBuscaDadosBoletoRepository` | Repositório JDBI para busca de dados de boletos |
| `RegistraBoletoConfiguration` | Configuração de beans e dependências da aplicação |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI |

## 3. Tecnologias Utilizadas
- **Framework:** Spring Boot 2.x
- **Java:** JDK 11
- **Persistência:** JDBI 3.9.1
- **Banco de Dados:** Sybase ASE (jConnect 16.3)
- **Documentação API:** Springfox Swagger 3.0.0
- **Segurança:** Spring Security OAuth2 (JWT)
- **Monitoramento:** Spring Actuator + Micrometer + Prometheus
- **Mapeamento:** MapStruct 1.3.1
- **Build:** Maven
- **Containerização:** Docker
- **Orquestração:** Kubernetes/OpenShift
- **Logs:** Logback
- **Testes:** JUnit 5, Mockito, Rest Assured, Pact

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/registra-boleto | RegistraBoletoController | Registra um boleto de baixa operacional |
| POST | /v1/registra-lancamento | RegistraLancamentoController | Registra um lançamento financeiro |
| GET | /v1/busca-registro/{protocolo} | BuscaRegistroController | Busca informações de registro por protocolo |
| GET | /v1/obter-dados-boleto/{cdLancamentoPgft} | BuscaDadosBoletoController | Obtém dados de um boleto por código de lançamento |

## 5. Principais Regras de Negócio
- **Registro de Boleto:** Valida tipo de pessoa e CPF/CNPJ do portador ou remetente antes de registrar. Define recebedor baseado no código do banco (413 ou 655). Registra na tabela `TbRegistroPagamentoCIP` com controle de sequencial.
- **Registro de Lançamento:** Verifica se já existe lançamento para o protocolo antes de criar novo. Obtém sequencial disponível através de procedure. Insere na tabela `TBL_LANCAMENTO` com diversos dados financeiros e de partes envolvidas.
- **Busca de Registro:** Retorna informações de baixa operacional aceita vinculada ao protocolo informado.
- **Busca de Dados de Boleto:** Retorna informações do boleto incluindo status, valores e flag de baixa.

## 6. Relação entre Entidades

**Entidades Principais:**
- `DadosBoleto`: Representa dados de um boleto (valor, datas, status, código de barras, flag de baixa)
- `RegistraBoletoDto`: DTO para registro de boleto com dados de pagamento e partes envolvidas
- `RegistraLancamentoDto`: DTO para registro de lançamento com informações financeiras completas
- `RegistroInfo`: Informações de registro contendo dados de pagamento, ISPB e instituições financeiras
- `PagamentoInfo`: Dados de pagamento (data, valor, código do título, código de barras)
- `IspbInfo`: Informações de ISPB (recebedor principal e administrado)
- `InstituicaoFinanceira`: Dados de instituições (remetente e favorecido)
- `Protocolo`: Número de protocolo do lançamento

**Relacionamentos:**
- `RegistroInfo` contém `PagamentoInfo`, `IspbInfo` e `InstituicaoFinanceira`
- Boletos são vinculados a lançamentos através do código de lançamento
- Registros são identificados por protocolo

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES.dbo.TBL_LANCAMENTO | Tabela | SELECT | Busca dados de lançamento por código |
| DBPGF_TES..TbRetornoBaixaOperacionalCIP | Tabela | SELECT | Busca informações de baixa operacional CIP |
| DBPGF_TES..TbRegistroPagamentoCIP | Tabela | SELECT | Busca registro de pagamento CIP |
| DBITP..TBL_CAIXA_ENTRADA_SPB | Tabela | SELECT | Busca dados de caixa de entrada SPB |
| TbSequencial | Tabela | SELECT/UPDATE | Controle de sequenciais para geração de IDs |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbRegistroPagamentoCIP | Tabela | INSERT | Insere novo registro de pagamento CIP |
| TbSequencial | Tabela | UPDATE | Atualiza sequencial disponível |
| TBL_LANCAMENTO | Tabela | INSERT | Insere novo lançamento financeiro |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs |
| swagger/sboot-spag-base-atom-registra-boleto.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |
| *.sql | Leitura | JDBI | Queries SQL para operações de banco |

## 10. Filas Lidas
Não se aplica - o sistema não consome mensagens de filas.

## 11. Filas Geradas
Não se aplica - o sistema não publica mensagens em filas.

## 12. Integrações Externas
- **Banco de Dados Sybase:** Integração com bases DBPGF_TES e DBITP para operações de leitura e escrita de dados de boletos e lançamentos
- **OAuth2/JWT:** Integração com servidor de autenticação para validação de tokens JWT (URLs variam por ambiente: des, qa, uat, prd)
- **Prometheus:** Exportação de métricas para monitoramento

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**
O código apresenta boa organização arquitetural seguindo padrões de separação de responsabilidades (controllers, services, repositories). Utiliza frameworks modernos e boas práticas como injeção de dependências, uso de DTOs e interfaces. Pontos positivos incluem: uso de Lombok para reduzir boilerplate, configuração adequada de profiles por ambiente, implementação de testes unitários, e documentação via Swagger.

Porém, há pontos de melhoria: lógica de negócio com strings hardcoded (códigos de banco), tratamento de exceções genérico em alguns pontos, falta de validações mais robustas nos DTOs, queries SQL embutidas em arquivos separados (boa prática) mas sem documentação adequada, e alguns métodos com muitos parâmetros que poderiam ser encapsulados em objetos. A cobertura de testes poderia ser mais abrangente, especialmente nos repositórios e mapeadores.

## 14. Observações Relevantes
- Sistema utiliza arquitetura hexagonal/ports and adapters com clara separação entre domain, application e infrastructure
- Configuração multi-ambiente bem estruturada (local, des, qa, uat, prd)
- Implementa controle de sequenciais através de tabela dedicada com transações
- Utiliza JDBI ao invés de JPA/Hibernate, adequado para queries complexas e controle fino de SQL
- Possui infraestrutura completa de observabilidade (Prometheus, Grafana)
- Configuração de segurança OAuth2 com JWT para autenticação
- Dockerização e preparação para deploy em Kubernetes/OpenShift
- Seguindo padrões de nomenclatura e organização do Banco Votorantim
- Sistema crítico para operações de pagamento, requer alta disponibilidade e consistência de dados