# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável pela **baixa operacional de boletos de pagamento** integrado à CIP (Câmara Interbancária de Pagamentos). O sistema processa solicitações de baixa de boletos registrados, tanto em modo normal quanto em contingência, realizando validações de negócio, integrações com serviços externos (SOAP e REST) e persistência de dados em banco de dados Oracle. Suporta operações intrabancárias e interbancárias, com tratamento específico para boletos do Banco Votorantim (655) e BVSA (413).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `BaixaOperacionalServiceImpl` | Orquestra o processo de baixa operacional, coordenando validações, integrações CIP e persistência |
| `ControlarOperacoesCipImpl` | Implementa lógica de controle de operações CIP (normal, contingência, bloqueio), montagem de dados e validações |
| `CacheBoletoServiceImpl` | Gerencia remoção de cache de boletos via API REST |
| `RoteadorSpbbService` | Integração REST com o roteador SPBB para efetivação de baixa operacional |
| `ControlarOperacoesCipConsumer` | Consome serviços SOAP da CIP para confirmação de boleto pagamento |
| `MapperBoletoBaixa` | Converte objetos `BoletoCompletoInfo` para formato DDA0108 |
| `SolicitacaoBaixaMapper` | Mapeia dados de boleto para DTO de solicitação de baixa |
| `HttpIntegration` | Classe base para integrações HTTP com gerenciamento de token OAuth |
| `TokenIntegration` | Obtém e gerencia tokens OAuth para autenticação em APIs |
| `WSSecurityUtil` | Utilitário para configuração de segurança WS-Security em clientes SOAP |
| `UsernameTokenHandler` | Handler JAX-WS para adicionar header UsernameToken em requisições SOAP |
| `BaixaOperacionalUtils` | Métodos utilitários para conversões, validações e formatações |

---

## 3. Tecnologias Utilizadas

- **Java EE 7 / Jakarta EE** (EJB 3.1, CDI, JAX-WS, JAX-RS)
- **Maven** (gerenciamento de dependências e build)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **SOAP Web Services** (JAX-WS para integração CIP)
- **REST APIs** (Apache HttpClient para integrações)
- **OAuth 2.0** (autenticação client_credentials)
- **WS-Security** (UsernameToken para SOAP)
- **JDBC** (acesso a banco de dados Oracle)
- **SLF4J** (logging)
- **Gson** (serialização/deserialização JSON)
- **Apache Commons Lang3**
- **JNDI** (lookup de configurações)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/boleto/removerCacheBoleto/{codigoBarra}` | `ConsultarBoletoPagamentoApi` | Remove cache de um boleto específico |
| GET | `/v1/boleto/removerTodosCacheBoleto` | `ConsultarBoletoPagamentoApi` | Remove todos os caches de boletos |

**Observação:** O sistema é primariamente um backend de processamento (EJB), não expõe endpoints REST próprios, mas consome APIs REST externas.

---

## 5. Principais Regras de Negócio

1. **Validação de Modo CIP**: Sistema verifica se CIP está em modo normal (S), contingência (C), bloqueio (B) ou desligado (N)
2. **Retentativas**: Até 1 retentativa em caso de falha na baixa operacional
3. **Baixa Integral vs Parcial**: Determina tipo de baixa baseado em valor pago, valor total e histórico de parcelas
4. **Intrabancária vs Interbancária**: Identifica se boleto é do próprio banco (655/413) ou de outro banco
5. **Validação STR**: Boletos com valor >= R$ 250.000,00 são classificados como STR
6. **Contingência ADDA114**: Em modo contingência, grava dados para processamento batch posterior
7. **Portador e Agregador**: Identifica corretamente CPF/CNPJ do portador e agregador (fintech) conforme origem
8. **Conversão Código de Barras**: Converte linha digitável (47 posições) para código de barras (44 posições)
9. **Data Movimento**: Utiliza data de movimento do boleto para processamento CIP
10. **Remoção de Cache**: Remove cache de boleto após baixa bem-sucedida

---

## 6. Relação entre Entidades

**Principais DTOs e suas relações:**

- **DicionarioPagamento**: Entidade central contendo todos os dados do lançamento/pagamento
  - Contém `BoletoPagamentoCompleto` (dados do boleto da CIP)
  - Relaciona-se com `LancamentoBaixaOperacionalDTO` (dados específicos de baixa)
  
- **BoletoCompletoInfo**: Estrutura de dados para envio à CIP
  - Contém `BoletoInfo` (dados básicos do boleto)
  - Mapeado para `BoletoBaixaDDA0108` (formato DDA)
  
- **SolicitacaoBaixaDTO**: Registro de solicitação de baixa
  - Persistido em banco para controle e auditoria
  
- **LancamentoBaixaOperacionalDTO**: Dados complementares do lançamento
  - Meio de pagamento, portador, flag de baixa CIP

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbLancamento (inferido) | tabela | SELECT | Consulta dados de lançamentos para baixa operacional |
| TbBaixaOperacional (inferido) | tabela | SELECT | Consulta histórico de baixas operacionais |
| TbRegistroPagamentoCIP (inferido) | tabela | SELECT | Consulta registros de pagamento CIP |

**Observação:** Nomes de tabelas inferidos a partir dos DAOs mencionados no código (`BaixaOperacionalSpagDAO`, `BaixaOperacionalPgftDAO`, `BaixaSpagDAO`), mas não há código DAO disponível para confirmação exata.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSolicitacaoBaixa (inferido) | tabela | INSERT/DELETE | Insere e remove solicitações de baixa operacional |
| TbRegistroPagamentoCIP (inferido) | tabela | INSERT | Grava envios de baixa operacional em contingência |
| TbBaixaOperacional (inferido) | tabela | UPDATE | Atualiza status de baixa operacional (flag e status) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| errorMessages.properties | leitura | commons/src/main/resources | Mensagens de erro do sistema |
| roles.properties | leitura | commons/src/main/resources | Definição de roles de segurança |
| config-arqt-base (ResourceBundle) | leitura | `ConfigArqtrBaseProperties` | Configurações de URLs e endpoints |

**Observação:** Sistema não gera arquivos físicos diretamente, mas em modo contingência prepara dados para geração de arquivo ADDA114 por processo batch externo.

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| CIP - Serviço SOAP BoletoPagamentoIntegrationService | SOAP | Confirmação de boleto pagamento na Câmara Interbancária |
| Roteador SPBB | REST | Efetivação de baixa operacional via API REST |
| Serviço OAuth Intranet | REST | Obtenção de token JWT para autenticação |
| API Consulta Boleto | REST | Remoção de cache de boletos |

**Endpoints configurados via JNDI:**
- `cell/persistent/endpoint_baixa_operacional`
- `cell/persistent/url_atom_solicitar_baixa_boleto`
- `cell/persistent/endpoint_consulta_boleto`

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, integration, persistence, commons)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-WS)
- Tratamento de exceções e logging presente
- Uso de DTOs para transferência de dados
- Configurações externalizadas via JNDI

**Pontos Negativos:**
- **Código comentado extensivamente**: Muitos trechos de código comentado (TODOs, código antigo) poluem a leitura
- **Métodos muito longos**: `montarDadosEnvioBaixaOperacional` e `efetuarBaixaOperacionalBoletoCIP` são extensos e complexos
- **Lógica de negócio duplicada**: Validações de tipo de baixa repetidas em vários métodos
- **Falta de testes unitários**: Apenas classes de teste vazias ou não enviadas
- **Acoplamento**: Dependência direta de classes concretas em alguns pontos
- **Magic numbers e strings**: Códigos hardcoded (655, 413, "S", "C", etc.) sem constantes nomeadas em alguns casos
- **Documentação inconsistente**: Javadoc ausente ou incompleto em muitos métodos
- **Tratamento genérico de exceções**: Catch de `Exception` genérico em vários pontos

---

## 14. Observações Relevantes

1. **Segurança**: Sistema utiliza WS-Security (UsernameToken) para SOAP e OAuth 2.0 para REST, com credenciais gerenciadas via JNDI

2. **Auditoria**: Trilha de auditoria implementada via handlers JAX-WS (`FormatadorTrilhaOutbound`, `CapturadorTrilhaOutbound`)

3. **Configuração Ambiente**: Sistema preparado para múltiplos ambientes (DES, QA, UAT, PRD) com WSDLs específicos

4. **Handlers SOAP Customizados**: 
   - `UsernameTokenHandler`: Adiciona header de segurança
   - `SOAPLoggingHandler`: Log de mensagens SOAP
   - `CodigoRetornoBaixaOperacionalUtil`: Extrai código de retorno da CIP

5. **Modo Contingência**: Sistema possui mecanismo robusto para operar em contingência quando CIP está indisponível

6. **Bancos Suportados**: Tratamento específico para Banco Votorantim (655) e BVSA (413)

7. **Encoding**: Sistema trata encoding UTF-8 explicitamente em requisições HTTP

8. **SSL/TLS**: Configuração de SSLContext com suporte a TLSv1, TLSv1.1 e TLSv1.2

9. **Retry**: Implementado retry manual em `RoteadorSpbbService` para chamadas REST

10. **Cache Management**: Sistema remove cache de boletos após processamento bem-sucedido para garantir consistência