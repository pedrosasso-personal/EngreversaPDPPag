## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço stateless desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por orquestrar requisições relacionadas à manutenção de tabelas de domínio do banco digital, especificamente para operações de consulta de parâmetros MT940 cadastrados nas contas ativas do banco.

### 2. Principais Classes e Responsabilidades
- **Application.java**: Classe principal que inicia a aplicação Spring Boot.
- **TabelasController.java**: Controlador REST que expõe endpoints para consulta de parâmetros MT940.
- **AppProperties.java**: Classe de configuração que carrega propriedades específicas do serviço.
- **OpenApiConfiguration.java**: Configuração do Swagger para documentação de APIs.
- **TabelasConfiguration.java**: Configuração de beans e serviços utilizados na aplicação.
- **ComParamentrosException.java**: Classe de exceção personalizada para erros com parâmetros.
- **HttpException.java**: Classe de exceção para erros HTTP.
- **ResourceExceptionHandler.java**: Manipulador de exceções que retorna respostas apropriadas para erros HTTP.
- **ContasGlobalRepositoryImpl.java**: Implementação do repositório para consulta de contas globais.
- **ParametroMt940RepositoryImpl.java**: Implementação do repositório para consulta de parâmetros MT940.
- **ContaGlobalMapper.java**: Classe de mapeamento para transformar representações de contas globais.
- **ParametroMt940Mapper.java**: Classe de mapeamento para transformar representações de parâmetros MT940.
- **ParametroMt940Router.java**: Configuração de rotas Camel para processamento de parâmetros MT940.
- **CamelContextWrapper.java**: Wrapper para o contexto Camel, gerenciando rotas e templates de produtor/consumidor.
- **ContaGlobal.java**: Classe de domínio representando uma conta global.
- **ContaGlobalDTO.java**: Classe de domínio representando um DTO de conta global.
- **ParametroBanco.java**: Classe de domínio representando parâmetros de banco.
- **ParametroMt940.java**: Classe de domínio representando parâmetros MT940.
- **CodigoErroEnum.java**: Enumeração de códigos de erro utilizados no sistema.
- **ContasGlobalRepository.java**: Interface de repositório para contas globais.
- **ParametroMt940Repository.java**: Interface de repositório para parâmetros MT940.
- **ParametroMt940ServiceImpl.java**: Implementação do serviço para consulta de parâmetros MT940.
- **ParametroMt940Service.java**: Interface de serviço para consulta de parâmetros MT940.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Springfox Swagger
- Apache Camel
- Prometheus
- Grafana
- Docker
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/manutencao-tabela/parametro-mt940/{cpfcnpj} | TabelasController | Consulta de parâmetros MT940 cadastrados nas contas ativas do banco digital. |

### 5. Principais Regras de Negócio
- Consulta de parâmetros MT940 para contas ativas utilizando CPF/CNPJ.
- Manipulação de exceções específicas para erros de consulta e HTTP.

### 6. Relação entre Entidades
- **ContaGlobal**: Representa uma conta global com atributos como número da conta, tipo de conta e data de encerramento.
- **ContaGlobalDTO**: DTO que encapsula o CPF/CNPJ e uma lista de contas globais.
- **ParametroBanco**: Representa parâmetros de banco, incluindo código e periodicidades.
- **ParametroMt940**: Representa parâmetros MT940, incluindo banco, CPF/CNPJ, conta corrente, login e status.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com serviços de cliente para consulta de dados cadastrais.
- Integração com serviços de conta corrente para manutenção de parâmetros MT940.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências e separação de responsabilidades. A documentação via Swagger está presente, facilitando a compreensão dos endpoints disponíveis. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade.

### 13. Observações Relevantes
- O sistema utiliza o Prometheus e Grafana para monitoramento e geração de métricas customizadas.
- A configuração do Dockerfile e docker-compose está presente para facilitar a execução em ambientes de contêiner.
- A documentação do projeto está incompleta no README.md, necessitando de uma descrição mais detalhada do projeto.