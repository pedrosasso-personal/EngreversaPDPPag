---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sbootlib-spag-base-correspondencia-ted** é uma biblioteca Java desenvolvida para validação dinâmica de objetos DTO (Data Transfer Objects) através de chaves configuráveis. O sistema permite definir regras de correspondência em formato de string que são parseadas e comparadas com os campos anotados dos DTOs, retornando os valores correspondentes quando há match completo. É uma solução genérica e reutilizável para mapeamento condicional de valores baseado em múltiplos critérios.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **CampoCorrespondencia** | Anotação para marcar campos do DTO que participarão da validação de correspondência |
| **ValidadorCampoCorrespondencia** | Classe principal que orquestra o processo de validação, recebe DTO e chave configurável e retorna os campos correspondentes |
| **ChaveConfiguravelParser** | Responsável por fazer o parsing da string de configuração e transformá-la em lista de objetos RegraConfiguravel |
| **RegraConfiguravel** | Representa uma regra de correspondência com campos de comparação e campos extras, realiza a verificação e pontuação |
| **MensagemErroRegra** | Enum que centraliza as mensagens de erro do sistema |
| **CampoCorrespondenciaException** | Exception customizada para erros de validação de correspondência |

### 3. Tecnologias Utilizadas
- **Java 11** (configurado no pom.xml)
- **Maven** (gerenciamento de dependências e build)
- **Log4j 2.25.0** (logging)
- **JUnit Jupiter 5.10.0** (testes unitários)
- **Mockito 5.20.0** (mocks para testes)
- **Reflection API** (acesso dinâmico aos campos anotados)
- **Java Streams API** (processamento funcional de coleções)
- **Regex Pattern** (parsing de strings configuráveis)

### 4. Principais Endpoints REST
Não se aplica. Esta é uma biblioteca utilitária sem endpoints REST.

### 5. Principais Regras de Negócio
1. **Validação por Correspondência**: O sistema compara valores de campos anotados do DTO com valores esperados definidos em uma chave configurável
2. **Sistema de Pontuação**: Cada regra recebe uma pontuação baseada no número de campos que correspondem aos valores esperados
3. **Seleção da Melhor Regra**: Dentre múltiplas regras, seleciona aquela com maior pontuação que atinge 100% de correspondência (pontuação máxima)
4. **Parsing de Chave Configurável**: Formato esperado: `campo1=valor1,campo2=valor2|extra1=valorA;campo1=valor3,campo2=valor4|extra2=valorB`
   - Separador de regras: `;`
   - Separador de condições e extras: `|`
   - Separador de campos: `,`
   - Separador chave-valor: `=`
5. **Validação Obrigatória**: DTO não pode ser nulo e chave configurável não pode ser vazia
6. **Retorno Condicional**: Retorna Map com campos de comparação e extras apenas se houver correspondência perfeita, caso contrário retorna null

### 6. Relação entre Entidades
O sistema possui uma estrutura simples de classes utilitárias sem relacionamentos complexos:

- **ValidadorCampoCorrespondencia** (classe estática) → utiliza → **ChaveConfiguravelParser**
- **ValidadorCampoCorrespondencia** → trabalha com → **RegraConfiguravel**
- **ChaveConfiguravelParser** → cria lista de → **RegraConfiguravel**
- **RegraConfiguravel** → valida → **DTO anotado com @CampoCorrespondencia**
- **CampoCorrespondenciaException** → utiliza → **MensagemErroRegra**

Não há entidades de domínio persistentes, apenas DTOs transitórios validados pela biblioteca.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica. A biblioteca não acessa banco de dados.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica. A biblioteca não acessa banco de dados.

### 9. Arquivos Lidos e Gravados
Não se aplica. A biblioteca não realiza operações de I/O em arquivos.

### 10. Filas Lidas
Não se aplica. A biblioteca não consome mensagens de filas.

### 11. Filas Geradas
Não se aplica. A biblioteca não publica mensagens em filas.

### 12. Integrações Externas
Não se aplica. Esta é uma biblioteca standalone sem integrações externas. Ela é projetada para ser integrada por outros sistemas como dependência Maven.

### 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Uso adequado de Streams API e programação funcional
- Boa separação de responsabilidades entre as classes
- Logging detalhado em pontos estratégicos (debug, info, warn, error)
- Uso de Pattern pré-compilados para melhor performance em regex
- Tratamento de exceções customizado
- Uso de imutabilidade (Collections.unmodifiableList)
- Código relativamente limpo e legível

**Pontos de Melhoria:**
- Falta de documentação JavaDoc nas classes e métodos públicos
- Método `parseValoresCorrespondencia` declarado mas não utilizado no código
- Mistura de responsabilidades na classe RegraConfiguravel (validação + pontuação + getters/setters)
- Falta de validações mais robustas no parsing (ex: valores vazios após split)
- Ausência de constantes para strings mágicas (separadores, regex patterns)
- Tratamento genérico de exceções em alguns pontos (catch de CampoCorrespondenciaException | IllegalAccessException)
- Poderia ter interfaces para facilitar testes e extensibilidade
- Falta de validação de tipos dos campos (assume toString() sempre funciona)

### 14. Observações Relevantes

1. **Biblioteca Reutilizável**: Este é um componente de infraestrutura destinado a ser reutilizado em múltiplos projetos do grupo Votorantim (conforme groupId)

2. **Configuração Jenkins**: O arquivo jenkins.properties indica que o componente é buildado com JDK 21 (apesar do pom.xml configurar Java 11), utiliza Maven e é deployado na plataforma Google Cloud

3. **Versionamento**: Versão atual 1.0.4 sugere que a biblioteca já passou por algumas iterações e correções

4. **Uso de Reflection**: A biblioteca faz uso intensivo de Reflection API para acessar campos anotados dinamicamente, o que pode ter impacto em performance em cenários de alto volume

5. **Thread-Safety**: As classes são stateless (métodos estáticos ou sem estado mutável compartilhado), tornando a biblioteca thread-safe

6. **Flexibilidade**: O design permite validação de qualquer DTO desde que seus campos estejam anotados com @CampoCorrespondencia

7. **Limitação de Tipos**: A comparação é feita via toString(), o que pode não ser ideal para todos os tipos de dados (ex: números, datas)

8. **Ausência de Cache**: Não há cache do parsing de chaves configuráveis, o que pode ser ineficiente se as mesmas chaves forem validadas repetidamente