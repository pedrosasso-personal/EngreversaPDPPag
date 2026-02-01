# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spag-base-atom-regras-rebate** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por gerenciar as regras e parametrizações de rebate (bonificações/descontos) do Banco Votorantim. O sistema permite cadastrar, alterar, consultar e excluir parametrizações de rebate tanto para produtos (serviços) quanto para clientes específicos, incluindo faixas de valores/quantidades, contas de apuração, periodicidade de pagamento e demais configurações relacionadas ao cálculo e pagamento de rebates.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **ParametrizacaoClienteController** | Controlador REST para gerenciar parametrizações de rebate por cliente |
| **ParametrizacaoProdutoController** | Controlador REST para gerenciar parametrizações de rebate por produto/serviço |
| **ServicoController** | Controlador REST para gerenciar os serviços/produtos de rebate |
| **FaixaParametrizacaoClienteController** | Controlador REST para consultar faixas de parametrização de clientes |
| **HistoricoParametrizacaoClienteController** | Controlador REST para consultar histórico de alterações de parametrizações de clientes |
| **HistoricoParametrizacaoProdutoController** | Controlador REST para consultar histórico de alterações de parametrizações de produtos |
| **ParametrizacaoClienteService** | Serviço de negócio para parametrizações de clientes |
| **ParametrizacaoProdutoService** | Serviço de negócio para parametrizações de produtos |
| **ServicoService** | Serviço de negócio para gerenciar serviços/produtos |
| **FaixaParametrizacaoClienteService** | Serviço de negócio para faixas de parametrização de clientes |
| **FaixaParametrizacaoProdutoService** | Serviço de negócio para faixas de parametrização de produtos |
| **ClienteService** | Serviço de negócio para gerenciar clientes |
| **ContaApuracaoService** | Serviço de negócio para gerenciar contas de apuração |
| **HistoricoParametrizacaoClienteService** | Serviço de negócio para histórico de parametrizações de clientes |
| **HistoricoParametrizacaoProdutoService** | Serviço de negócio para histórico de parametrizações de produtos |
| **JdbiConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **RegrasRebateConfiguration** | Configuração dos beans de serviço da aplicação |
| **RestResponseEntityExceptionHandler** | Tratamento centralizado de exceções REST |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot** (framework principal)
- **JDBI 3.9.1** (biblioteca para acesso a banco de dados)
- **SQL Server** (banco de dados Microsoft SQL Server)
- **Maven** (gerenciamento de dependências e build)
- **Lombok** (redução de código boilerplate)
- **Swagger/OpenAPI 2.9.2** (documentação de APIs)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer/Prometheus** (métricas e observabilidade)
- **JUnit 5 + Mockito** (testes unitários)
- **Pact** (testes de contrato)
- **Docker** (containerização)
- **OpenShift/Kubernetes** (orquestração)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/produtos` | ServicoController | Lista todos os serviços/produtos de rebate |
| GET | `/produtos/{id}` | ServicoController | Busca produto por ID |
| GET | `/produtos/nome?nome={nome}` | ServicoController | Busca produtos por nome |
| POST | `/produtos` | ServicoController | Cadastra novo serviço/produto |
| PATCH | `/produtos/{id}` | ServicoController | Altera serviço/produto |
| DELETE | `/produtos/{id}` | ServicoController | Exclui serviço/produto |
| GET | `/parametrizacao/produto/{id}` | ParametrizacaoProdutoController | Busca parametrização de produto por ID |
| GET | `/parametrizacao/produto/byIdServico/{id}` | ParametrizacaoProdutoController | Busca parametrização por ID do serviço |
| POST | `/parametrizacao/produto` | ParametrizacaoProdutoController | Cadastra parametrização de produto |
| PUT | `/parametrizacao/produto/{id}` | ParametrizacaoProdutoController | Altera parametrização de produto |
| DELETE | `/parametrizacao/produto/{id}` | ParametrizacaoProdutoController | Exclui parametrização de produto |
| GET | `/parametrizacao/cliente/periodicidade/{periodicidade}` | ParametrizacaoClienteController | Lista parametrizações por periodicidade |
| GET | `/parametrizacao/cliente/{id}` | ParametrizacaoClienteController | Busca parametrização de cliente por ID |
| GET | `/parametrizacao/cliente/byCpfCnpjAndIdServico/{cpfCnpj}/{idServico}` | ParametrizacaoClienteController | Busca parametrização por CPF/CNPJ e serviço |
| POST | `/parametrizacao/cliente` | ParametrizacaoClienteController | Cadastra parametrização de cliente |
| PATCH | `/parametrizacao/cliente/{id}` | ParametrizacaoClienteController | Altera parametrização de cliente |
| DELETE | `/parametrizacao/cliente/{id}` | ParametrizacaoClienteController | Exclui parametrização de cliente |
| GET | `/parametrizacao/faixas/cliente/{id}` | FaixaParametrizacaoClienteController | Busca faixa de parametrização por ID |
| GET | `/historico/faixas/cliente/{id}?data={data}` | HistoricoFaixaParametrizacaoClienteController | Busca faixa histórica por ID e data |
| GET | `/historico/faixas/cliente/todas/{idParametrizacao}?data={data}` | HistoricoFaixaParametrizacaoClienteController | Busca todas faixas históricas por parametrização e data |
| GET | `/historico/parametrizacao/cliente/{idParametrizacao}` | HistoricoParametrizacaoClienteController | Lista histórico de alterações de parametrização de cliente |
| GET | `/historico/parametrizacao/produto/{idParametrizacao}` | HistoricoParametrizacaoProdutoController | Lista histórico de alterações de parametrização de produto |

---

## 5. Principais Regras de Negócio

- **Cadastro de Serviços**: Não permite cadastrar serviços com siglas duplicadas
- **Exclusão de Serviços**: Não permite excluir serviços que possuam parametrizações ativas (cliente ou produto)
- **Cadastro de Parametrização de Produto**: Valida existência do serviço antes de criar parametrização
- **Cadastro de Parametrização de Cliente**: Valida existência do serviço e cadastra cliente se não existir
- **Exclusão de Parametrização de Produto**: Não permite excluir se existirem parametrizações de cliente vinculadas ao produto
- **Alteração de Parametrizações**: Permite adicionar, alterar e excluir faixas e contas de apuração de forma incremental
- **Histórico de Alterações**: Registra todas as alterações (inclusão, alteração, exclusão) em tabelas de log/histórico
- **Reativação de Contas**: Ao adicionar uma conta já existente mas inativa, o sistema a reativa ao invés de criar duplicata
- **Validação de Usuário**: Exige login de usuário válido para operações de alteração e exclusão
- **Status de Parametrizações**: Controla status (ATIVO, SUSPENSO, EXCLUIDO) das parametrizações
- **Faixas de Rebate**: Suporta faixas por valor ou quantidade, com percentual ou valor fixo de rebate
- **Apuração**: Suporta diferentes formas de apuração (por cliente ou por contas) e tipos (bancária, periodicidade)

---

## 6. Relação entre Entidades

**Principais entidades e relacionamentos:**

- **Servico** (1) ← (N) **ParametrizacaoProduto**: Um serviço pode ter uma parametrização de produto
- **Servico** (1) ← (N) **ParametrizacaoCliente**: Um serviço pode ter várias parametrizações de clientes
- **Cliente** (1) ← (N) **ParametrizacaoCliente**: Um cliente pode ter várias parametrizações (uma por serviço)
- **ParametrizacaoProduto** (1) ← (N) **FaixaParametrizacaoProduto**: Uma parametrização de produto possui várias faixas
- **ParametrizacaoCliente** (1) ← (N) **FaixaParametrizacaoCliente**: Uma parametrização de cliente possui várias faixas
- **ParametrizacaoCliente** (1) ← (N) **ContaApuracao**: Uma parametrização de cliente pode ter várias contas de apuração
- **ParametrizacaoCliente** (1) ← (N) **HistoricoParametrizacaoCliente**: Histórico de alterações da parametrização
- **ParametrizacaoProduto** (1) ← (N) **HistoricoParametrizacaoProduto**: Histórico de alterações da parametrização

**Enumerações importantes:**
- Status, Periodicidade, FormaRebate, TipoApuracao, TipoEntrada, ApuracaoBancaria, ContagemPrazo, TipoConta, Flag, FormaApuracao, TipoAlteracao

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbServicoRebate | tabela | SELECT | Consulta serviços/produtos de rebate |
| TbClienteRebate | tabela | SELECT | Consulta clientes cadastrados |
| TbParametroServico | tabela | SELECT | Consulta parametrizações de produtos |
| TbParametroCliente | tabela | SELECT | Consulta parametrizações de clientes |
| TbParametroFaixaServico | tabela | SELECT | Consulta faixas de parametrização de produtos |
| TbParametroFaixaCliente | tabela | SELECT | Consulta faixas de parametrização de clientes |
| TbContaApuracaoCliente | tabela | SELECT | Consulta contas de apuração de clientes |
| TbRegistroParametroServico | tabela | SELECT | Consulta registros de alteração de parametrização de produto |
| TbRegistroParametroCliente | tabela | SELECT | Consulta registros de alteração de parametrização de cliente |
| TbLogParametroServico | tabela | SELECT | Consulta logs históricos de parametrização de produto |
| TbLogParametroCliente | tabela | SELECT | Consulta logs históricos de parametrização de cliente |
| TbLogParametroFaixaServico | tabela | SELECT | Consulta logs históricos de faixas de produto |
| TbLogParametroFaixaCliente | tabela | SELECT | Consulta logs históricos de faixas de cliente |
| TbLogContaApuracaoCliente | tabela | SELECT | Consulta logs históricos de contas de apuração |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbServicoRebate | tabela | INSERT | Insere novos serviços/produtos de rebate |
| TbServicoRebate | tabela | UPDATE | Atualiza serviços/produtos (nome, descrição, exclusão lógica) |
| TbClienteRebate | tabela | INSERT | Insere novos clientes |
| TbParametroServico | tabela | INSERT | Insere novas parametrizações de produtos |
| TbParametroServico | tabela | UPDATE | Atualiza parametrizações de produtos |
| TbParametroCliente | tabela | INSERT | Insere novas parametrizações de clientes |
| TbParametroCliente | tabela | UPDATE | Atualiza parametrizações de clientes |
| TbParametroFaixaServico | tabela | INSERT | Insere faixas de parametrização de produtos |
| TbParametroFaixaServico | tabela | UPDATE | Atualiza faixas de parametrização de produtos |
| TbParametroFaixaCliente | tabela | INSERT | Insere faixas de parametrização de clientes |
| TbParametroFaixaCliente | tabela | UPDATE | Atualiza faixas de parametrização de clientes |
| TbContaApuracaoCliente | tabela | INSERT | Insere contas de apuração |
| TbContaApuracaoCliente | tabela | UPDATE | Atualiza contas de apuração (ativação/desativação) |
| TbRegistroParametroServico | tabela | INSERT | Registra alterações em parametrizações de produto |
| TbRegistroParametroCliente | tabela | INSERT | Registra alterações em parametrizações de cliente |
| TbLogParametroServico | tabela | INSERT | Insere logs de histórico de parametrização de produto |
| TbLogParametroCliente | tabela | INSERT | Insere logs de histórico de parametrização de cliente |
| TbLogParametroFaixaServico | tabela | INSERT | Insere logs de histórico de faixas de produto |
| TbLogParametroFaixaCliente | tabela | INSERT | Insere logs de histórico de faixas de cliente |
| TbLogContaApuracaoCliente | tabela | INSERT | Insere logs de histórico de contas de apuração |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação (datasource, profiles, etc) |
| logback-spring.xml | leitura | Logback | Configuração de logs da aplicação |
| *.sql (resources) | leitura | JDBI Repositories | Arquivos SQL para queries do JDBI |

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
| SQL Server (DBSPAG2) | Banco de Dados | Banco de dados principal contendo todas as tabelas de parametrização de rebate (schema: spagRegraRebate) |
| API Gateway OAuth2 | Autenticação | Validação de tokens JWT via JWK (diferentes URLs por ambiente: des, qa, uat, prd) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrões hexagonais (ports/adapters) com separação clara entre domain, application e common
- Uso adequado de padrões de projeto (Repository, Service, Mapper, DTO)
- Boa cobertura de testes unitários e estrutura de testes bem organizada
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Implementação de histórico/auditoria de alterações
- Tratamento centralizado de exceções
- Uso de JDBI com SQL externalizado facilitando manutenção
- Documentação via Swagger/OpenAPI
- Fixtures para testes bem estruturados

**Pontos de Melhoria:**
- Alguns métodos de serviço são extensos e poderiam ser refatorados
- Falta validação de entrada em alguns endpoints (uso de @Valid em apenas um endpoint)
- Algumas classes de mapper possuem métodos estáticos que dificultam testes
- Código comentado em alguns arquivos (ex: logback-spring.xml)
- Falta documentação JavaDoc em classes e métodos
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "lista", "result")
- Transações gerenciadas por classes wrapper específicas (TransationalParametrizacaoClienteService) ao invés de anotações diretas nos serviços

---

## 14. Observações Relevantes

- O sistema utiliza **exclusão lógica** (flag FlAtivo = 'N') ao invés de exclusão física dos registros
- Todas as operações de alteração geram **registros de auditoria** em tabelas de log e histórico
- O sistema suporta **retroatividade** de parametrizações através de flags específicas
- Há suporte para **múltiplos ambientes** (local, des, qa, uat, prd) com configurações específicas
- O sistema implementa **versionamento de parametrizações** através de timestamps de alteração
- Utiliza **pool de conexões Hikari** com configurações específicas por ambiente
- Implementa **soft delete** para contas de apuração, permitindo reativação
- O schema do banco é **spagRegraRebate** (ou sPagRegraRebate em algumas queries)
- Sistema preparado para **containerização** com Dockerfile e configurações Kubernetes/OpenShift
- Métricas expostas via **Prometheus** na porta 9090
- API principal exposta na porta **8080**
- Utiliza **OAuth2 com JWT** para autenticação/autorização