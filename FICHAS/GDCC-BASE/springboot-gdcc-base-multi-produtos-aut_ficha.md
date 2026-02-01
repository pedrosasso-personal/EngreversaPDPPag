## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por gerenciar a autenticação e autorização de débitos em conta, integrando-se com diversos sistemas de origem e bancos conveniados. O sistema utiliza JMS para comunicação assíncrona e possui endpoints para listar bancos conveniados e autenticar débitos em conta.

### 2. Principais Classes e Responsabilidades
- `AutenticacarDebitoContaBusinessService`: Gerencia a autenticação de débitos em conta, incluindo validação de campos e geração de registros de autorização.
- `AutorizacaoDebitoBusinessService`: Responsável por incluir registros de autorização de débitos e logs associados.
- `ContaConvenioService`: Consulta parâmetros de conta convênio.
- `ContaConvenioSistemaOrigemService`: Busca contas convênio do sistema de origem.
- `ListaBancoConveniadosService`: Lista bancos conveniados.
- `ModeloAutorizacaoService`: Busca modelos de autorização de débitos.
- `RegistroAutorizacaoDebitoService`: Consulta registros de autorização de débitos.
- `SistemaOrigemService`: Busca sistemas de origem.
- `ObterSequencialService`: Obtém sequenciais para registros de débitos.
- `ConverterJms`: Converte mensagens JMS para JSON e vice-versa.
- `DocketConfiguration`: Configura o Swagger para documentação de APIs.
- `JmsConfiguration`: Configura JMS para o sistema.
- `MappingMessageConverterCuston`: Converte mensagens para JSON utilizando Jackson.
- `AutenticarDebitoContaAPI`: Endpoint REST para autenticar débitos em conta.
- `ListaBancosConveniadosAPI`: Endpoint REST para listar bancos conveniados.
- `AutenticarDebitoContaJmsService`: Serviço JMS para enviar mensagens de autenticação e autorização de débitos.

### 3. Tecnologias Utilizadas
- Spring Boot
- JMS
- Swagger
- Sybase JDBC
- IBM MQ
- Jackson
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint                          | Classe Controladora               | Descrição                                      |
|--------|-----------------------------------|-----------------------------------|------------------------------------------------|
| POST   | /v1/autenticarDebitoConta         | AutenticarDebitoContaAPI          | Autentica débitos em conta.                    |
| GET    | /v1/listarBancoConveniado         | ListaBancosConveniadosAPI         | Lista bancos conveniados para multiprodutos.   |

### 5. Principais Regras de Negócio
- Validação de campos obrigatórios para autenticação de débitos.
- Geração de registros de autorização de débitos.
- Consulta de parâmetros de conta convênio.
- Listagem de bancos conveniados com filtros opcionais.

### 6. Relação entre Entidades
- `AutenticarDebitoContaRequest` e `AutenticarDebitoContaResponse` são utilizados para comunicação de autenticação de débitos.
- `ContaConvenioVO` e `ContaConvenioSistemaOrigemVO` representam dados de conta convênio.
- `ModeloAutorizacaoVO` e `RegistroAutorizacaoDebitoVO` são utilizados para autorização de débitos.
- `SistemaOrigemVO` representa sistemas de origem.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção                | Tipo     | Operação | Breve Descrição                                      |
|--------------------------------------------|----------|----------|------------------------------------------------------|
| TbContaConvenio                            | tabela   | SELECT   | Consulta parâmetros de conta convênio.               |
| TbContaConvenioSistemaOrigem               | tabela   | SELECT   | Busca contas convênio do sistema de origem.          |
| TbBanco                                    | tabela   | SELECT   | Lista bancos conveniados.                            |
| TbParametroAutorizacaoDebito               | tabela   | SELECT   | Consulta modelos de autorização de débitos.          |
| TbRegistroAutorizacaoDebito                | tabela   | SELECT   | Consulta registros de autorização de débitos.        |
| TbSistemaOrigem                            | tabela   | SELECT   | Busca sistemas de origem.                            |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção                | Tipo     | Operação | Breve Descrição                                      |
|--------------------------------------------|----------|----------|------------------------------------------------------|
| TbRegistroAutorizacaoDebito                | tabela   | INSERT   | Insere registros de autorização de débitos.          |
| TbAutorizacaoDebitoPrpsaCntro              | tabela   | INSERT   | Insere propostas de autorização de débitos.          |
| TbEventoRegistroAutorizacaoDbo             | tabela   | INSERT   | Insere logs de eventos de autorização de débitos.    |
| TbRegistroDebito                           | tabela   | INSERT   | Insere registros de débitos.                         |

### 9. Filas Lidas
- `DEV.QUEUE.1`: Fila para autenticação de débitos em conta.

### 10. Filas Geradas
- `DEV.QUEUE.2`: Fila para autorização de débitos em conta.
- `dev/`: Tópico para débitos em conta no varejo.
- `operacao`: Tópico para retorno de inclusão de débitos.

### 11. Integrações Externas
- Integração com IBM MQ para comunicação assíncrona.
- Integração com banco de dados Sybase para operações de débitos e autorizações.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação via Swagger é um ponto positivo. No entanto, algumas partes do código poderiam ser mais concisas e claras, especialmente em relação ao tratamento de exceções.

### 13. Observações Relevantes
- O sistema utiliza variáveis de ambiente para configuração de filas e tópicos JMS.
- A configuração de segurança LDAP está presente, mas desativada em ambientes de teste.
- O projeto possui suporte para testes unitários, de integração e funcionais.