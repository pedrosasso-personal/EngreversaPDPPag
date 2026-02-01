## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico desenvolvido em Java utilizando o framework Spring Boot. Ele é responsável por monitorar lotes, realizando operações de inserção e consulta de dados relacionados a contingências e números de controle em um banco de dados Sybase.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **AppConfiguration**: Configurações gerais da aplicação, incluindo conversores de mensagens HTTP e integração com Jdbi.
- **ExceptionHandler**: Manipulador de exceções específicas de negócios.
- **JdbiConfiguration**: Configuração do Jdbi para acesso ao banco de dados.
- **ContigenciaDomain**: Representa a entidade de contingência com atributos como moviId, nuControle, dtGravacao e dsHost.
- **NumeroControleDomain**: Representa a entidade de número de controle com atributos como dtMovto e numControle.
- **GlobalExceptionHandler**: Manipulador global de exceções, lidando com exceções de negócios e gerais.
- **RegraNegocioException**: Exceção específica para regras de negócio.
- **MonitoramentoLoteMapper**: Mapeia entre entidades de domínio e representações DTO.
- **MonitoramentoLoteRepository**: Interface de acesso ao banco de dados para operações de consulta e inserção.
- **MonitoramentoLoteApiDelegateImpl**: Implementação dos endpoints REST para monitoramento de lotes.
- **MonitoramentoLoteService**: Serviço que contém a lógica de negócios para operações de monitoramento de lotes.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Sybase
- Maven

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /monitoramento-lote/{grmsId}/{moviId} | MonitoramentoLoteApiDelegateImpl | Retorna o número de controle para um dado grmsId e moviId. |
| POST   | /monitoramento-lote/insere/ultimo-movimento | MonitoramentoLoteApiDelegateImpl | Insere o último movimento no banco de dados. |
| POST   | /monitoramento-lote/insere/contigencia | MonitoramentoLoteApiDelegateImpl | Insere uma contingência no banco de dados. |

### 5. Principais Regras de Negócio
- Inserção de dados de contingência e último movimento no banco de dados.
- Recuperação de número de controle baseado em parâmetros específicos.
- Manipulação de exceções de negócios e regras de negócio.

### 6. Relação entre Entidades
- **ContigenciaDomain** e **NumeroControleDomain** são entidades de domínio que representam dados de contingência e número de controle, respectivamente.
- **MonitoramentoLoteMapper** mapeia entre estas entidades e suas representações DTO.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_pmge_parametro_geral     | tabela | SELECT   | Retorna a data de movimento atual. |
| tb_movi_nu_ctrl_contingencia | tabela | SELECT   | Retorna o número de controle. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| tb_ulmv_ultimo_movimento_idt | tabela | INSERT  | Insere a data do último movimento. |
| tb_movi_nu_ctrl_contingencia | tabela | INSERT  | Insere dados de contingência. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com Sybase para operações de banco de dados.
- Utilização de JWT para autenticação via OAuth2.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e segue boas práticas de desenvolvimento, como o uso de injeção de dependências e separação de responsabilidades. No entanto, poderia haver mais documentação e comentários para facilitar o entendimento de partes complexas do código.

### 13. Observações Relevantes
- O projeto utiliza o modelo de microserviços atômicos.
- A configuração de segurança desativa o CSRF para endpoints públicos.
- O sistema possui testes unitários para validar a lógica de negócios e manipulação de exceções.