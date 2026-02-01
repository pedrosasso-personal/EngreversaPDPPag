## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de callback para parceiros, desenvolvido para gerenciar a confirmação de pagamentos e integração com sistemas parceiros. Ele utiliza o framework Spring Boot e RabbitMQ para mensageria, além de integrar com APIs externas para realizar operações de pagamento e controle de retorno.

### 2. Principais Classes e Responsabilidades
- `Application`: Classe principal para inicialização do aplicativo Spring Boot.
- `MainService`: Serviço principal que gerencia o processamento de retorno de parceiros e notificação de callbacks.
- `CallbackParceirosController`: Controlador REST que expõe endpoints para operações de callback.
- `CallbackParceiroConfiguration`: Configuração de beans e integração com Camel para roteamento de mensagens.
- `RabbitMQConfiguration`: Configuração de conexão e templates para RabbitMQ.
- `BoletoRepositoryImpl`, `CallbackParceiroRepositoryImpl`, `PagamentoRepositoryImpl`, `ParceriaRepositoryImpl`, `RetornoSolicitacaoRepositoryImpl`, `TransferenciaRepositoryImpl`, `TributosRepositoryImpl`: Implementações de repositórios para operações de integração com serviços externos.
- `CallbackQueueParceiroImpl`: Implementação de fila para envio de mensagens via RabbitMQ.
- `FeatureToggleUtils`: Utilitário para gerenciar feature toggles usando ConfigCat.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- RabbitMQ
- Apache Camel
- Swagger
- Maven
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/callback-parceiro/ | CallbackParceirosController | Confirmação de pagamento de parceiro. |
| POST   | /v1/callback-partner/ | CallbackParceirosController | Confirmação de pagamento de parceiro. |
| POST   | /v1/notificar-esteira/ | CallbackParceirosController | Notificação de esteira de callback. |

### 5. Principais Regras de Negócio
- Confirmação de pagamentos via callback para parceiros.
- Enriquecimento de dados de lançamento quando necessário.
- Retentativa de envio de mensagens em caso de falha.
- Integração com serviços externos para validação e confirmação de pagamentos.

### 6. Relação entre Entidades
- `CallbackParceiro`, `CallbackPartner`, `CallbackResponse`: Entidades de domínio para gerenciar dados de callback.
- `ControleRetorno`, `RetornoSolicitacao`, `RetornoSolicitacaoResponse`: Entidades para controle de retorno e solicitação.
- `Pagamento`, `Parceria`, `Participante`, `Remetente`: Entidades relacionadas a dados de pagamento e parceria.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- `CONFIRMA_PAGAMENTO_API_QUEUE`: Fila para confirmação de pagamento via API.
- `NOTIFICA_CALLBACK_ESTEIRA_QUEUE`: Fila para notificação de callback de esteira.

### 10. Filas Geradas
- `CONFIRMA_PAGAMENTO_API_WAITING_QUEUE`: Fila para mensagens em espera de confirmação de pagamento.
- `NOTIFICA_CALLBACK_ESTEIRA_WAITING_QUEUE`: Fila para mensagens em espera de notificação de callback de esteira.

### 11. Integrações Externas
- APIs de pagamento e controle de retorno.
- Serviço de autenticação OAuth.
- ConfigCat para feature toggles.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de interfaces para abstração. A documentação é clara e os testes estão bem organizados. No entanto, poderia haver uma melhor separação de responsabilidades em algumas classes.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para gerenciar fluxos alternativos de autenticação.
- A configuração de RabbitMQ é feita via arquivos de configuração externos.
- O projeto está configurado para ser executado em ambientes de desenvolvimento, QA, UAT e produção com variáveis de ambiente específicas.