## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de Parcerias" é um microserviço desenvolvido para gerenciar parcerias financeiras, permitindo a inserção, consulta e atualização de correspondências TED, além de validações e consultas de clientes e fintechs. Utiliza o framework Spring Boot e integra-se com bancos de dados SQL Server para operações de persistência.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia o aplicativo Spring Boot.
- **CorrespondenciaTedController**: Controlador responsável por gerenciar endpoints relacionados a correspondências TED.
- **ParceriasController**: Controlador que gerencia endpoints relacionados a fintechs e clientes.
- **CorrespondenciaTedService**: Serviço que contém a lógica de negócios para operações de correspondência TED.
- **FintechService**: Serviço que gerencia operações relacionadas a fintechs e clientes.
- **CorrespondenteService**: Serviço para validação de correspondentes.
- **CorrespondeciaTedRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a correspondências TED.
- **CorrespondenteRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a correspondentes.
- **FintechRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a fintechs.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- JDBI
- SQL Server
- Swagger
- MapStruct
- Mockito

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/parcerias/buscarFintech | ParceriasController | Busca dados da Fintech pelo CNPJ e código de liquidação. |
| GET | /v1/parcerias/validarCorrespondente | ParceriasController | Valida se um correspondente é válido pelo CNPJ e conta. |
| GET | /v1/parcerias/buscarCliente | ParceriasController | Busca cliente pelo CNPJ, conta e código de liquidação. |
| GET | /v1/parcerias/buscarClientePorCdOrigem | ParceriasController | Busca cliente pelo CNPJ, conta, código de origem e liquidação. |
| POST | /v1/parcerias/buscar-parceiro | ParceriasController | Busca parceiro com base em parâmetros de cliente. |
| POST | /correspondencia-ted | CorrespondenciaTedController | Insere nova correspondência de TED. |
| GET | /correspondencia-ted | CorrespondenciaTedController | Busca paginada de correspondências TED. |
| PUT | /correspondencia-ted/{id} | CorrespondenciaTedController | Atualiza uma correspondência TED existente. |
| GET | /correspondencia-ted/max-codigo-lancamento | CorrespondenciaTedController | Retorna o código do último lançamento de TED. |
| GET | /correspondencia-ted/analistas | CorrespondenciaTedController | Lista analistas que realizaram correspondências de TEDs. |
| PUT | /correspondencia-ted/rejeicao | CorrespondenciaTedController | Rejeição de múltiplas TEDs. |

### 5. Principais Regras de Negócio
- Validação de correspondentes pelo CNPJ e conta.
- Inserção e atualização de correspondências TED.
- Consultas de clientes e fintechs com base em CNPJ, conta e códigos de liquidação e origem.
- Rejeição de múltiplas TEDs com status específico.

### 6. Relação entre Entidades
- **CorrespondenciaTed**: Relaciona-se com **StatusCorrespondenciaEnum** para definir o status da correspondência.
- **Cliente** e **UnifiedClienteFintech**: Compartilham atributos comuns e se relacionam com **UrlsParametrizados** para URLs de callback e notificações.
- **Fintech**: Entidade que representa dados de fintechs, incluindo URLs de callback e notificações.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCorrespondenciaTED | tabela | SELECT | Armazena dados de correspondências TED. |
| TbCorrespondenteBancario | tabela | SELECT | Armazena dados de correspondentes bancários. |
| TbParametroPagamentoFintech | tabela | SELECT | Armazena parâmetros de pagamento de fintechs. |
| TbValidacaoOrigemPagamento | tabela | SELECT | Armazena validações de origem de pagamento. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCorrespondenciaTED | tabela | INSERT/UPDATE | Inserção e atualização de dados de correspondências TED. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com APIs de autenticação via OAuth2.
- Integração com Swagger para documentação de APIs.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependência e separação de responsabilidades. A documentação é clara e os testes são abrangentes. No entanto, poderia haver uma maior cobertura de testes para casos de erro e exceções.

### 13. Observações Relevantes
- O projeto utiliza o padrão de microserviços atômicos, facilitando a escalabilidade e manutenção.
- A configuração de segurança é feita através de OAuth2, garantindo proteção aos endpoints expostos.
- A documentação via Swagger facilita o entendimento e uso das APIs disponíveis.