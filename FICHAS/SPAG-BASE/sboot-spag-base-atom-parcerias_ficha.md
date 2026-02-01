# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-spag-base-atom-parcerias** é um serviço atômico REST desenvolvido em Java com Spring Boot, responsável por gerenciar informações de parcerias do sistema SPAG (Sistema de Pagamentos). O sistema oferece funcionalidades para consulta e validação de fintechs, correspondentes bancários, clientes e gerenciamento de correspondências de TED (Transferência Eletrônica Disponível). Atua como um componente de integração que centraliza informações de parceiros comerciais e suas configurações de liquidação.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ParceriasController** | Controlador REST principal para endpoints de consulta de fintechs, correspondentes e clientes |
| **CorrespondenciaTedController** | Controlador REST para gerenciamento de correspondências de TED |
| **FintechService** | Serviço de domínio para lógica de negócio relacionada a fintechs e clientes |
| **CorrespondenciaTedService** | Serviço de domínio para operações de correspondência TED |
| **CorrespondenteService** | Serviço de domínio para validação de correspondentes bancários |
| **FintechRepositoryImpl** | Implementação JDBI para acesso a dados de fintechs e clientes |
| **CorrespondeciaTedRepositoryImpl** | Implementação JDBI para acesso a dados de correspondências TED |
| **CorrespondenteRepositoryImpl** | Implementação JDBI para acesso a dados de correspondentes |
| **CustomExceptionHandler** | Tratamento centralizado de exceções da aplicação |
| **JdbiConfiguration** | Configuração do framework JDBI para acesso a dados |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Security OAuth2** (autenticação e autorização)
- **JDBI 3.9.1** (framework de acesso a dados)
- **Microsoft SQL Server** (banco de dados)
- **MapStruct 1.3.1** (mapeamento de objetos)
- **Springfox/Swagger 3.0.0** (documentação de API)
- **Lombok** (redução de boilerplate)
- **Maven** (gerenciamento de dependências)
- **Micrometer/Prometheus** (métricas e monitoramento)
- **Logback** (logging)
- **JUnit 5 + Mockito** (testes unitários)
- **REST Assured** (testes funcionais)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/parcerias/buscarFintech/` | ParceriasController | Busca dados de fintech por CNPJ e código de liquidação |
| GET | `/v1/parcerias/validarCorrespondente` | ParceriasController | Valida se um correspondente é válido através de CNPJ e conta |
| GET | `/v1/parcerias/buscarCliente` | ParceriasController | Busca cliente (Wallet/Fintech/Comum) por CNPJ, conta e liquidação |
| GET | `/v1/parcerias/buscarClientePorCdOrigem` | ParceriasController | Busca cliente incluindo código de origem para estornos |
| POST | `/v1/parcerias/buscar-parceiro` | ParceriasController | Busca unificada de parceiro com múltiplos parâmetros |
| POST | `/correspondencia-ted` | CorrespondenciaTedController | Insere nova correspondência de TED |
| GET | `/correspondencia-ted` | CorrespondenciaTedController | Busca paginada de correspondências TED com filtros |
| GET | `/correspondencia-ted/{id}` | CorrespondenciaTedController | Busca correspondência TED por ID |
| PUT | `/correspondencia-ted/{id}` | CorrespondenciaTedController | Atualiza correspondência TED existente |
| PUT | `/correspondencia-ted/rejeicao` | CorrespondenciaTedController | Rejeita múltiplas correspondências TED |
| GET | `/correspondencia-ted/max-codigo-lancamento` | CorrespondenciaTedController | Retorna o último código de lançamento inserido |
| GET | `/correspondencia-ted/analistas` | CorrespondenciaTedController | Lista analistas que realizaram correspondências |

---

## 5. Principais Regras de Negócio

1. **Validação de Correspondente**: Verifica se um correspondente bancário está ativo através de CNPJ e número de conta
2. **Busca de Cliente por Tipo**: Diferencia entre clientes Wallet (W), Fintech (F) e Comum (C) para retornar URLs parametrizadas específicas
3. **Gestão de Correspondência TED**: Controla o ciclo de vida de correspondências TED com status (N-não correspondido, C-correspondido, R-rejeitado)
4. **Validação de Intervalo de Datas**: Garante que filtros de busca paginada tenham data inicial e final válidas
5. **Rejeição em Lote**: Permite rejeitar múltiplas TEDs simultaneamente, validando que estejam no status "Não Correspondido"
6. **URLs Parametrizadas por Liquidação**: Retorna URLs de callback, notificação e retorno específicas baseadas no tipo de cliente e código de liquidação
7. **Validação de CNPJ**: Compara CNPJ do parâmetro com CNPJ do resultado para garantir consistência
8. **Controle de Migração**: Verifica status de migração de participantes para operações de estorno
9. **Paginação de Resultados**: Implementa busca paginada com cálculo automático de total de páginas

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Fintech**: Representa uma fintech parceira com CNPJ, nome, contas CP1/CP2 e URLs de integração
- **Cliente**: Entidade base para clientes com tipo de integração, banco liquidante e URLs parametrizadas
- **UnifiedClienteFintech**: Extensão de Cliente com informações completas de fintech, usuário e contas
- **Correspondente**: Representa correspondente bancário com código, conta e CNPJ
- **CorrespondenciaTed**: Representa uma correspondência de TED com favorecido, remetente, valor e status
- **UrlsParametrizados**: Agrupa URLs de callback, retorno de solicitação e recebimento

**Relacionamentos:**
- Cliente possui relação com UrlsParametrizados (1:N baseado em liquidação)
- UnifiedClienteFintech herda de Cliente e adiciona informações de conta e usuário
- CorrespondenciaTed possui relacionamento com Correspondente através de numeroConta
- Fintech possui relacionamento com contas de pagamento (CP1, CP2)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Cadastro de fintechs com parâmetros de pagamento |
| TbValidacaoOrigemPagamento | tabela | SELECT | URLs de validação e retorno por origem de pagamento |
| TbContaPagamentoFintech | tabela | SELECT | Contas de pagamento das fintechs (CP1, CW) |
| TbContaUsuarioFintech | tabela | SELECT | Contas de usuários vinculadas às fintechs |
| TbUsuarioContaFintech | tabela | SELECT | Usuários das fintechs |
| TbRelacaoContaUsuarioFintech | tabela | SELECT | Relacionamento entre contas e usuários |
| TbOrigemPagamentoMultiplaConta | tabela | SELECT | Origens de pagamento para múltiplas contas (Wallet) |
| TbRelacaoLiquidacaoGrupo | tabela | SELECT | Relacionamento entre liquidação e grupos |
| TbCorrespondenteBancario | tabela | SELECT | Cadastro de correspondentes bancários |
| TbContaCorrespondenteBancario | tabela | SELECT | Contas dos correspondentes bancários |
| TbCorrespondenciaTED | tabela | SELECT | Correspondências de TED registradas |
| TbControleMigracaoParticipante | tabela | SELECT | Controle de status de migração de participantes |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCorrespondenciaTED | tabela | INSERT | Inserção de novas correspondências de TED |
| TbCorrespondenciaTED | tabela | UPDATE | Atualização de correspondências TED (status, dados do remetente, histórico) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Configurações da aplicação por ambiente |
| application-local.yml | leitura | Spring Boot | Configurações específicas do ambiente local |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| sboot-spag-base-atom-parcerias.yml | leitura | Swagger Codegen | Especificação OpenAPI para geração de interfaces |
| *.sql | leitura | JDBI/RepositoryImpl | Queries SQL para operações de banco de dados |

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
| Microsoft SQL Server (DBSPAG) | Banco de Dados | Banco de dados principal contendo informações de parcerias, fintechs e correspondências |
| OAuth2 JWT Provider | Autenticação | Serviço de autenticação OAuth2 para validação de tokens JWT (URLs variam por ambiente) |
| Prometheus | Monitoramento | Exportação de métricas da aplicação |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo padrões hexagonais (ports/adapters)
- Separação clara entre camadas (presentation, domain, infrastructure)
- Uso adequado de frameworks modernos (Spring Boot, JDBI, MapStruct)
- Boa cobertura de testes unitários
- Documentação OpenAPI/Swagger bem definida
- Tratamento centralizado de exceções
- Uso de Lombok para redução de boilerplate
- Implementação de segurança com OAuth2

**Pontos de Melhoria:**
- Algumas classes de serviço com múltiplas responsabilidades (FintechService com lógica complexa)
- Queries SQL embutidas em arquivos separados (boa prática), mas algumas queries muito complexas poderiam ser otimizadas
- Falta de documentação JavaDoc em algumas classes críticas
- Alguns métodos com muitos parâmetros (ex: getUrlsParametrizados)
- Validações de negócio misturadas com lógica de serviço em alguns pontos
- Uso de strings literais para tipos de cliente ("W", "F", "C") poderia ser substituído por enums
- Alguns testes poderiam ter melhor nomenclatura e organização

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está dividido em três módulos Maven (application, domain, common), facilitando manutenção e evolução
2. **Multi-ambiente**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
3. **Segurança**: Implementa autenticação OAuth2 com JWT, com endpoints públicos configuráveis
4. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim
5. **Containerização**: Dockerfile preparado para deploy em containers
6. **CI/CD**: Estrutura preparada para pipeline Jenkins (jenkins.properties)
7. **Infraestrutura como Código**: Arquivo infra.yml com configurações de deployment Kubernetes
8. **Sanitização de Logs**: Implementa SecureLogUtil para prevenir log injection
9. **Paginação**: Sistema de paginação implementado com cálculo automático de páginas
10. **Versionamento de API**: Endpoints versionados (v1) permitindo evolução da API
11. **Testes Organizados**: Estrutura de testes separada por tipo (unit, integration, functional)
12. **Validação Arquitetural**: Profile Maven para validação de regras arquiteturais com ArchUnit