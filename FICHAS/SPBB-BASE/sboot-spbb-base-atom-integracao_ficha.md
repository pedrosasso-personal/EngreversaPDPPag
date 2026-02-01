## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de integração desenvolvido em Java, utilizando o framework Spring Boot. Ele tem como objetivo facilitar a integração de mensagens SPB (Sistema de Pagamentos Brasileiro), realizando operações de validação, processamento e replicação de mensagens entre diferentes entidades financeiras.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **IntegracaoConfiguration**: Configuração de beans para serviços de integração.
- **JdbiConfiguration**: Configuração para o uso do Jdbi, uma biblioteca de mapeamento de objetos para SQL.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **IntegracaoLtrController**: Controlador REST para lidar com mensagens LTR.
- **ProcessarMensagemCoreController**: Controlador REST para processar mensagens do núcleo.
- **SPBLegadoController**: Controlador REST para validação de mensagens SPB legado.
- **SPBLegadoReplicaController**: Controlador REST para atualização de réplicas SPB legado.
- **IntegracaoLtrService**: Serviço para manipulação de mensagens LTR.
- **ProcessarMensagemCoreService**: Serviço para processamento de mensagens do núcleo.
- **ValidarMensagemService**: Serviço para validação de mensagens.
- **SPBLegadoService**: Serviço para manipulação de réplicas SPB legado.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Sybase
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/mensagensLTR0002 | IntegracaoLtrController | Insere mensagem LTR0002 |
| POST   | /v1/mensagensLTR0008 | IntegracaoLtrController | Insere mensagem LTR0008 |
| POST   | /v1/mensagensLTR0004 | IntegracaoLtrController | Insere mensagem LTR0004 |
| POST   | /processarMensagemCore | ProcessarMensagemCoreController | Processa mensagem do núcleo |
| POST   | /validar-mensagem | SPBLegadoController | Valida mensagem SPB legado |
| PUT    | /spb-legado/replica | SPBLegadoReplicaController | Atualiza réplica SPB legado |

### 5. Principais Regras de Negócio
- Validação de mensagens SPB com base em regras de negócio específicas.
- Processamento de mensagens do núcleo, incluindo atualização de saldo e tratamento de erros.
- Replicação de mensagens SPB para entidades financeiras.
- Verificação de saldo de reserva antes de processar transações.

### 6. Relação entre Entidades
- **MensagemLtr**: Representa uma mensagem LTR com atributos como CNPJ, ISPB, e valor de lançamento.
- **ProcessarMensagemDomain**: Contém informações para processamento de mensagens do núcleo.
- **ReplicacaoMensagemDomain**: Utilizado para replicação de mensagens entre entidades.
- **SaldoReserva**: Representa o saldo de reserva de uma conta.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_inst_instituicao         | tabela | SELECT   | Busca ID da instituição pelo CNPJ |
| tb_usua_usuario             | tabela | SELECT   | Busca ID do usuário pela sigla do sistema |
| tb_mvlr_movimento_LTR       | tabela | SELECT   | Busca número de controle IF pelo ID do movimento |
| tb_movi_movimento           | tabela | SELECT   | Consulta movimento por ISPB e header |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_movi_movimento           | tabela | UPDATE   | Atualiza status do movimento |
| tb_movi_movimento_stop_id   | tabela | UPDATE   | Atualiza registro de réplica de movimento |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com APIs de autenticação via OAuth2.
- Utilização de serviços de conversão de mensagens SPB.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para abstração. A documentação via Swagger é um ponto positivo. No entanto, a complexidade de algumas classes pode ser reduzida para melhorar a legibilidade e manutenção.

### 13. Observações Relevantes
- O sistema utiliza Sybase como banco de dados, o que pode exigir configurações específicas de conexão.
- A documentação do Swagger facilita o entendimento dos endpoints disponíveis.
- O uso de Feature Toggles permite flexibilidade na ativação de funcionalidades.