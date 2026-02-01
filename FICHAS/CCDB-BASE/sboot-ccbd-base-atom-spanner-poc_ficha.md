```markdown
## Ficha Técnica do Sistema

### 1. Descrição Geral
Este sistema é uma prova de conceito (PoC) para a utilização do Google Spanner, com o objetivo de migrar serviços atualmente utilizados no Sybase para o banco Google Spanner. O sistema busca ser altamente escalável, consistente, performático e flexível, além de oferecer suporte robusto e documentação para auxílio em troubleshootings.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ContaController**: Controlador REST responsável por gerenciar requisições relacionadas à efetivação de transações financeiras.
- **EfetivarTefService**: Serviço responsável por efetivar transações financeiras entre contas, incluindo validações e atualizações de saldo.
- **CriticasService**: Serviço que realiza validações e críticas sobre as transações e contas envolvidas.
- **ContaCorrenteRepository**: Repositório para operações de persistência relacionadas à entidade ContaEntity.
- **MovimentoMapper**: Mapper para converter objetos de dados de efetivação em entidades de movimento.
- **PubSubProperties**: Classe de configuração para propriedades do Google Pub/Sub.

### 3. Tecnologias Utilizadas
- Spring Boot
- Google Cloud Spanner
- Google Cloud Pub/Sub
- Maven
- Lombok
- Swagger/OpenAPI

### 4. Principais Endpoints REST
| Método | Endpoint                                   | Classe Controladora | Descrição                        |
|--------|--------------------------------------------|---------------------|----------------------------------|
| POST   | /v1/banco-digital/conta/efetivarTef        | ContaController     | Efetiva uma transação financeira |

### 5. Principais Regras de Negócio
- Validação de contas e transações antes da efetivação.
- Atualização de saldos e histórico de transações após a efetivação.
- Publicação de eventos para monitoramento de bloqueios de crédito.
- Tratamento de exceções específicas para operações de conta corrente.

### 6. Relação entre Entidades
- **ContaEntity**: Representa uma conta corrente, com atributos como saldo, agência, tipo de conta, etc.
- **MovimentoDiaEntity**: Representa um movimento diário de uma conta.
- **HistoricoSaldoEntity**: Representa o histórico de saldo de uma conta.
- **TransacaoEntity**: Representa uma transação financeira.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo     | Operação | Breve Descrição                          |
|-----------------------------|----------|----------|------------------------------------------|
| TbConta                     | tabela   | SELECT   | Armazena informações sobre contas correntes |
| TbMovimentoDia              | tabela   | SELECT   | Armazena informações sobre movimentos diários |
| TbHistoricoSaldo            | tabela   | SELECT   | Armazena histórico de saldo das contas   |
| TbTransacao                 | tabela   | SELECT   | Armazena informações sobre transações    |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo     | Operação          | Breve Descrição                          |
|-----------------------------|----------|-------------------|------------------------------------------|
| TbConta                     | tabela   | UPDATE            | Atualiza informações de saldo e movimento |
| TbMovimentoDia              | tabela   | INSERT/UPDATE     | Insere e atualiza movimentos diários     |
| TbHistoricoSaldo            | tabela   | UPDATE            | Atualiza histórico de saldo              |
| TbSaldoBloqueado            | tabela   | UPDATE            | Atualiza informações de bloqueio de saldo |

### 9. Filas Lidas
- Não se aplica

### 10. Filas Geradas
- **bloqueiosMonitoradosOutputChannel**: Canal de saída para publicação de bloqueios monitorados.
- **transactionsOutputChannel**: Canal de saída para publicação de transações efetivadas.

### 11. Integrações Externas
- Integração com Google Cloud Pub/Sub para publicação de eventos.
- Integração com Google Cloud Spanner para operações de banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utiliza boas práticas de programação e está bem organizado. A utilização de frameworks como Spring Boot e Lombok facilita a legibilidade e manutenção. No entanto, algumas classes de teste estão vazias, o que pode impactar na cobertura de testes.

### 13. Observações Relevantes
- O sistema utiliza o Google Spanner como banco de dados, que é uma solução de banco de dados altamente escalável e consistente.
- A documentação do Swagger está integrada, permitindo fácil acesso aos endpoints expostos.
- O sistema está configurado para rodar em ambientes de desenvolvimento, homologação e produção, conforme especificado no arquivo `infra.yml`.

---
```