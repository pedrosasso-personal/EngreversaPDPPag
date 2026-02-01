## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço de portabilidade de salário, desenvolvido em Java utilizando o framework Spring Boot. Ele orquestra operações relacionadas a solicitações de portabilidade de salário, incluindo consulta de status, solicitação, cancelamento e envio de motivos de cancelamento. O sistema também integra com outros serviços para obter dados cadastrais e informações de instituições bancárias.

### 2. Principais Classes e Responsabilidades
- **ApplicationConfiguration**: Configura beans para APIs de integração com outros serviços.
- **AppProperties**: Define propriedades de configuração do aplicativo.
- **PortabilidadeController**: Controlador que gerencia endpoints relacionados à portabilidade.
- **PortabilidadeControllerV2**: Versão alternativa do controlador de portabilidade.
- **PortabilidadeServiceImpl**: Implementação do serviço de portabilidade, utilizando Camel para orquestração.
- **MDMDadosRazaoSocialServiceImpl**: Serviço para consulta de razão social utilizando Camel.
- **PortabilidadeRepositoryImpl**: Implementação do repositório de portabilidade, interagindo com APIs externas.
- **ConsultaGlobalRepositoryImpl**: Implementação do repositório para consultas globais de dados cadastrais.
- **ConsultaInstituicoesRepositoryImpl**: Implementação do repositório para consultas de instituições bancárias.
- **CamelContextWrapper**: Wrapper para o contexto Camel, gerenciando rotas e templates de produtor/consumidor.
- **Banco**: Enumeração que representa bancos com seus códigos e nomes.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Apache Camel
- Swagger
- Prometheus
- Grafana
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/portabilidade/consulta | PortabilidadeController | Consulta situação de portabilidade. |
| POST | /v1/portabilidade/solicitacao | PortabilidadeController | Solicita portabilidade de salário. |
| PUT | /v1/portabilidade/cancelamento | PortabilidadeController | Cancela solicitação de portabilidade. |
| GET | /v1/portabilidade/consultaClienteTedSalario | PortabilidadeController | Consulta TED de salário. |
| GET | /v2/portabilidade/consulta | PortabilidadeControllerV2 | Consulta situação de portabilidade (v2). |
| POST | /v2/portabilidade/solicitacao | PortabilidadeControllerV2 | Solicita portabilidade de salário (v2). |
| GET | /v2/portabilidade/{cnpj}/razao-social | PortabilidadeControllerV2 | Consulta razão social por CNPJ. |

### 5. Principais Regras de Negócio
- Validação de CNPJ para consultas de razão social.
- Verificação de status de portabilidade antes de permitir cancelamento.
- Integração com APIs externas para obter dados cadastrais e informações bancárias.
- Tratamento de erros específicos para operações de portabilidade.

### 6. Relação entre Entidades
- **PortabilidadeVO**: Entidade principal que representa uma solicitação de portabilidade, incluindo dados de banco, empregador e cliente.
- **MotivoCancelamentoDTO**: Representa os motivos de cancelamento de uma portabilidade.
- **StatusPortabilidadeDTO**: Representa o status atual de uma portabilidade.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **DiasUteisApi**: Consulta dias úteis bancários.
- **DadosCadastraisApi**: Consulta dados cadastrais de clientes.
- **InstituicoesApi**: Consulta instituições bancárias.
- **PortabilidadeSalarioApi**: Gerencia operações de portabilidade de salário.
- **ObterDadosCadastraisFullApi**: Obtém dados cadastrais completos de um CNPJ.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para abstração. A documentação é clara e os testes são abrangentes. No entanto, algumas áreas poderiam ser melhoradas em termos de simplificação e redução de complexidade.

### 13. Observações Relevantes
- O sistema utiliza Apache Camel para orquestração de rotas, facilitando a integração com múltiplos serviços.
- A configuração do sistema é gerenciada por arquivos YAML, permitindo fácil adaptação a diferentes ambientes.
- O uso de Docker e Kubernetes é indicado para implantação em ambientes de nuvem.