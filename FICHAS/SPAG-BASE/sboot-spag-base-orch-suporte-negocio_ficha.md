---
## Ficha Técnica do Sistema

### 1. Descrição Geral
O **sboot-spag-base-orch-suporte-negocio** é um orquestrador de validações e enriquecimento de transações financeiras do Sistema de Pagamentos (SPAG). O sistema processa e valida diferentes tipos de operações bancárias (TED, TEF, DOC, PIX, Boletos, Tributos, Saque Digital) antes de sua efetivação, aplicando regras de negócio complexas, validações de limites, análise de fraude, verificação de dias úteis e integração com múltiplos sistemas externos. Utiliza Apache Camel para orquestração de rotas de processamento e implementa padrões de Clean Architecture.

---

### 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **SuporteNegocioController** | Controller REST V1 - endpoints de validação de transações (boleto, transferência, tributo, saque digital, arrecadação) |
| **SuporteNegocioV2Controller** | Controller REST V2 - versão aprimorada dos endpoints de transferência e boleto |
| **SuporteNegocioService** | Serviço principal que orquestra validações e enriquecimentos de lançamentos financeiros |
| **TransferenciaRouter** | Rota Camel para validação de transferências (TED/DOC) |
| **BoletoRouter** | Rota Camel para validação de pagamentos de boleto |
| **TributoRouter** | Rota Camel para validação de pagamentos de tributos |
| **TefRouter** | Rota Camel para validação de transferências entre contas (TEF) |
| **SaqueDigitalRouter** | Rota Camel para validação de saques digitais |
| **ValidacoesStnRouter** | Rota Camel para validações específicas STN (Sistema de Transferência Nacional) |
| **LimiteReservaPreValidacaoAspect** | Aspecto AOP que valida limite de reserva antes da execução de métodos anotados com @PreValidate |
| **AnaliseFraudeService** | Serviço de integração com análise de fraude transacional |
| **FeatureToggleService** | Gerenciador de feature toggles (ConfigCat) |
| **Lancamento** | Entidade de domínio representando um lançamento financeiro |
| **ValidadorBoleto/Transferencia/Tributo/SaqueDigital/Stn** | Interfaces de validadores específicos por tipo de operação |
| **Repositories (Impl)** | Implementações de integração com APIs externas (15+ sistemas) |
| **Mappers** | Conversores entre objetos de domínio e representações REST |

---

### 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Java 11** - Linguagem de programação
- **Apache Camel 3.2.0** - Orquestração de rotas e integração
- **Maven** - Gerenciamento de dependências
- **OAuth2 + JWT** - Segurança e autenticação
- **Swagger/OpenAPI** - Documentação de APIs
- **ConfigCat** - Feature Toggle
- **Spring AOP** - Programação orientada a aspectos
- **RestTemplate** - Cliente HTTP para integrações
- **Lombok** - Redução de boilerplate
- **Jackson** - Serialização JSON
- **SLF4J/Logback** - Logging

---

### 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/validaTransferencia | SuporteNegocioController | Valida e enriquece transferências TED/DOC |
| POST | /v2/validaTransferencia | SuporteNegocioV2Controller | Valida transferências V2 (TED IN/OUT, STN) |
| POST | /v1/validaPagamentoBoleto | SuporteNegocioController | Valida e enriquece pagamento de boleto |
| POST | /v2/validaPagamentoBoleto | SuporteNegocioV2Controller | Valida pagamento de boleto V2 |
| POST | /v1/validaPagamentoTributo | SuporteNegocioController | Valida e enriquece pagamento de tributos (DARF/GRU) |
| POST | /v1/validaSaqueDigital | SuporteNegocioController | Valida saque digital (feature toggle FT_SAQUE_DIGITAL_ATIVO) |
| POST | /v1/validarDocumentoParceiro | SuporteNegocioController | Valida documento de parceiro |
| POST | /v1/pagamentoArrecadacao | SuporteNegocioController | Valida pagamento de arrecadação |
| POST | /v1/validar/pagamento-manual | SuporteNegocioController | Valida pagamento manual |

---

### 5. Principais Regras de Negócio

- **Validação de Limites Transacionais**: Verifica limites diários e noturnos por tipo de operação e banco
- **Conversão TED Inteligente**: Converte automaticamente entre STR (código 32) e CIP (código 31) baseado em valor e horário
- **Grade Horária de Câmaras**: Valida horários de funcionamento das câmaras de compensação (STR26, CIP)
- **Validação de Dias Úteis**: Verifica se a data de movimentação é dia útil na praça padrão
- **Circuit Breaker Transacional**: Impede processamento duplicado de transações
- **Validação Fintech/Parceiro (CP1)**: Valida modalidade de parceiro e correspondente bancário
- **Análise de Fraude**: Integra com sistema de validação de fraudes (com contingência e retry)
- **Validação de Co-titulares**: Verifica co-titularidade em operações STN
- **Flag Débito Sem Saldo**: Permite débito incondicional baseado em configuração de empresa
- **Limites Saque Digital**: R$ 5.000 (comercial) / R$ 1.000 (noturno) com validação de cédulas
- **Validação CNPJ Raiz**: Valida 8 primeiros dígitos para pessoa jurídica
- **Enriquecimento ISPB**: Adiciona código ISPB dos bancos envolvidos
- **Validação Código de Barras**: 47 dígitos para boletos
- **Validação QR Code Saque Digital**: Formato parceiro/produto/versão/uuid/hash/numeroPC
- **Validação Mesma Titularidade**: Verifica se remetente e favorecido são o mesmo titular
- **Validação Limite Reserva**: Via AOP com feature toggle global ou por origem/sigla (suporta wildcard)

---

### 6. Relação entre Entidades

**Entidade Principal: Lancamento**
- Representa uma transação financeira completa

**Relacionamentos:**
- **Lancamento → Participante (Remetente)**: Dados do remetente (banco, agência, conta, CPF/CNPJ, nome)
- **Lancamento → Participante (Favorecido)**: Dados do favorecido
- **Lancamento → Participante (Co-titular)**: Co-titulares da conta (quando aplicável)
- **Lancamento → Fintech**: Dados de cliente fintech (quando aplicável)
- **Lancamento → ContaCorrente**: Informações da conta corrente (remetente/favorecido)
- **Lancamento → ConfigEmpresa**: Configuração de empresa (flag débito sem saldo)
- **Lancamento → LimiteReserva**: Reserva de limite transacional (SGLT)
- **Lancamento → ConfigCIP**: Configuração da Câmara Interbancária de Pagamentos
- **Lancamento → Boleto**: Dados específicos de boleto (código barras, vencimento, juros, desconto)
- **Lancamento → Tributo (STN)**: Dados de tributos (DARF/GRU, competência, unidade gestora)
- **Lancamento → AnaliseFraude**: Resultado da análise de fraude (protocolo, status)

**Hierarquia de Validadores:**
- ValidadorSimples (interface base)
  - ValidadorTransferencia
  - ValidadorBoleto
  - ValidadorTributo
  - ValidadorStn
  - ValidadorSaqueDigital

---

### 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Parametrizações (conversão TED) | API | SELECT/READ | Configurações de conversão TED entre STR e CIP |
| Parametrizações (config CIP) | API | SELECT/READ | Configurações da Câmara Interbancária de Pagamentos |
| Parametrizações (tesouraria) | API | SELECT/READ | Configurações de tesouraria por filial |
| Cadastro (bancos COMPE/ISPB) | API | SELECT/READ | Códigos COMPE e ISPB dos bancos |
| Cadastro (filiais) | API | SELECT/READ | Dados cadastrais de filiais por CNPJ/conta |
| Cadastro (domínios) | API | SELECT/READ | Tabelas de domínio (tags e valores) |
| Limites (tributos) | API | SELECT/READ | Limites de tributos por banco |
| Limites (transacionais) | API | SELECT/READ | Status de reserva de limite (NSU) |
| Parcerias (fintechs) | API | SELECT/READ | Dados de fintechs por CPF/CNPJ e código liquidação |
| Parcerias (correspondentes) | API | SELECT/READ | Validação de correspondentes bancários |
| Conta Corrente (clientes) | API | SELECT/READ | Dados de contas corrente de clientes |
| Conta Corrente (co-titulares) | API | SELECT/READ | Co-titulares de contas |
| Conta Corrente (saldos) | API | SELECT/READ | Saldos e bloqueios de contas |
| Conta Corrente Domínio | API | SELECT/READ | Datas de movimentação (último dia, data atual) |
| Produtos (transações) | API | SELECT/READ | Dados de transações e flag saldo |
| Produtos (finalidades) | API | SELECT/READ | Finalidades de transações por código liquidação |
| Produtos (grade horária) | API | SELECT/READ | Grade horária de câmaras de liquidação |
| Dias úteis (calendário) | API | SELECT/READ | Validação de dias úteis por praça |
| Cliente Dados Cadastrais | API | SELECT/READ | Dados cadastrais completos de clientes |
| Conta Fintech | API | SELECT/READ | Contas de usuários fintech |
| Circuit Breaker | API | SELECT/READ | Status de circuit breaker por transação |

---

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema é um orquestrador de validação e enriquecimento, não realiza atualizações diretas em banco de dados. As operações de escrita são delegadas para sistemas downstream após validação.

---

### 9. Arquivos Lidos e Gravados

Não se aplica. O sistema não manipula arquivos diretamente, apenas processa requisições REST e integra com APIs externas.

---

### 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, opera exclusivamente via endpoints REST síncronos.

---

### 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas, responde sincronamente às requisições REST.

---

### 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|----------------|------|-----------|
| **sboot-spag-base-atom-limites** | REST API | Consulta limites de tributos por banco |
| **sboot-spag-base-atom-parametrizacoes** | REST API | Configurações do sistema (CIP, conta, empresa, conversão TED) |
| **sboot-spag-base-atom-parcerias** | REST API | Validação de parceiros, fintechs e correspondentes bancários |
| **sboot-spag-base-atom-pagamento** | REST API | Geração de autenticação bancária |
| **sboot-spag-base-atom-seguranca** | REST API | Validação de clientId e extração de JWT |
| **sboot-sitp-base-atom-integrar-pagamento** | REST API | Transações ITP, cadastro (filiais, bancos, domínios), circuit breaker |
| **sboot-glob-base-atom-calendario** | REST API | Validação de dias úteis (versão 1) |
| **sboot-dcor-base-atom-dias-uteis** | REST API | Validação de dia útil e próximo dia útil (versão 2) |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | REST API | Dados cadastrais completos de clientes |
| **sboot-ccbd-base-atom-conta-corrente-dominio** | REST API | Domínio de conta corrente (datas de movimentação) |
| **sboot-ccbd-base-orch-consulta-cc-cliente** | REST API | Consulta completa de conta corrente (saldo, bloqueios, titular) |
| **springboot-spag-base-consulta-conta-fintech** | REST API | Consulta de contas de usuários fintech (autenticação básica SPAG) |
| **sboot-sglt-base-atom-limites-transacionais** | REST API | Gerenciador de limites transacionais (consulta status NSU) |
| **sboot-spag-base-orch-validacao-fraudes** | REST API | Análise de fraude transacional (com retry e contingência) |
| **Gateway BV OAuth2** | OAuth2 | Autenticação OAuth2 (clientId, clientSecret, tokenUrl) |

---

### 13. Avaliação da Qualidade do Código

**Nota: 7,5/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura limpa e bem organizada (Clean Architecture com separação domain/application/common)
- Uso adequado de padrões de integração (Apache Camel com routers e processors)
- Separation of Concerns bem aplicado (validadores, repositories, services)
- Tratamento de exceções customizado e estruturado
- Configuração externalizada em YAML por ambiente
- Documentação Swagger completa
- Segurança OAuth2 configurada adequadamente
- Logs estruturados e sanitizados
- Feature Toggles para controle de funcionalidades
- AOP para validações transversais (limite de reserva)
- Mappers bem definidos para conversão de objetos
- Enums para constantes e códigos de erro

**Pontos Negativos:**
- Falta de testes unitários significativos (stubs vazios mencionados)
- Complexidade elevada em algumas classes (SuporteNegocioService com múltiplos métodos similares)
- Possível duplicação de lógica entre validadores
- Dependência forte de integrações externas (15+ APIs) sem estratégia clara de fallback em todos os casos
- Documentação inline limitada em alguns componentes
- Alguns métodos muito longos que poderiam ser refatorados

**Recomendações:**
- Implementar testes unitários e de integração abrangentes
- Refatorar métodos longos aplicando Extract Method
- Adicionar circuit breakers para todas as integrações críticas
- Melhorar documentação JavaDoc
- Considerar cache para consultas frequentes (bancos, domínios)

---

### 14. Observações Relevantes

1. **Arquitetura Modular**: Projeto dividido em módulos application, domain e common, facilitando manutenção e evolução

2. **Orquestração Camel**: Uso extensivo de Apache Camel Routes para orquestração de fluxos de validação, permitindo composição flexível de regras

3. **Feature Toggles**: Sistema preparado para ativação/desativação de funcionalidades via ConfigCat:
   - FT_SAQUE_DIGITAL_ATIVO
   - FT_TEF_ROTA_MODERNIZADA
   - FT_VALIDA_LIMITE_RESERVA_GLOBAL
   - FT_VALIDA_LIMITE_RESERVA_POR_ORIGEM_SIGLA

4. **Validação Limite Reserva com Wildcard**: Suporta configuração flexível por origem/sigla com wildcard (*), permitindo regras genéricas e específicas

5. **Análise de Fraude com Contingência**: Integração com sistema de fraude possui retry policy e não bloqueia transação em caso de falha (contingência)

6. **Conversão TED Inteligente**: Lógica sofisticada de conversão entre STR (código 32) e CIP (código 31) baseada em valor e horário, otimizando custos

7. **Suporte Multi-banco**: Preparado para processar transações de múltiplos bancos (655-BV, 653, 888, 413-BVSA, 161)

8. **Validação CNPJ Raiz**: Implementa validação específica dos 8 primeiros dígitos do CNPJ para pessoa jurídica

9. **Geração de Código via Swagger**: Utiliza geração automática de código cliente/servidor a partir de contratos OpenAPI

10. **Properties por Ambiente**: Configurações específicas para des/qa/uat/prd, facilitando deploy em diferentes ambientes

11. **Modalidade Parceiro**: Validação específica de modalidade CV-PF/PJ para operações com parceiros

12. **Conta Especial 10000001**: Lógica específica para identificar transações de contas tipo CT/IF dos bancos BV/BVSA

13. **Autenticação Básica SPAG**: RestTemplate configurado com credenciais básicas para integração com sistema de consulta conta fintech

14. **Extração ClientId JWT**: Capacidade de extrair clientId do payload JWT (campo "aud") para auditoria e controle

15. **Validação Ordenada**: Validadores implementam Comparable para garantir ordem de execução específica das regras de negócio