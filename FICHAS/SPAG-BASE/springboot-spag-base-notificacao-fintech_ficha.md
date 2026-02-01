## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço REST desenvolvido para gerenciar notificações de fintechs. Ele possui uma estrutura básica de diretórios, arquivos de configuração, Dockerfile e dependências comuns. O serviço expõe uma API para enviar notificações, que são armazenadas em um banco de dados.

### 2. Principais Classes e Responsabilidades
- **NotificacaoFintechService**: Serviço responsável por processar e enviar notificações de fintech.
- **DocketConfiguration**: Configuração do Swagger para documentação da API.
- **NotificacaoFintech**: Classe de domínio representando uma notificação de fintech.
- **NotificacaoFintechRequest**: Classe de domínio representando a requisição de notificação.
- **NotificacaoFintechResponse**: Classe de domínio representando a resposta após o processamento da notificação.
- **TipoNotificacaoEnum**: Enumeração dos tipos de notificações possíveis.
- **NotificacaoFintechRepository**: Repositório responsável por interagir com o banco de dados para operações de inserção de notificações.
- **NotificacaoFintechApi**: Classe controladora REST que expõe o endpoint para envio de notificações.
- **Server**: Classe principal que inicia o aplicativo Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Gradle
- Swagger
- Docker
- Microsoft SQL Server
- JUnit
- Mockito

### 4. Principais Endpoints REST
| Método | Endpoint   | Classe Controladora         | Descrição                                 |
|--------|------------|-----------------------------|-------------------------------------------|
| POST   | /notificar | NotificacaoFintechApi       | Envia uma notificação de fintech.         |

### 5. Principais Regras de Negócio
- Inserção de notificações no banco de dados com validação de dados.
- Tratamento de exceções durante o processo de envio de notificações.
- Autenticação básica para acesso à API.

### 6. Relação entre Entidades
- **NotificacaoFintech**: Representa uma notificação com atributos como data de envio, tipo, protocolo, conta, CNPJ, descrição, arquivo, login, ativo, data de inclusão e alteração.
- **TipoNotificacaoEnum**: Enumeração para definir tipos de notificações como "MOVIMENTACAO" e "EXTRATO".

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo   | Operação | Breve Descrição |
|-----------------------------|--------|----------|-----------------|
| TbControleArquivoContaFintech | tabela | SELECT   | Tabela que armazena informações de notificações de fintech. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo   | Operação | Breve Descrição |
|-----------------------------|--------|----------|-----------------|
| TbControleArquivoContaFintech | tabela | INSERT   | Tabela onde as notificações de fintech são inseridas. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
Não se aplica.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e segue boas práticas de desenvolvimento, como uso de injeção de dependências, separação de responsabilidades e documentação com Swagger. No entanto, poderia haver mais comentários explicativos em algumas partes do código para melhorar a legibilidade e manutenibilidade.

### 13. Observações Relevantes
- O projeto utiliza o Gradle para gerenciamento de dependências e construção do projeto.
- A configuração do Swagger está presente para facilitar a documentação e teste da API.
- O sistema possui testes unitários e de integração, garantindo a qualidade e funcionalidade do código.