## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microserviço atômico desenvolvido em Java com Spring Boot, responsável por gerenciar transações de conta corrente quando o sistema principal está indisponível. Ele utiliza RabbitMQ para filas de mensagens e se integra com um banco de dados SQL Server para operações de leitura e escrita.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ContaCorrenteStdinController**: Controlador REST que gerencia endpoints relacionados a transações de conta corrente.
- **ContaCorrenteStdinService**: Serviço que contém a lógica de negócios para efetivar transações de crédito, débito e TEF (Transferência Eletrônica de Fundos).
- **TransactionalContaCorrenteStdinService**: Extensão do serviço principal que adiciona suporte a transações.
- **ContaCorrenteStdinRepositoryImpl**: Implementação do repositório que interage com o banco de dados para operações de conta corrente.
- **ProcessaContaCorrenteStdinRepositoryImpl**: Implementação do repositório que interage com RabbitMQ para enviar transações para processamento.
- **BloqueioSimplificadoMapper**: Mapper para converter resultados de consultas SQL em objetos de domínio.
- **TransacaoMapper**: Mapper para converter objetos de domínio em transações para persistência.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- SQL Server
- Swagger
- JDBI
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/banco-digital/contas/transacao | ContaCorrenteStdinController | Verifica se existe transação pendente no stand-in |
| PUT    | /v1/banco-digital/contas/transacao/circuitbreaker | ContaCorrenteStdinController | Executa o circuit breaker para transações |
| PUT    | /v1/banco-digital/contas/transacao/conta/circuitbreaker | ContaCorrenteStdinController | Executa o circuit breaker para uma conta específica |
| PUT    | /v1/banco-digital/contas/transacao/post-fila | ContaCorrenteStdinController | Envia operações ativas para a fila |
| PUT    | /v1/banco-digital/contas/transacao/inativar | ContaCorrenteStdinController | Inativa uma transação no stand-in |
| GET    | /v1/banco-digital/contas | ContaCorrenteStdinController | Consulta informações da conta |
| POST   | /v1/banco-digital/contas/validacao | ContaCorrenteStdinController | Valida a situação da conta |
| POST   | /v1/banco-digital/contas/credito | ContaCorrenteStdinController | Efetiva crédito |
| POST   | /v1/banco-digital/contas/tef | ContaCorrenteStdinController | Efetiva TEF |
| POST   | /v1/banco-digital/contas/debito | ContaCorrenteStdinController | Solicita débito |
| POST   | /v1/banco-digital/contas/debito/confirmar | ContaCorrenteStdinController | Efetiva débito |
| POST   | /v1/banco-digital/contas/bloqueio/cancelar | ContaCorrenteStdinController | Cancela bloqueio |
| GET    | /v1/banco-digital/contas/transacao/conta/consultar-bloqueios-standin/{cdAgencia}/{cdBanco}/{cdSequenciaBloqueioSaldo}/{cdMotivoBloqueio} | ContaCorrenteStdinController | Consulta bloqueios StandIn |

### 5. Principais Regras de Negócio
- Verificação de transações pendentes no stand-in.
- Efetivação de crédito e débito com validação de saldo e bloqueios.
- Implementação de circuit breaker para transações e contas.
- Cancelamento de bloqueios de saldo.
- Envio de transações para processamento via RabbitMQ.

### 6. Relação entre Entidades
- **ContaCorrenteSimplificado**: Representa uma conta corrente simplificada com atributos como saldo total, saldo disponível, saldo bloqueado, etc.
- **Transacao**: Representa uma transação financeira com atributos como código do banco, agência, conta, tipo de transação, etc.
- **BloqueioSimplificado**: Representa um bloqueio simplificado com atributos como sequência de bloqueio e valor da operação.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEfetivacaoCashStandIn     | tabela | SELECT | Armazena transações de efetivação de cash stand-in |
| TbConta                     | tabela | SELECT | Armazena informações de contas correntes |
| TbCotroleBloqueioConta      | tabela | SELECT | Armazena controle de bloqueios de conta |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbEfetivacaoCashStandIn     | tabela | INSERT, UPDATE, DELETE | Armazena transações de efetivação de cash stand-in |
| TbCotroleBloqueioConta      | tabela | UPDATE, INSERT | Armazena controle de bloqueios de conta |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **sample-queue**: Fila para envio de transações para processamento.

### 11. Integrações Externas
- RabbitMQ para gerenciamento de filas de mensagens.
- SQL Server para persistência de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de mappers para conversão de dados. A documentação é clara e os testes são abrangentes. No entanto, poderia haver uma melhor organização dos pacotes e classes para facilitar a manutenção.

### 13. Observações Relevantes
O sistema utiliza OAuth2 para autenticação e possui endpoints expostos via Swagger para facilitar o acesso à documentação das APIs. Além disso, o uso de RabbitMQ permite que o sistema seja escalável e robusto em relação ao processamento de mensagens assíncronas.