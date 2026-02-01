## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "java-flex-calc-controladoria-carga" é um projeto Java que utiliza a tecnologia Java EE para implementar serviços de controle de carga de contratos. Ele faz uso de EJBs para lógica de negócios e JAX-WS para serviços web. O objetivo principal do sistema é gerenciar a integração de contratos, incluindo inserção e validação de dados relacionados a contratos financeiros.

### 2. Principais Classes e Responsabilidades
- **ControladoriaCargaFlexService**: Interface que define o método para inserir contratos de controladoria.
- **ControladoriaCargaFlexServiceImpl**: Implementação da interface `ControladoriaCargaFlexService`, responsável por inserir contratos de controladoria utilizando um DAO.
- **IntegracaoContratoTO**: Classe que representa os dados de um contrato para integração.
- **ControladoriaCargaFlexDaoImpl**: Implementação do DAO para operações de banco de dados relacionadas a contratos de controladoria.
- **WebserviceBeanMapperImpl**: Classe responsável por mapear objetos entre diferentes representações, utilizando anotações para conversão.
- **BeanValidatorServiceImpl**: Implementação do serviço de validação de beans, verificando anotações como `NotNull` e `GreaterThanZero`.
- **ControladoriaLegadoServiceEndpoint**: Classe que expõe o serviço web para criar contratos de controladoria, incluindo validação e inserção de dados.

### 3. Tecnologias Utilizadas
- Java EE (EJB, JAX-WS)
- Maven
- Spring JDBC
- WebSphere Application Server
- SLF4J para logging
- JUnit e Mockito para testes

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Validação de campos obrigatórios e valores maiores que zero para contratos.
- Inserção de contratos de controladoria no banco de dados.
- Mapeamento de objetos entre diferentes representações utilizando conversores.
- Tratamento de falhas e geração de respostas de erro padronizadas.

### 6. Relação entre Entidades
- **IntegracaoContratoTO**: Entidade principal que contém informações detalhadas sobre o contrato.
- **ParceiroComercialInfoTO**: Entidade que representa informações sobre o parceiro comercial, utilizada dentro de `IntegracaoContratoTO`.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbIntegracaoContrato        | tabela                     | INSERT                        | Armazena informações de contratos integrados. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **Web Services**: Integração via JAX-WS para expor serviços de criação de contratos de controladoria.
- **Banco de Dados**: Utilização de Spring JDBC para operações de banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando padrões de projeto como DAO e Builder. As anotações para validação e conversão são bem aplicadas, facilitando a manutenção e extensão do sistema. No entanto, algumas partes do código poderiam ser melhor documentadas para aumentar a clareza.

### 13. Observações Relevantes
- O sistema utiliza o WebSphere Application Server para deploy, o que pode influenciar na configuração e execução dos serviços.
- A configuração de segurança é feita através de roles declaradas nas anotações dos EJBs.
- O projeto está dividido em múltiplos módulos Maven, cada um responsável por uma parte específica da aplicação (business, commons, persistence, ws, ear).