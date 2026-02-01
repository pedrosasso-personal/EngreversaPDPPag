## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "sboot-spbb-base-atom-ispb-piloto-reserva" é um serviço atômico desenvolvido em Java utilizando o framework Spring Boot. Ele é parte de uma arquitetura de microserviços e tem como objetivo gerenciar operações relacionadas a reservas e ajustes de valores em um contexto bancário. O sistema fornece uma API RESTful para interagir com diferentes funcionalidades, como consulta de reservas, ajuste de valores, e integração com sistemas externos.

### 2. Principais Classes e Responsabilidades
- **Application.java**: Classe principal que inicia a aplicação Spring Boot.
- **AppConfiguration.java**: Configurações gerais da aplicação, incluindo mapeamento de serviços e conversores de mensagens HTTP.
- **JdbiConfiguration.java**: Configuração do Jdbi para acesso a banco de dados, incluindo plugins e mapeadores de linha.
- **BusinessException.java**: Classe de exceção para erros de negócio.
- **GlobalExceptionHandler.java**: Manipulador global de exceções, configurando respostas para diferentes tipos de erros.
- **RegraNegocioException.java**: Exceção específica para regras de negócio.
- **WaitUtil.java**: Utilitário para pausar a execução por um determinado tempo.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Sybase
- Maven
- Swagger/OpenAPI

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /envia-pendentes/busca-data | N/A | Retorna a data do sistema. |
| GET    | /ajuste-reserva/{holdId}/{instId} | N/A | Retorna o valor da reserva. |
| POST   | /ajuste-reserva/inserir | N/A | Insere um ajuste de reserva. |
| PUT    | /ajuste-reserva/atualiza-valores | N/A | Atualiza os valores de reserva. |
| GET    | /piloto-reserva/verifica-certificado | N/A | Verifica o certificado. |
| PUT    | /piloto-reserva/movimento/prio/atualizar | N/A | Atualiza o movimento prioritário. |

### 5. Principais Regras de Negócio
- Tratamento de exceções específicas para regras de negócio.
- Configuração de serviços e mapeadores para operações de reserva e ajuste.
- Integração com sistemas externos para autenticação e autorização via OAuth2.

### 6. Relação entre Entidades
Não se aplica.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBISPB                      | tabela | SELECT   | Banco de dados principal utilizado para operações de reserva. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBISPB                      | tabela | INSERT/UPDATE | Atualizações de valores de reserva. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com APIs de autenticação via OAuth2.
- Utilização de Sybase como banco de dados.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, utilizando boas práticas de desenvolvimento como injeção de dependências e tratamento de exceções. A documentação e configuração são claras, facilitando a manutenção e entendimento do sistema. Poderia melhorar em termos de comentários e explicações sobre regras de negócio específicas.

### 13. Observações Relevantes
- O sistema utiliza um perfil de configuração para diferentes ambientes (local, des, uat, prd).
- A documentação do Swagger está bem detalhada, permitindo fácil acesso aos endpoints disponíveis.
- A configuração de logs é feita utilizando Logback, com suporte para JSON.

---