## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "spag.base.consulta-boleto" é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Seu principal objetivo é realizar consultas de boletos na CIP (Centralizadora de Informações de Pagamentos) e gerenciar o cache dessas consultas. O sistema também integra funcionalidades de envio e recebimento de mensagens via JMS, além de operações de cache utilizando Redis.

### 2. Principais Classes e Responsabilidades
- **DocketConfiguration**: Configurações do Swagger para documentação da API.
- **JmsConfiguration**: Configurações para o uso de JMS (Java Message Service).
- **RedisConfiguration**: Configurações para o uso de Redis como cache.
- **FeatureToogleEnum**: Enumeração para controle de funcionalidades do sistema.
- **MessageQueueRepository**: Gerencia o envio e recebimento de mensagens em filas JMS.
- **ParametroPagamentoFintechRepository**: Realiza consultas no banco de dados para obter informações de parceiros.
- **BoletoController**: Controlador REST que gerencia as operações de consulta de boletos.
- **BoletoService**: Serviço que implementa a lógica de consulta de boletos e gerenciamento de cache.
- **ConfigCatService**: Serviço para gerenciar feature toggles relacionadas ao cache de boletos.
- **MessageService**: Serviço para envio e recebimento de mensagens via JMS.
- **RolloutService**: Serviço para gerenciar o rollout de funcionalidades de cache.
- **ParametroInvalidoException**: Exceção personalizada para parâmetros inválidos.
- **Util**: Classe utilitária com métodos auxiliares para o sistema.
- **Server**: Classe principal que inicia o aplicativo Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Spring Data Redis
- JMS (Java Message Service)
- Swagger
- Docker
- Gradle
- SQL Server
- Redis

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/boleto/{codigoBarra} | BoletoController | Realiza consulta de boleto na CIP. |
| GET    | /v1/boleto/enviaMensagem/{codigoBarra} | BoletoController | Envia mensagem para o SPB. |
| GET    | /v1/boleto/recebeMensagem/{id} | BoletoController | Recebe mensagem do SPB. |
| GET    | /v1/boleto/removerCacheBoleto/{codigoBarra} | BoletoController | Remove o cache de um boleto específico. |
| GET    | /v1/boleto/removerTodosCacheBoleto | BoletoController | Remove todos os caches de boletos. |

### 5. Principais Regras de Negócio
- Validação do código de barras do boleto (deve ter 44 caracteres numéricos).
- Implementação de cache para consultas de boletos.
- Rollout de funcionalidades de cache baseado em feature toggles.
- Integração com parceiros através de consultas de CNPJ no banco de dados.

### 6. Relação entre Entidades
Não se aplica.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroPagamentoFintech | tabela | SELECT | Consulta CNPJ do parceiro pelo apiKey. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
- QL.SPAG.ROTEADOR_CIP.RSP

### 10. Filas Geradas
- QR.SPAG.CONSULTA_BOLETO_CIP

### 11. Integrações Externas
- Integração com Redis para operações de cache.
- Integração com JMS para envio e recebimento de mensagens.
- Integração com SQL Server para consultas de dados de parceiros.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e separação de responsabilidades. A documentação via Swagger está presente, facilitando a compreensão dos endpoints. No entanto, poderia haver uma maior utilização de testes automatizados para garantir a qualidade e robustez do sistema.

### 13. Observações Relevantes
- O sistema utiliza feature toggles para gerenciar o rollout de funcionalidades de cache, permitindo ativar ou desativar funcionalidades de forma controlada.
- A configuração do sistema é feita através de arquivos YAML, permitindo fácil adaptação para diferentes ambientes (desenvolvimento, teste, produção).