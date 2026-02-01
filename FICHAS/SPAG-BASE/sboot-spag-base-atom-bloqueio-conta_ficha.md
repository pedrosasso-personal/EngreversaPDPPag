```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de bloqueio de contas por ordens judiciais, desenvolvido para gerenciar e processar informações relacionadas a bloqueios e desbloqueios de contas bancárias com base em ordens judiciais. Ele utiliza o Spring Boot para criar endpoints REST que permitem a inserção, atualização e consulta de ordens judiciais, além de gerar resumos de bloqueios e processamentos diários.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **BloqueioContaConfiguration**: Configuração de beans relacionados ao serviço de bloqueio de contas.
- **DBConfiguration**: Configuração de datasources para conexão com bancos de dados.
- **JdbiConfiguration**: Configuração do Jdbi para interação com o banco de dados.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **OrdemJudicialConfiguration**: Configuração de beans relacionados ao serviço de ordens judiciais.
- **BloqueioContaRepositoryImpl**: Implementação do repositório para operações de bloqueio de conta.
- **OrdemJudicialRepositoryImpl**: Implementação do repositório para operações de ordens judiciais.
- **OrdemJudicialController**: Controlador REST para gerenciar ordens judiciais.
- **BloqueioContaService**: Serviço de domínio para operações de bloqueio de conta.
- **OrdemJudicialService**: Serviço de domínio para operações de ordens judiciais.
- **StringHelper**: Utilitário para manipulação de strings.
- **UtilDate**: Utilitário para manipulação de datas.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- SQL Server
- Docker
- Prometheus
- Grafana

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/registros-sem-endereco | OrdemJudicialController | Consulta registros sem endereço. |
| PUT    | /v1/atualizar-ordem-judicial | OrdemJudicialController | Atualiza uma ordem judicial. |
| POST   | /v1/ordem-judicial | OrdemJudicialController | Insere uma nova ordem judicial. |
| GET    | /v1/ordem-judicial | OrdemJudicialController | Consulta ordens judiciais por data e documentos. |
| GET    | /v1/bloqueio-conta/resumo-bloqueio-dia | OrdemJudicialController | Obtém resumo de bloqueio por dia. |
| GET    | /v1/bloqueio-conta/resumo-erro-processamento-parceiro | OrdemJudicialController | Obtém resumo de erro de processamento por parceiro. |
| GET    | /v1/bloqueio-conta/resumo-ordens-naoTrabalhadas | OrdemJudicialController | Obtém resumo de ordens não trabalhadas. |

### 5. Principais Regras de Negócio
- Processamento de ordens judiciais para bloqueio e desbloqueio de contas.
- Verificação de protocolos processados.
- Resumo de bloqueios e processamentos diários.
- Inserção e atualização de ordens judiciais no banco de dados.

### 6. Relação entre Entidades
- **OrdemJudicial**: Entidade principal que representa uma ordem judicial.
- **AtualizarOrdemJudical**: Entidade para atualização de ordens judiciais.
- **ErroProcessamentoParceiro**: Entidade para erros de processamento por parceiro.
- **OrdemNaoTrabalhada**: Entidade para ordens judiciais não trabalhadas.
- **ResumoBloqueioDia**: Entidade para resumo de bloqueios por dia.
- **ResumoProcessamentoDia**: Entidade para resumo de processamentos por dia.
- **ResumoProcessamentoEBloqueioDia**: Entidade para resumo combinado de bloqueios e processamentos.
- **SolicitacaoRegistro**: Entidade para registros de solicitação.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSolicitacaoJuridico       | tabela | SELECT | Consulta de solicitações jurídicas. |
| TbProcessoJuridico          | tabela | SELECT | Consulta de processos jurídicos. |
| TbTipoSolicitacaoJuridico   | tabela | SELECT | Consulta de tipos de solicitações jurídicas. |
| TbContaUsuarioFintech       | tabela | SELECT | Consulta de contas de usuários fintech. |
| TbParametroPagamentoFintech | tabela | SELECT | Consulta de parâmetros de pagamento fintech. |
| TbUsuarioContaFintech       | tabela | SELECT | Consulta de usuários de contas fintech. |
| TbControleBloqueioConta     | tabela | SELECT | Consulta de controle de bloqueio de contas. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleBloqueioConta     | tabela | INSERT, UPDATE | Inserção e atualização de controle de bloqueio de contas. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com serviços de autenticação via OAuth2.
- Integração com Prometheus para métricas.
- Integração com Grafana para visualização de métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, com uso adequado de padrões de projeto e boas práticas de desenvolvimento. A documentação é clara e os serviços são bem definidos. No entanto, poderia haver uma melhor separação de responsabilidades em algumas classes e mais testes automatizados.

### 13. Observações Relevantes
- O sistema utiliza Docker para containerização e facilita a execução de serviços de monitoramento como Prometheus e Grafana.
- A configuração do Swagger permite fácil acesso à documentação das APIs.
- O sistema está preparado para diferentes ambientes de execução, como desenvolvimento, teste e produção.

--- 
```