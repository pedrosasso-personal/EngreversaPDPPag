# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de validação de débitos veiculares desenvolvido em Spring Boot. O sistema oferece serviços REST para consulta e validação de débitos veiculares, incluindo funcionalidades para buscar informações de arrecadadores, validar CNPJs de fintechs, consultar débitos veiculares e validar liquidações. Utiliza arquitetura hexagonal (ports and adapters) com separação clara entre camadas de domínio, aplicação e infraestrutura.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot para inicialização da aplicação |
| `ValidaDebitosController` | Controller REST para endpoints de validação de débitos veiculares |
| `ValidaLiquidacaoController` | Controller REST para endpoints de validação de liquidação veicular |
| `ValidaDebitosVeicularesService` | Serviço de domínio para regras de negócio de débitos veiculares |
| `ValidaLiquidacaoVeicularService` | Serviço de domínio para regras de negócio de liquidação |
| `JdbiValidaDebitosVeicularesRepositoryImpl` | Implementação do repositório usando JDBI para débitos veiculares |
| `JdbiValidaLiquidacaoVeicularRepositoryImpl` | Implementação do repositório usando JDBI para liquidação |
| `ValidaDebitosVeicularesConfiguration` | Configuração Spring para beans e dependências |
| `ResourceExceptionHandler` | Tratamento centralizado de exceções |
| `ValidaDebitosVeicularesException` | Exceção customizada para erros de negócio |
| `CodigoErroEnum` | Enumeração de códigos de erro do sistema |
| `ValidaDebitosMapper` | Mapeamento entre objetos de domínio e representação |
| `ValidaLiquidacaoMapper` | Mapeamento para objetos de liquidação |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven
- **Banco de Dados**: Microsoft SQL Server
- **Acesso a Dados**: JDBI 3.9.1
- **Driver JDBC**: Microsoft SQL Server JDBC Driver 7.4.0
- **Documentação API**: Swagger/OpenAPI (Springfox 3.0.0)
- **Mapeamento de Objetos**: MapStruct 1.3.1
- **Utilitários**: Lombok
- **Monitoramento**: Spring Boot Actuator, Micrometer Prometheus
- **Auditoria**: BV Audit 2.2.1
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact
- **Containerização**: Docker
- **Observabilidade**: Prometheus, Grafana

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/valida-debitos-veiculares/buscaCnpj` | ValidaDebitosController | Busca CNPJ de Fintech por clientId |
| GET | `/valida-debitos-veiculares/buscaDebito` | ValidaDebitosController | Busca débito veicular por CNPJ e protocolo |
| GET | `/valida-debitos-veiculares/buscaDebitoId` | ValidaDebitosController | Busca débito veicular por transaction ID |
| GET | `/valida-debitos-veiculares/buscaArrecadadores` | ValidaDebitosController | Lista todos os arrecadadores |
| GET | `/valida-liquidacao-veicular/buscaDebitoVeicular` | ValidaLiquidacaoController | Busca débito veicular para liquidação |
| GET | `/valida-liquidacao-veicular/buscaContaArrecadador` | ValidaLiquidacaoController | Busca conta do arrecadador |
| GET | `/valida-liquidacao-veicular/buscaSolicitacaoPagamento` | ValidaLiquidacaoController | Busca solicitações de pagamento |
| GET | `/valida-liquidacao-veicular/liquidacaoDebitoVeicular` | ValidaLiquidacaoController | Busca liquidações de débito veicular |

## 5. Principais Regras de Negócio

- **Validação de CNPJ**: Sistema valida formato de CNPJ antes de realizar consultas
- **Validação de Campos Obrigatórios**: Verifica presença de campos obrigatórios (clientId, nuProtocoloSolicitacaoCliente, transactionId)
- **Consulta de Débitos**: Permite busca de débitos por protocolo/CNPJ ou por transaction ID
- **Validação de Liquidação**: Verifica débitos não pagos do dia atual para liquidação
- **Gestão de Arrecadadores**: Mantém cadastro de arrecadadores e suas contas
- **Tratamento de Erros**: Sistema possui enumeração completa de códigos de erro com mensagens descritivas
- **Auditoria**: Registra operações através do componente BV Audit

## 6. Relação entre Entidades

**Entidades Principais:**

- **ValidaDebitosVeiculares**: Entidade raiz do domínio
- **BuscaDebitoResponseDomain**: Representa resultado de consulta de débito (contém cdConsultaDebitoVeicular, stLancamento, nuCpfCnpjFintech, placa, renavam, estado, etc.)
- **BuscaDebitoVeicularDomain**: Representa débito veicular completo com informações de arrecadador
- **ArrecadadorDomain**: Representa arrecadador (cdArrecadador, nuCpfCnpj, nmRazaoSocial, flAtivo)
- **ContaArrecadadorDomain**: Representa conta bancária do arrecadador
- **LiquidacaoDebitoVeicular**: Representa liquidação de débito (cdAutenticacaoBancaria, cdDebitoVeicular, stLancamento, vrDebitoVeicular)
- **PagamentoSolicitadoDomain**: Representa solicitação de pagamento

**Relacionamentos:**
- Débito Veicular possui relacionamento com Arrecadador (cdArrecadador)
- Arrecadador possui Conta Arrecadador
- Débito Veicular pode ter múltiplas Liquidações
- Liquidação está associada a Lançamento

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Consulta CNPJ de fintech por indicador de interface |
| TbConsultaDebitoVeicular | tabela | SELECT | Consulta débitos veiculares por protocolo/CNPJ ou transaction ID |
| TbArrecadador | tabela | SELECT | Lista arrecadadores cadastrados |
| TbContaArrecadador | tabela | SELECT | Consulta conta bancária do arrecadador |
| TbLancamento | tabela | SELECT | Consulta lançamentos de pagamento |
| TbLancamentoDebitoVeicular | tabela | SELECT | Consulta lançamentos específicos de débitos veiculares |

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log (configurável por ambiente) | Configuração de logs da aplicação |
| application.yml | leitura | resources/ | Configurações da aplicação Spring Boot |
| *.sql | leitura | resources/br/com/votorantim/spag/base/valida/debitos/veiculares/infrastructure/database/ | Queries SQL utilizadas pelo JDBI |
| sboot-spag-base-atom-valida-debitos-veiculares.yaml | leitura | resources/swagger/ | Especificação OpenAPI dos endpoints |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Microsoft SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal para consulta de débitos veiculares, arrecadadores e liquidações |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |
| Grafana | Observabilidade | Visualização de métricas e dashboards |
| API Gateway BV | Autenticação | Validação de tokens JWT (OAuth2) |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura hexagonal bem implementada com separação clara de responsabilidades (domain, application, infrastructure)
- Uso adequado de padrões como Repository, Service e Mapper
- Tratamento de exceções centralizado e bem estruturado
- Boa cobertura de testes (unitários, integração e funcionais)
- Uso de tecnologias modernas e adequadas (JDBI, MapStruct, Lombok)
- Documentação OpenAPI completa
- Configuração adequada de observabilidade (Prometheus/Grafana)
- Código limpo e legível com nomenclatura consistente

**Pontos de Melhoria:**
- Algumas classes de domínio poderiam ter validações mais robustas
- Falta de documentação JavaDoc em algumas classes importantes
- Alguns métodos de serviço poderiam ser mais granulares
- Configurações de ambiente poderiam estar mais centralizadas
- Ausência de cache para consultas frequentes

## 14. Observações Relevantes

- O sistema utiliza perfis Spring (local, des, qa, uat, prd) para configuração por ambiente
- Implementa auditoria através do componente BV Audit
- Possui infraestrutura como código (infra-as-code) para deploy em OpenShift
- Utiliza JDBI ao invés de JPA/Hibernate para acesso a dados, proporcionando maior controle sobre queries SQL
- Configuração de logs em formato JSON para ambientes não-locais
- Sistema preparado para containerização com Docker
- Implementa health checks através do Spring Actuator
- Possui pipeline Jenkins configurado (jenkins.properties)
- Utiliza HikariCP como pool de conexões
- Implementa testes de contrato com Pact
- Configuração de segurança OAuth2 com JWT
- Métricas expostas no formato Prometheus
- Dashboard Grafana pré-configurado para monitoramento