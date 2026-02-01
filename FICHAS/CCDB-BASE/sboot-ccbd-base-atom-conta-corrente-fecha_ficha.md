## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Conta Corrente Fecha" é um serviço atômico desenvolvido para gerenciar operações de fechamento de contas correntes, incluindo a atualização de faixas de contas, geração de arquivos de reprocessamento e integração com sistemas de mensageria e banco de dados. Ele utiliza o framework Spring Boot e é integrado com RabbitMQ para mensageria e JDBI para acesso ao banco de dados.

### 2. Principais Classes e Responsabilidades
- **ReprocessamentoServiceImpl**: Implementa a lógica de geração de arquivos M06 para reprocessamento de movimentos financeiros.
- **ContaCorrenteFechaConfiguration**: Configura os beans necessários para o funcionamento do sistema, incluindo repositórios e serviços.
- **DatabaseConfiguration**: Configura as conexões com os bancos de dados utilizando JDBI.
- **OpenApiConfiguration**: Configura o Swagger para documentação de APIs.
- **PubSubConfiguration**: Configura o canal de mensagens para integração com o Google Cloud Pub/Sub.
- **RabbitMQConfiguration**: Configura a conexão com o RabbitMQ.
- **CompensacaoStatusRepositoryImpl**: Implementa o repositório para obter o status de compensação.
- **ContaCorrenteFechaRepositoryImpl**: Implementa o repositório para operações de fechamento de contas correntes.
- **ListenerAtualizaFaixaConta**: Consome mensagens do RabbitMQ para atualizar faixas de contas.
- **ListenerFechamentoDoDia**: Consome mensagens do Pub/Sub para processar o fechamento diário de contas.
- **Application**: Classe principal para inicialização do Spring Boot.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- JDBI
- Swagger
- Google Cloud Pub/Sub
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/conta-corrente-fecha/atualizaFaixaConta | ContaCorrenteFechaController | Atualiza a faixa de contas. |
| POST   | /v1/conta-corrente-fecha/atualizaFaixaPosDesbloqueio | ContaCorrenteFechaController | Atualiza a faixa de contas após desbloqueio. |
| GET    | /v1/conta-corrente-fecha/downloadMontado | ContaCorrenteFechaController | Faz o download do arquivo M06. |
| GET    | /v1/conta-corrente-fecha/download | ContaCorrenteFechaController | Gera o arquivo M06. |
| POST   | /v1/conta-corrente-fecha/limite/credito/importar | ImportarController | Importa limite de crédito. |
| POST   | /v1/conta-corrente-fecha/contrato/agendado/importar | ImportarController | Importa contrato agendado. |
| GET    | /v1/conta-corrente-fecha/sincronizacao/obter-data-inicial | SincronizarModalidadesController | Obtém data inicial. |
| GET    | /v1/conta-corrente-fecha/compensacoes-status/{cdAgencia} | CompensacoesStatusController | Obtém o status da compensação de uma agência. |

### 5. Principais Regras de Negócio
- Geração de arquivos M06 para reprocessamento de movimentos financeiros.
- Atualização de faixas de contas correntes com base em mensagens recebidas.
- Sincronização de modalidades de contas.
- Importação de limites de crédito e contratos agendados.
- Validação de fechamento diário de contas.

### 6. Relação entre Entidades
- **Conta**: Representa uma conta bancária com informações como banco, agência e tipo de conta.
- **Movimento**: Representa uma transação financeira realizada em uma conta.
- **Reprocessamento**: Representa o estado de reprocessamento de movimentos financeiros.
- **LimiteContaCorrente**: Representa os limites de crédito associados a uma conta corrente.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbHistoricoMovimento        | tabela | SELECT | Consulta movimentos históricos. |
| TbSaldoBloqueado            | tabela | SELECT | Consulta saldos bloqueados. |
| TbSaldoIndisponivel         | tabela | SELECT | Consulta saldos indisponíveis. |
| TbConta                     | tabela | SELECT | Consulta informações de contas. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbHistoricoSaldoBloqueado   | tabela | INSERT | Insere histórico de saldo bloqueado. |
| TbSaldoBloqueado            | tabela | DELETE | Remove saldos bloqueados. |
| TbSaldoIndisponivel         | tabela | DELETE | Remove saldos indisponíveis. |
| TbConta                     | tabela | UPDATE | Atualiza informações de contas. |

### 9. Filas Lidas
- RabbitMQ: "atualiza_conta_faixa", "atualiza_conta_faixa_pos_desbloqueio"
- Google Cloud Pub/Sub: Canal de mensagens para criação de saldo histórico.

### 10. Filas Geradas
- Não se aplica.

### 11. Integrações Externas
- Google Cloud Pub/Sub: Para integração de mensagens.
- RabbitMQ: Para mensageria interna.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para abstração. A documentação e os logs são adequados, facilitando a manutenção e entendimento do fluxo de execução. No entanto, poderia haver uma melhor organização dos pacotes e classes para aumentar a clareza.

### 13. Observações Relevantes
- O sistema utiliza Docker para facilitar a implantação e execução em ambientes de desenvolvimento e produção.
- A configuração de segurança e autenticação é realizada através de propriedades do Spring Boot e configurações de RabbitMQ.
- A documentação das APIs é gerada automaticamente através do Swagger.