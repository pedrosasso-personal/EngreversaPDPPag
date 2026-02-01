## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico para validação de cartões de débito, desenvolvido em Java utilizando o framework Spring Boot. Ele realiza operações de verificação, inserção e atualização de informações de cartões de débito em um banco de dados, além de consumir mensagens de uma fila JMS para processar essas informações.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **CartaoConta**: Classe de domínio que representa as informações de um cartão de conta.
- **CartaoContaService**: Serviço que contém a lógica de negócio para verificar, inserir e atualizar informações de cartões de débito.
- **CartaoContaRepositoryImpl**: Implementação do repositório que interage com o banco de dados para realizar operações de verificação, inserção e atualização de cartões de débito.
- **CartaoContaListener**: Componente que escuta mensagens da fila JMS e inicia o processo de verificação de cartões de débito.
- **AppConfigurationListener**: Configuração de listeners JMS e conversores de mensagens.
- **MappingMessageLocalConverter**: Conversor de mensagens personalizado para integração com JMS.
- **DateFormatUtil**: Utilitário para formatação de datas.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot 2+
- Maven 3.5.3
- JUnit Jupiter 5+
- Lombok 1.18.10
- Swagger 2.9.2
- Microsoft SQL Server
- JMS (IBM MQ)

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Verificar se um cartão de débito já está registrado no sistema.
- Inserir novo cartão de débito no banco de dados caso não esteja registrado.
- Atualizar informações de cartão de débito existente.
- Registrar log de operações realizadas com cartões de débito.

### 6. Relação entre Entidades
- **CartaoConta**: Entidade principal que contém informações detalhadas sobre o cartão de conta, como banco, emissor, produto, conta, filial, entre outros atributos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbCartaoConta               | tabela                     | SELECT                 | Tabela que armazena informações de cartões de conta. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbCartaoConta               | tabela                     | INSERT, UPDATE                | Tabela que armazena informações de cartões de conta. |
| TbLogCartaoConta            | tabela                     | INSERT                        | Tabela que armazena logs de operações realizadas com cartões de conta. |

### 9. Filas Lidas
- QL.CCBD.STATUS_CARTAO.INT: Fila JMS de onde o sistema consome mensagens para processar informações de cartões de débito.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com IBM MQ para consumo de mensagens JMS.
- Integração com banco de dados Microsoft SQL Server para operações de leitura e escrita.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como a separação de responsabilidades entre classes e o uso de injeção de dependências. A documentação é clara e o uso de bibliotecas como Lombok e Spring Boot facilita a manutenção. No entanto, a ausência de testes unitários completos pode impactar a robustez do sistema.

### 13. Observações Relevantes
- O projeto utiliza um modelo de microserviços stateless, o que facilita a escalabilidade e a manutenção.
- A documentação do projeto está incompleta, especialmente na seção de descrição do README.md.
- A configuração de filas e banco de dados é feita através de arquivos YAML, permitindo flexibilidade na configuração para diferentes ambientes.