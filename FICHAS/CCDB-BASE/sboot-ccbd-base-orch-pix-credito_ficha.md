# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-pix-credito** é um microsserviço orquestrador responsável por processar transações PIX utilizando cartão de crédito. Ele coordena múltiplas etapas do processo, incluindo validação de limites, cálculo de tarifas, autorização de pagamento, efetivação de transferências TEF e PIX, além de gerenciar estornos em caso de falhas. O sistema segue uma arquitetura baseada em Spring Boot com Apache Camel para orquestração de fluxos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `PixCreditoController` | Controller REST v1 que recebe requisições de processamento PIX crédito |
| `PixCreditoControllerV2` | Controller REST v2 com funcionalidades estendidas (validação de titularidade, efetivação PIX) |
| `PixCreditoService` | Serviço de domínio que orquestra o fluxo de processamento via Apache Camel |
| `PixCreditoRouter` | Define as rotas Camel com os fluxos de processamento (v1 e v2) |
| `TarifadorRepositoryImpl` | Integração com serviço de cálculo de tarifas (IOF, encargos, tributos) |
| `AutorizadorRepositoryImpl` | Integração com serviço de autorização de pagamento com cartão de crédito |
| `SalvarTransacaoPixCreditoRepositoryImpl` | Persiste transação PIX crédito no atom |
| `TransferenciaTefRepositoryImpl` | Efetiva transferência TEF entre contas |
| `EfetivarTransacaoPixRepositoryImpl` | Efetiva a transação PIX propriamente dita |
| `ConsultarLimitePixCreditoRepositoryImpl` | Valida limite diário de PIX crédito (R$ 1.000,00) |
| `VerificarTitularidadeDestinatarioRepositoryImpl` | Valida se destinatário não é o próprio remetente |
| `ValidaClienteRepositoryImpl` | Valida situação da conta corrente do cliente |
| `EstornarTransacaoRepositoryImpl` | Envia notificação de estorno para fila RabbitMQ |
| `ConsultarDadosPessoaRepositoryImpl` | Consulta dados cadastrais da pessoa |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** (framework principal)
- **Apache Camel 3.0.1** (orquestração de fluxos)
- **Spring Security OAuth2** (autenticação JWT)
- **RabbitMQ** (mensageria para estornos)
- **RestTemplate** (cliente HTTP para integrações)
- **Swagger/OpenAPI** (documentação de APIs)
- **Lombok** (redução de boilerplate)
- **JUnit 5 + Mockito** (testes unitários)
- **Maven** (gerenciamento de dependências)
- **Docker** (containerização)
- **Kubernetes/OpenShift** (orquestração de containers)
- **Logback** (logging com formato JSON)
- **Actuator + Prometheus** (monitoramento e métricas)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/pix-credito/processar` | `PixCreditoController` | Processa PIX crédito (fluxo básico sem efetivação PIX) |
| POST | `/v2/banco-digital/pix-credito/processar` | `PixCreditoControllerV2` | Processa PIX crédito com validações adicionais e efetivação PIX |

**Headers obrigatórios:**
- `codigoBanco`: Código do banco (161 ou 436)
- `numeroAgencia`: Número da agência
- `numeroConta`: Número da conta
- `tipoConta`: Tipo da conta (5=CC, 6=CT, etc)

---

## 5. Principais Regras de Negócio

1. **Limite Diário PIX Crédito**: Valor máximo de R$ 1.000,00 por dia para transações PIX com cartão de crédito
2. **Validação de Titularidade**: Não permite transferências PIX crédito para contas da mesma pessoa (mesma titularidade)
3. **Validação de Conta**: Verifica se conta está ativa e desbloqueada para movimentações
4. **Cálculo de Tarifas**: Calcula IOF, encargos e tributos via serviço tarifador
5. **Autorização de Pagamento**: Valida disponibilidade de limite no cartão de crédito
6. **Fluxo de Estorno**: Em caso de falha após autorização, executa estorno automático via fila
7. **Tipos de Estorno**: 
   - ESTORNO_AUTORIZADOR (falha após autorização)
   - ESTORNO_AUTORIZADOR_BANCO_DADOS (falha após salvar no BD)
   - ESTORNO_AUTORIZADOR_BANCO_DADOS_TEF (falha após TEF)
8. **Produto PIX**: Código de produto fixo = 63
9. **Validação de Chave PIX**: Consulta chave DICT para validar destinatário

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **PixCreditoDTO**: Entidade central que trafega por todo o fluxo, contendo:
  - Dados do cliente (CPF, banco, agência, conta)
  - Dados do cartão selecionado
  - Valores (operação, IOF)
  - Tarifas calculadas (encargos, tarifas, tributos)
  - Protocolos (autorização, TEF, end-to-end)
  - Dados de efetivação PIX (chave, favorecido, NSU)

- **Cartao**: Dados do cartão de crédito (vencimento, últimos dígitos, tipo, bandeira, status)

- **DadosEfetivacaoPixDTO**: Informações específicas para efetivação PIX (chave, favorecido, NSU, QR Code)

- **PessoaDTO / ContaDTO / ParticipanteDTO**: Estrutura hierárquica de dados do favorecido

- **Protocolo**: Registros de protocolos gerados (TEF, CREDITO, END_TO_END)

**Relacionamentos:**
- PixCreditoDTO (1) -> (1) Cartao
- PixCreditoDTO (1) -> (0..1) DadosEfetivacaoPixDTO
- PixCreditoDTO (1) -> (0..3) TarifaDXC (encargos, tarifas, tributos)
- DadosEfetivacaoPixDTO (1) -> (1) PessoaDTO (favorecido)
- PessoaDTO (1) -> (0..1) ContaDTO
- ContaDTO (1) -> (0..1) ParticipanteDTO

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações PIX Crédito (via API) | API REST | SELECT | Consulta transações PIX crédito do dia para validação de limite |
| Dados Cadastrais Pessoa (via API) | API REST | SELECT | Consulta dados cadastrais da pessoa por CPF |
| Chaves DICT (via API) | API REST | SELECT | Consulta chave PIX no DICT |
| Validação Conta (via API) | API REST | SELECT | Valida situação da conta corrente |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Transações PIX Crédito (via API) | API REST | INSERT | Salva nova transação PIX crédito |
| Transações PIX Crédito (via API) | API REST | UPDATE | Atualiza status da transação (protocolos, status processamento) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

| Nome da Fila | Exchange | Routing Key | Descrição |
|--------------|----------|-------------|-----------|
| Fila de Estorno PIX Crédito | ex.ccbd.pix | estornar.pix.cartao | Notificações de estorno de transações PIX crédito |

**Estrutura da mensagem:**
```json
{
  "seqTransacao": "1234",
  "tipoEstorno": "ESTORNO_AUTORIZADOR_BANCO_DADOS_TEF"
}
```

---

## 12. Integrações Externas

| Sistema | Tipo | Descrição |
|---------|------|-----------|
| sboot-trbd-base-atom-tarifador | REST | Cálculo de tarifas (IOF, encargos, tributos) |
| sboot-cart-svhp-atom-autorizador | REST | Autorização de pagamento com cartão de crédito |
| sboot-ccbd-base-atom-pix-credito | REST | Persistência de transações PIX crédito |
| sboot-spag-base-orch-transferencias | REST | Efetivação de transferências TEF |
| sboot-ccbd-base-orch-efet-transf-pix | REST | Efetivação de transações PIX |
| sboot-glob-base-atom-cliente-dados-cadastrais | REST | Consulta de dados cadastrais |
| sboot-ccbd-base-orch-chaves-dict | REST | Consulta de chaves DICT |
| sboot-ccbd-base-orch-consulta-cc-cliente | REST | Validação de conta corrente |
| RabbitMQ | Mensageria | Envio de notificações de estorno |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository e Service
- Cobertura de testes unitários presente
- Uso de Apache Camel para orquestração de fluxos complexos
- Tratamento de exceções estruturado com enums
- Configuração externalizada por ambiente
- Uso de Lombok para reduzir boilerplate

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: mappers com lógica de negócio)
- Tratamento de exceções poderia ser mais granular em alguns pontos
- Falta de validações de entrada em alguns endpoints
- Código com alguns "magic numbers" e strings hardcoded
- Documentação inline (JavaDoc) ausente em várias classes
- Alguns métodos muito extensos que poderiam ser refatorados
- Uso de RestTemplate (legado) ao invés de WebClient (reativo)
- Configuração de segurança poderia ser mais explícita

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto está organizado em 3 módulos Maven (common, domain, application) seguindo boas práticas de separação
2. **Versionamento de API**: Possui duas versões de API (v1 e v2) com funcionalidades diferentes
3. **Ambientes**: Suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
4. **Bancos Suportados**: Trabalha com Banco Votorantim (161) e BVSA (436)
5. **Segurança**: Utiliza OAuth2 com JWT para autenticação
6. **Observabilidade**: Integrado com Prometheus para métricas e logs estruturados em JSON
7. **Container**: Preparado para execução em containers Docker/Kubernetes
8. **Testes**: Possui estrutura para testes unitários, integração e funcionais
9. **Geração de Código**: Utiliza Swagger Codegen para gerar clientes REST a partir de contratos OpenAPI
10. **Auditoria**: Integrado com framework de auditoria do BV