## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma biblioteca Java desenvolvida com Spring Boot, destinada à validação de objetos DTO (Data Transfer Object) utilizando chaves configuráveis. Ele permite verificar se os campos de um DTO correspondem a regras definidas por uma chave de configuração.

### 2. Principais Classes e Responsabilidades
- **CampoCorrespondencia**: Anotação para marcar campos de DTO que devem ser validados.
- **MensagemErroRegra**: Enumeração que define mensagens de erro para regras de validação.
- **CampoCorrespondenciaException**: Exceção personalizada para erros relacionados à validação de campos de correspondência.
- **ChaveConfiguravelParser**: Classe responsável por analisar e dividir a chave configurável em regras de validação.
- **RegraConfiguravel**: Classe que representa uma regra de validação configurável, contendo lógica para verificar correspondência e calcular pontuação.
- **ValidadorCampoCorrespondencia**: Classe que executa a validação dos DTOs com base nas regras configuráveis.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Maven
- Log4j para logging
- JUnit e Mockito para testes

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Validação de DTOs com base em chaves configuráveis.
- Correspondência de campos de DTO com valores esperados definidos nas regras.
- Cálculo de pontuação para determinar a melhor regra de correspondência.

### 6. Relação entre Entidades
Não se aplica.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
Não se aplica.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, com uso adequado de padrões de projeto e boas práticas de programação. A utilização de exceções personalizadas e enumerações para mensagens de erro contribui para a clareza e manutenibilidade. No entanto, a documentação poderia ser mais detalhada em alguns pontos, especialmente nas classes de validação.

### 13. Observações Relevantes
A biblioteca é configurada para ser utilizada em ambientes que suportam Java 11 e Maven. A estrutura do projeto é modular, facilitando a integração com outros sistemas que necessitem de validação de DTOs.