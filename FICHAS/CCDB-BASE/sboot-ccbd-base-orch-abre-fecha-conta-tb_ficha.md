## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um microsserviço corporativo atômico responsável por executar procedimentos de encerramento de contas, importação de limites de crédito, sincronização de modalidades e outras operações relacionadas a contas correntes. Ele utiliza o Spring Boot para gerenciar suas operações e integrações com outros serviços.

### 2. Principais Classes e Responsabilidades
- **AbreFechaContaTbConfiguration**: Configurações gerais do sistema, incluindo beans para serviços e APIs.
- **ContaCorrenteFechaConfiguration**: Configurações específicas para a API de fechamento de conta corrente.
- **GlobalConfiguration**: Configurações para integração com o serviço global de conta.
- **RabbitMQConfiguration**: Configurações para integração com RabbitMQ.
- **AbreFechaContaTbRepositoryImpl**: Implementação do repositório para operações de abertura e fechamento de contas.
- **AbreFechaContaTbService**: Serviço para operações de abertura e fechamento de contas.
- **MovimentoService**: Serviço para gerenciar movimentos priorizados.
- **SincronizarService**: Serviço para sincronização de modalidades.
- **Application**: Classe principal para inicialização do Spring Boot.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- RabbitMQ
- Swagger
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/abre-fecha-conta-tb | AbreFechaContaTbController | Obtém informações de abertura e fechamento de conta. |
| POST   | /v1/limite/credito/importar | V1Controller | Importa limite de crédito. |
| POST   | /v1/contrato/agendado/importar | V1Controller | Importa contrato agendado. |
| POST   | /v1/modalidades/sincronizar | V1Controller | Sincroniza modalidades das contas. |

### 5. Principais Regras de Negócio
- Encerramento de contas baseado em análise de pendências financeiras.
- Importação de limites de crédito e contratos agendados.
- Sincronização de modalidades de contas correntes.
- Atualização de status de controle de encerramento de contas.

### 6. Relação entre Entidades
- **AbreFechaContaTb**: Entidade principal para abertura e fechamento de contas.
- **StatusConta**: Representa o status atual de uma conta, incluindo valores e bloqueios.
- **MovimentoPriorizadoDomain**: Representa um movimento priorizado na conta.
- **EncerramentoConta**: Detalhes sobre o processo de encerramento de uma conta.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica               |      |          |                 |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica               |      |          |                 |

### 9. Filas Lidas
- events.business.CCBD-BASE.consisteAberturaConta
- events.business.CCBD-BASE.consisteEncerramentoConta
- events.business.CCBD-BASE.gravarMovimento

### 10. Filas Geradas
Não se aplica

### 11. Integrações Externas
- APIs de conta corrente para consulta e atualização de informações.
- APIs de movimentações para gerenciar movimentos priorizados.
- APIs de sincronização de modalidades.
- RabbitMQ para processamento assíncrono de mensagens.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, utilizando boas práticas de programação e integração com Spring Boot e Apache Camel. A documentação é clara e os testes estão bem definidos, embora algumas áreas possam ser melhoradas em termos de cobertura de testes e tratamento de exceções.

### 13. Observações Relevantes
- O sistema utiliza Swagger para documentação de APIs, facilitando a integração e o entendimento dos endpoints disponíveis.
- A configuração do RabbitMQ é feita através de variáveis de ambiente, permitindo flexibilidade em diferentes ambientes de execução.