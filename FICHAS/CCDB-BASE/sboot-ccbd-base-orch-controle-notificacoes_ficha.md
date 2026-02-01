## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço stateless de controle de notificações, responsável por enviar notificações de push preditivo para boletos agendados para o próximo dia útil. Ele também pode ser utilizado para o controle de outras notificações.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ControleNotificacoesController**: Controlador REST que expõe endpoints para consulta e envio de notificações.
- **ControleNotificacoesService**: Serviço de domínio que orquestra o envio de notificações.
- **ControleNotificacoesRepositoryImpl**: Implementação do repositório que interage com APIs externas para consulta e atualização de agendamentos.
- **ControleNotificacoesMapper**: Mapper responsável por converter objetos de representação em objetos de domínio.
- **DataUtils**: Utilitário para manipulação de datas, como busca do próximo dia útil.
- **CamelContextWrapper**: Wrapper para o contexto Camel, gerenciando rotas de integração.
- **ControleNotificacoesRouter**: Define rotas Camel para orquestração de notificações.

### 3. Tecnologias Utilizadas
- Spring Boot
- Apache Camel
- Swagger
- Prometheus
- Grafana
- Docker
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/notificacoes/consumo-tributo | ControleNotificacoesController | Busca boletos agendados de Consumo/Tributo, trata e envia os dados para Orch Envio de Push. |

### 5. Principais Regras de Negócio
- Envio de notificações de push para boletos agendados para o próximo dia útil.
- Atualização de status de agendamentos após envio de notificações.
- Consulta de agendamentos de consumo e tributo via API externa.

### 6. Relação entre Entidades
- **AgendamentoDomainResponse**: Representa a resposta de um agendamento, incluindo detalhes como código de agendamento, valor, e remetente.
- **PessoaAgendamento**: Representa uma pessoa envolvida no agendamento, com informações como nome, CPF/CNPJ, e conta bancária.
- **ControleNotificacoes**: Entidade de domínio que encapsula o resultado do processamento de notificações.
- **AgendamentoPushInfo**: Informações necessárias para o envio de notificações de push, como CPF/CNPJ e valor total agendado.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **AtualizarAgendamentoApi**: API para atualizar agendamentos.
- **ConsultaAgendamentosConsumoTributoApi**: API para consultar agendamentos de consumo e tributo.
- **EnvioPushOrchApi**: API para enviar notificações de push personalizadas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, utilizando boas práticas de programação como injeção de dependências e uso de mapeadores. A documentação está presente, e o uso de tecnologias como Swagger facilita a exposição de APIs. No entanto, poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza o framework Apache Camel para orquestração de rotas, o que facilita a integração com serviços externos.
- A configuração de segurança é habilitada através do Spring Security OAuth2.
- O projeto está configurado para diferentes ambientes (local, des, qa, uat, prd) através de perfis Spring.