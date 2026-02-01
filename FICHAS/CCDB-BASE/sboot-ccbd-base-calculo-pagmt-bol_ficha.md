# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-calculo-pagmt-bol** é um microserviço Spring Boot responsável por realizar cálculos de pagamento de boletos bancários. Ele valida dados de boletos, calcula valores de juros, multas, descontos e saldo devedor, considerando diferentes modelos de cálculo (recebedora ou destinatário), datas de vencimento, pagamentos parciais, baixas operacionais e efetivas. O serviço integra-se com APIs externas para obter informações sobre dias úteis e feriados, essenciais para os cálculos financeiros.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| `CalcularPagmtBoletoController` | Controller REST que expõe o endpoint de validação e cálculo de boletos |
| `CalcularPagmtBoletoServiceImpl` | Serviço principal que orquestra os cálculos de descontos, juros, multa e total |
| `CalcularDescontosServiceImpl` | Implementa a lógica de cálculo de descontos conforme regras de negócio |
| `CalcularJurosServiceImpl` | Implementa a lógica de cálculo de juros (dias corridos ou úteis) |
| `CalcularMultaServiceImpl` | Implementa a lógica de cálculo de multas |
| `CalcularTotalServiceImpl` | Calcula o valor total considerando baixas operacionais e efetivas |
| `ObterDiasUteisServiceImpl` | Integra com serviço externo para obter dias úteis e não úteis |
| `CalculatorUtil` | Utilitário com funções auxiliares para cálculos e validações |
| `DataUtil` | Utilitário para manipulação de datas |
| `HorarioUtil` | Utilitário para obter data atual |
| `BoletoCalcular` | Entidade de domínio representando os dados de entrada do boleto |
| `BoletoCalculado` | Entidade de domínio representando o resultado dos cálculos |

---

## 3. Tecnologias Utilizadas

- **Java 11**
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Security OAuth2** (autenticação e autorização JWT)
- **Lombok** (redução de boilerplate)
- **Springfox Swagger 3.0.0** (documentação OpenAPI)
- **Logback** com JSON (logging estruturado)
- **Micrometer Prometheus** (métricas e monitoramento)
- **RestTemplate** (cliente HTTP para integrações)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **JUnit/Mockito** (testes)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/pagamento-boleto/validar` | `CalcularPagmtBoletoController` | Valida dados do boleto e calcula valores de juros, multa, desconto e saldo devedor |

---

## 5. Principais Regras de Negócio

1. **Validação de Boleto Vencido**: Boletos vencidos não permitem desconto e podem ter restrições de pagamento dependendo da configuração
2. **Cálculo de Juros**: Suporta 9 tipos de cálculo (valor fixo, percentual ao dia/mês/ano, dias corridos ou úteis)
3. **Cálculo de Multa**: Suporta 3 tipos (isento, valor fixo, percentual)
4. **Cálculo de Desconto**: Suporta 7 tipos de desconto com base em datas e valores/percentuais
5. **Modelos de Cálculo**: Tipo 01/04 (recebedora - a calcular) e Tipo 02/03 (destinatário - calculado pela CIP)
6. **Pagamento Parcial**: Controla quantidade de pagamentos parciais permitidos e valores mínimo/máximo
7. **Baixas Operacionais e Efetivas**: Considera baixas já registradas no cálculo do saldo devedor
8. **Validação de Data de Agendamento**: Não permite agendamento em data passada ou boleto vencido (exceto fatura de cartão de crédito)
9. **Bloqueio de Pagamento**: Valida indicadores de bloqueio e situação do título
10. **Duplicidade de Pagamento**: Impede pagamento de boletos já baixados

---

## 6. Relação entre Entidades

- **BoletoCalcular**: Entidade de entrada contendo todos os dados do boleto (beneficiário, pagador, valores, datas, listas de juros/multa/desconto, baixas)
- **BoletoCalculado**: Entidade de saída com os valores calculados (juros, multa, desconto, saldo atual)
- **Titulo**: Representa configurações de juros, multa ou desconto (código, data, valor, percentual)
- **CalculoTitulo**: Representa cálculos pré-definidos pela CIP (modelo 02/03)
- **BaixaOperacional**: Representa baixas operacionais registradas
- **BaixaEfetiva**: Representa baixas efetivas confirmadas

**Relacionamentos**:
- BoletoCalcular possui listas de Titulo (juros, multa, desconto)
- BoletoCalcular possui lista de CalculoTitulo
- BoletoCalcular possui listas de BaixaOperacional e BaixaEfetiva
- BoletoCalculado é gerado a partir de BoletoCalcular após processamento

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs em formato JSON |
| sboot-ccbd-base-calculo-pagmt-bol.yaml | leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-dcor-base-atom-dias-uteis | API REST | Serviço para obter próxima data útil e listar dias não úteis (feriados). Usado nos cálculos de juros e multa baseados em dias úteis |
| OAuth2 JWT Provider | API REST | Provedor de autenticação JWT (api-digitaldes.bancovotorantim.com.br ou api-digital.bancovotorantim.com.br) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (presentation, service, calculator, domain)
- Uso adequado de padrões como Strategy (CalculatorService) e Service Layer
- Documentação OpenAPI bem estruturada
- Uso de Lombok reduzindo boilerplate
- Tratamento de exceções customizadas
- Configuração externalizada por profiles
- Logs estruturados em JSON

**Pontos de Melhoria:**
- Código com comentários em português misturados com código em inglês
- Métodos muito longos (ex: `validarBoleto` com múltiplas validações inline)
- Lógica de negócio complexa em switches extensos que poderiam ser refatorados para Strategy Pattern
- Falta de testes unitários nos arquivos fornecidos (marcados como NAO_ENVIAR)
- Alguns métodos com responsabilidades múltiplas (ex: `montarBoleto` faz conversão e mapeamento)
- Uso de `BigDecimal` sem escala consistente em alguns pontos
- Falta de validação de nulos em alguns fluxos
- Código com lógica duplicada entre cálculos de juros/multa

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza OAuth2 com JWT para autenticação, com endpoints públicos configurados para Swagger
2. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
3. **Monitoramento**: Expõe métricas Prometheus na porta 9090 e health checks
4. **Containerização**: Possui Dockerfile configurado para deploy em Google Cloud Platform
5. **Infraestrutura como Código**: Arquivo infra.yml define configurações de deploy no Kubernetes/OpenShift
6. **Auditoria**: Integra com biblioteca de trilha de auditoria do Banco Votorantim
7. **Versionamento**: API versionada (v1) seguindo boas práticas REST
8. **Cálculos Financeiros**: Utiliza `BigDecimal` com truncamento para 2 casas decimais (RoundingMode.DOWN)
9. **Dependência Externa Crítica**: O serviço de dias úteis é essencial para cálculos corretos - falhas nessa integração podem impactar o negócio
10. **Modelo Multi-módulo**: Projeto Maven dividido em módulos `domain` e `application` para melhor organização