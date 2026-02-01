# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema orquestrador de cálculo de boletos bancários desenvolvido em Java com Spring Boot e Apache Camel. O sistema realiza consultas de boletos via CIP (Câmara Interbancária de Pagamentos), calcula juros, multas e descontos aplicáveis, valida parceiros e integra-se com múltiplos serviços externos para processamento completo de boletos de pagamento. Implementa regras de negócio complexas para cálculo de encargos baseados em diferentes modalidades (dias corridos, dias úteis, percentuais, valores fixos) e tipos de modelo de cálculo.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot |
| `BoletoRouter` | Roteador Apache Camel que orquestra o fluxo de processamento de boletos |
| `BoletoCalculadoServiceImpl` | Serviço principal para cálculo e consulta de boletos |
| `CalculoJurosServiceImpl` | Implementa lógica de cálculo de juros com múltiplas estratégias |
| `CalculoDescontoServiceImpl` | Implementa lógica de cálculo de descontos |
| `CalculoND2Service` | Gerencia estratégias de cálculo (Strategy Pattern) |
| `ProcessorCalculoBoleto` | Processador Camel que determina se deve realizar cálculo |
| `ProcessorCalculoBoletoVencido` | Processador que identifica boletos vencidos |
| `RequestConsultaBoletoCIPProcessor` | Processa requisições de consulta CIP e extrai clientId do JWT |
| `ResponseConsultaBoletoCipProcessor` | Processa respostas da consulta CIP |
| `BoletoCipApiRepositoryImpl` | Repositório para integração com API de consulta CIP |
| `SegurancaApiRepositoryImpl` | Repositório para validação de parceiros |
| `CalendarioApiRepositoryImpl` | Repositório para consulta de dias úteis e calendário |
| `CalcularBoletoRepositoryApiImpl` | Repositório para cálculo final de boletos |
| Estratégias (StrategyND2) | Implementações de diferentes modalidades de cálculo de juros |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.7.7
- **Orquestração**: Apache Camel (múltiplos componentes)
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven 3.8+
- **Segurança**: Spring Security OAuth2 Resource Server, JWT (java-jwt 4.0.0)
- **Serialização**: Jackson, Gson
- **Logging**: Logback com formato JSON
- **Documentação API**: OpenAPI Generator 7.1.0, SpringDoc OpenAPI
- **Testes**: JUnit 5, Mockito, Easy Random
- **Containerização**: Docker
- **Infraestrutura**: Google Cloud Platform (GCP)
- **Observabilidade**: Micrometer, Prometheus
- **Cliente HTTP**: RestTemplate, OkHttp
- **Auditoria**: sbootlib-atle-base-trilha-auditoria-web

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /atacado/pagamentos/consultaBoletoCalculado | BoletoRouter (via Camel) | Consulta e calcula boleto com juros, multas e descontos aplicáveis |

## 5. Principais Regras de Negócio

- **Validação de Parceiro**: Valida se o CPF/CNPJ do cliente está autorizado para o parceiro (clientId extraído do token JWT)
- **Consulta de Data de Referência**: Converte data de referência informada para o próximo dia útil caso necessário
- **Consulta CIP**: Busca dados completos do boleto na Câmara Interbancária de Pagamentos
- **Verificação de Situação**: Determina se o cálculo deve ser realizado baseado na situação do título (códigos 05, 11 ou 12)
- **Identificação de Boleto Vencido**: Compara data de referência com data de vencimento
- **Cálculo de Juros**: Aplica 10 estratégias diferentes de cálculo (isento, valor fixo, percentual, dias corridos, dias úteis, combinações)
- **Cálculo de Descontos**: Processa descontos com 7 modalidades diferentes (isento, valor fixo até data, percentual, antecipação)
- **Cálculo de Multa**: Aplica multa conforme configuração do título
- **Tipo de Modelo de Cálculo**: Suporta 4 tipos (01-Recebedora a calcular, 02-Destinatário calculado/Recebedora a calcular, 03-Destinatário calculado, 04-Recebedora a calcular)
- **Tratamento de Baixas**: Considera baixas operacionais e efetivas no cálculo
- **Validação de Abatimento**: Aplica abatimento conforme tipo de cálculo e situação do boleto
- **Cálculo de Dias Úteis/Corridos**: Integra com serviço de calendário para cálculos precisos

## 6. Relação entre Entidades

**Entidade Principal: BoletoCalculado**
- Contém: PessoaBeneficiarioOriginal (1:1)
- Contém: PessoaPagador (1:1)
- Contém: PessoaBeneficiarioFinal (0:1)
- Contém: SacadorAvalista (0:1)
- Contém: Lista de BaixaEfetiva (1:N)
- Contém: Lista de BaixaTitulo (1:N) - baixas operacionais
- Contém: Lista de Titulo (1:N) - descontos, juros, multas
- Contém: Lista de CalculoTitulo (1:N)

**BaixaEfetiva**
- Contém: BaixaTitulo (1:1)
- Atributos: canalPagamento, meioPagamento

**BoletoParametroRoute**
- Entidade de transporte entre processadores
- Atributos: apiKeyParceiro, codigoBarras, cpfCnpj, dataReferenciaRequest, dataReferenciaApi

**Titulo**
- Representa descontos, juros ou multas
- Atributos: codigo, data, percentual, valor

**CalculoTitulo**
- Resultado de cálculo para data específica
- Atributos: dataValidade, valorDesconto, valorJuros, valorMulta, valorTotalCobrar

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| logback-spring.xml | leitura | Configuração Logback | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | Spring Boot | Configuração principal da aplicação |
| application-local.yml | leitura | Spring Boot | Configuração para ambiente local |
| layers.xml | leitura | Docker Build | Configuração de camadas para otimização de imagem Docker |
| swagger/*.yaml | leitura | OpenAPI Generator | Especificações OpenAPI para geração de clientes e APIs |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| sboot-spag-base-atom-seguranca | REST API | Validação de documentos de parceiros (CPF/CNPJ) |
| springboot-spag-base-consulta-boleto | REST API | Consulta de boletos na CIP (Câmara Interbancária de Pagamentos) |
| sboot-cadc-base-atom-calendario | REST API | Consulta de dias úteis, cálculo de prazos e validação de datas |
| sboot-spag-base-atom-boleto | REST API | Cálculo final de boletos com todos os encargos |
| API Gateway OAuth | REST API | Autenticação e autorização via OAuth2 com JWT |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de padrões (Strategy, Repository)
- Uso adequado de Apache Camel para orquestração
- Testes unitários abrangentes com boa cobertura
- Configuração externalizada e adequada para múltiplos ambientes
- Uso de DTOs e mapeamento adequado entre camadas
- Implementação de auditoria e observabilidade
- Documentação OpenAPI bem estruturada

**Pontos de Melhoria:**
- Classe `BoletoCalculadoMapper` comentada (não utilizada)
- Algumas classes com lógica complexa que poderiam ser refatoradas (ex: `BoletoCipApiRepositoryImpl` com método muito extenso)
- Uso misto de BigDecimal e Double em algumas representações
- Falta de constantes para códigos mágicos (ex: "05", "11", "12" para situações)
- Alguns métodos estáticos em classes de serviço (ex: `CalculoDescontoServiceImpl`)
- Tratamento de exceções genérico em alguns pontos
- Logs com sanitização mas poderiam ter mais contexto de negócio
- Falta de documentação JavaDoc em métodos complexos

## 14. Observações Relevantes

- O sistema utiliza autenticação JWT e extrai o `clientId` do token para validação de parceiros
- Implementa 10 estratégias diferentes de cálculo de juros usando Strategy Pattern
- Suporta 4 tipos de modelo de cálculo com regras específicas para cada
- Integração com calendário bancário para cálculos precisos de dias úteis
- Configuração multi-camadas no Docker para otimização de build e deploy
- Utiliza RestTemplate com autenticação básica para algumas integrações
- Sistema preparado para ambientes DES, UAT e PRD com configurações específicas
- Implementa circuit breaker e retry através do framework Atlante
- Logs estruturados em JSON para facilitar análise e monitoramento
- Testes bem estruturados com uso de mocks e dados de teste realistas
- Arquitetura baseada em microserviços atômicos seguindo padrões do Banco Votorantim