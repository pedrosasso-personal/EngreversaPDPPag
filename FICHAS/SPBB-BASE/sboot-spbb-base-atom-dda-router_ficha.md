## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "DdaRouter" é um serviço atômico desenvolvido para centralizar o envio de solicitações de baixa de boletos e cancelamento de baixas de boletos para a Nuclea (CIP) via mensagens DDA0108 e DDA0115. Ele utiliza o framework Spring Boot e é configurado para operar com segurança, integração com o IBM MQ para envio de mensagens, e criptografia de dados.

### 2. Principais Classes e Responsabilidades
- **APIKeyAuthFilter**: Filtro de autenticação que verifica a presença de uma chave API no cabeçalho da requisição.
- **DdaRouterConfiguration**: Configuração de segurança e criação de beans para serviços e delegados da API.
- **DecryptConfiguration**: Configuração para serviços de criptografia e feature toggle.
- **JmsConfig**: Configuração para conexão com o IBM MQ e criação de templates JMS.
- **DdaRouterService**: Serviço principal que gerencia as operações de solicitação e cancelamento de baixa de boletos.
- **EncryptService**: Serviço responsável pela criptografia de mensagens.
- **FeatureToggleService**: Serviço que gerencia feature toggles.
- **DdaRouterApiDelegateImpl**: Implementação dos endpoints REST para solicitar e cancelar baixas de boletos.
- **DDAMapper**: Mapeamento entre representações de dados e entidades de domínio.
- **DdaRouterJMSRepositoryImpl**: Implementação de repositório para envio de mensagens via JMS.
- **Application**: Classe principal para inicialização da aplicação.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- IBM MQ
- Maven
- Swagger/OpenAPI
- Lombok
- Gson
- Spring Security
- Spring Retry

### 4. Principais Endpoints REST
| Método | Endpoint                     | Classe Controladora          | Descrição                        |
|--------|------------------------------|------------------------------|----------------------------------|
| POST   | /v1/solicitarBaixaBoleto     | DdaRouterApiDelegateImpl     | Solicita a baixa de um boleto.   |
| POST   | /v1/cancelarBaixaBoleto      | DdaRouterApiDelegateImpl     | Cancela a baixa de um boleto.    |

### 5. Principais Regras de Negócio
- Verificação de campos obrigatórios para diferentes tipos de baixa de boletos.
- Criptografia de mensagens antes do envio.
- Envio de mensagens para diferentes filas JMS baseado no ISPB.
- Utilização de feature toggles para habilitar/desabilitar funcionalidades.

### 6. Relação entre Entidades
- **DDA0108** e **DDA0115**: Entidades de domínio que representam os dados necessários para as operações de baixa e cancelamento de boletos.
- **DDAException**: Exceção personalizada para erros específicos do domínio DDA.
- **Enums**: APIKeyEnum e ISPBEnum para valores constantes usados no sistema.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
- **QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT**: Filas para envio de mensagens de baixa de boletos.

### 11. Integrações Externas
- Integração com IBM MQ para envio de mensagens.
- Utilização de SPBSecJava para criptografia de mensagens.
- Feature toggle via Atlante.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de annotations do Spring. A documentação está presente e os nomes das classes e métodos são claros e descritivos. No entanto, poderia haver uma maior separação de responsabilidades em algumas classes, e o uso de exceções poderia ser mais consistente.

### 13. Observações Relevantes
- A aplicação utiliza perfis de configuração para diferentes ambientes (local, des, uat, prd).
- A segurança é configurada para utilizar JWT para autenticação.
- O sistema está preparado para ser executado em ambientes Docker, conforme indicado pela estrutura de diretórios.