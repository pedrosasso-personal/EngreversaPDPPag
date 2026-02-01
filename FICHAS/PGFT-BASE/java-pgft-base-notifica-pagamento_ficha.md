# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-pgft-base-notifica-pagamento** é um componente de integração responsável por notificar e registrar lançamentos de pagamentos na base de dados PGFT (Plataforma de Gestão Financeira e Tesouraria). O sistema recebe informações de pagamentos através de uma API REST, valida, transforma e persiste esses dados em múltiplas bases de dados (PGFT e SPAG), além de realizar integrações com serviços externos via Apache Camel para obtenção de feature toggles. O componente também trata devoluções de pagamentos, atualizando os registros correspondentes.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `NotificaPagamentoPGFT` | Endpoint REST principal que recebe notificações de pagamento e orquestra o fluxo de processamento |
| `IncluirLancamentoBean` | Bean EJB responsável pela lógica de negócio de inclusão e atualização de lançamentos |
| `DeParaLegadoBean` | Bean EJB para conversão de códigos entre sistemas legados (BUC para PGF) |
| `TbLancamentoDAOImpl` | DAO para operações de leitura e escrita na tabela de lançamentos do PGFT |
| `DbSpagDAOImpl` | DAO para operações na base SPAG, incluindo atualização de referências cruzadas |
| `ChaveSequencialDAOImpl` | DAO para obtenção de chaves sequenciais através de stored procedure |
| `TbDeParaLegadoDAOImpl` | DAO para consulta da tabela de conversão de códigos legados |
| `CamelClient` | Cliente HTTP para integração com serviços externos via Apache Camel |
| `FeatureToggleIntegrationService` | Serviço de integração para consulta de feature toggles |
| `AccessToken` | Gerenciador de tokens OAuth para autenticação em serviços externos |
| `Lancamento` | Entidade de domínio representando um lançamento de pagamento |
| `TbLancamentoInputMapper` | Mapper para conversão de entidade de domínio em parâmetros SQL |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, JAX-RS, JAX-WS, CDI)
- **IBM WebSphere Application Server** (runtime)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados)
- **Apache HttpComponents** (cliente HTTP)
- **Google Gson** (serialização/deserialização JSON)
- **Oracle Database** (via JDBC)
- **SQL Server** (Sybase - bases DBPGF_TES e DBSPAG)
- **OAuth 2.0** (autenticação)
- **Apache Camel** (integração)
- **Swagger** (documentação de APIs)
- **Log4j2/SLF4J** (logging)
- **JUnit, Mockito, PowerMock** (testes)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/notificarPagamentoPGFT/` | `NotificaPagamentoPGFT` | Recebe notificação de pagamento e registra lançamento no PGFT |

---

## 5. Principais Regras de Negócio

1. **Validação de Duplicidade**: Antes de inserir um lançamento, verifica se já existe registro com mesmo protocolo, data de movimento, origem e liquidação
2. **Geração de Chave Sequencial**: Obtém número sequencial único através de stored procedure para identificação do lançamento
3. **Conversão de Códigos Legados**: Converte código BUC para código PGF através de tabela de-para
4. **Tratamento de Devoluções**: Para transações específicas (8408, 8678, 8680) com liquidação tipo 1, atualiza campos de devolução no lançamento original
5. **Exclusão Condicional de Registro**: Lançamentos de devolução TED (liquidação 31/32 com transação 7400) não são registrados no PGFT
6. **Feature Toggle para Boletos**: Consulta feature toggle para determinar se boletos devem ter baixa via job (campo flBoletoBaixa)
7. **Sincronização entre Bases**: Após inserir no PGFT, atualiza a base SPAG com o código do lançamento PGFT
8. **Tratamento de Dados Fintech**: Registra informações específicas de clientes Fintech (remetente e favorecido)
9. **Validação de Entidade**: Obtém código de entidade baseado no código de origem do pagamento

---

## 6. Relação entre Entidades

**Principais Entidades:**

- **Lancamento**: Entidade principal contendo todos os dados do lançamento de pagamento (protocolo, valores, datas, dados de remetente/favorecido, informações bancárias, etc.)
- **PkSeq**: Entidade para controle de chaves sequenciais (retorno da stored procedure)
- **DeParaLegado**: Entidade para mapeamento de códigos entre sistemas legados
- **LancamentoNotificaPGFT**: Entidade simplificada para retorno de consultas
- **DicionarioPagamento**: DTO de entrada/saída contendo dados completos do pagamento

**Relacionamentos:**
- Um `DicionarioPagamento` é convertido em um `Lancamento` para persistência
- `Lancamento` referencia código de instituição obtido através de `DeParaLegado`
- `PkSeq` fornece chave primária para novos `Lancamento`
- Lançamentos de devolução referenciam lançamentos originais através de `CdLancamentoOrigem`

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | tabela | SELECT | Verifica existência de lançamento duplicado |
| DBGLOBAL..TbDeParaLegado | tabela | SELECT | Consulta conversão de código BUC para código PGF |
| dbitp..tbl_sist_origem_spb | tabela | SELECT | Obtém código de entidade (grupo empresa) por código de origem |
| DBSPAG..TbLancamento | tabela | SELECT | Busca código de lançamento PGFT do lançamento original (para devoluções) |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBPGF_TES..TBL_LANCAMENTO | tabela | INSERT | Insere novo lançamento de pagamento no PGFT |
| DBPGF_TES..TBL_LANCAMENTO | tabela | UPDATE | Atualiza campos de devolução (protocolo, usuário, data/horário) |
| DBSPAG..TbLancamento | tabela | UPDATE | Atualiza código de lançamento PGFT e data de alteração |

---

## 9. Arquivos Lidos e Gravados

não se aplica

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
| Apache Camel (Orquestrador de Transferências) | API REST | Consulta feature toggles através do endpoint `/v1/featureToggle/{feature}` |
| Serviço OAuth | API REST | Obtém access token para autenticação em serviços externos |

**Detalhes da Integração Camel:**
- Autenticação via OAuth 2.0 (client credentials)
- Suporte a proxy (mor-isa)
- Configuração de endpoints via JNDI
- Retry automático em caso de token expirado (401)
- Suporte a requisições GET e POST com headers customizados

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (domain, persistence, business, integration, rs)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Implementação de DAOs com Spring JDBC
- Tratamento de exceções e logging
- Uso de mappers para conversão de dados

**Pontos Negativos:**
- Classe `NotificaPagamentoPGFT` muito extensa (mais de 400 linhas) com múltiplas responsabilidades
- Lógica de negócio complexa misturada com código de apresentação (REST endpoint)
- Métodos privados extensos que dificultam manutenção
- Uso excessivo de comentários de código desabilitado (plugins Maven)
- Falta de validações de entrada mais robustas
- Tratamento genérico de exceções em alguns pontos
- Código com dependências de configurações via JNDI que dificultam testes
- Alguns RowMappers vazios (retornam null)
- Mistura de nomenclaturas (português e inglês)
- Falta de documentação JavaDoc em classes críticas

---

## 14. Observações Relevantes

1. **Stored Procedure**: O sistema utiliza a stored procedure `prObterSequencialDisponivel` para geração de chaves sequenciais, garantindo unicidade dos identificadores de lançamento

2. **Múltiplas Bases de Dados**: O componente integra três bases distintas:
   - `jdbc/sitpBaseDbItpDS` (DBPGF_TES, DBGLOBAL, dbitp)
   - `jdbc/spagBaseDBSPAGDS` (DBSPAG)

3. **Configurações Externalizadas**: Utiliza variáveis JNDI para configuração de endpoints e credenciais:
   - `cell/persistent/endpoint_camel_oauth`
   - `cell/persistent/endpoint_camel_orch_transferencias`
   - `cell/persistent/client_id_spag`
   - `cell/persistent/client_secret_spag`

4. **Segurança**: 
   - Autenticação BASIC configurada
   - Roles: `intr-middleware` e `spag-integracao`
   - Integração com WAS Alias para credenciais

5. **Transações**: Beans configurados com `TransactionAttributeType.NOT_SUPPORTED`, indicando que o controle transacional é gerenciado externamente

6. **Feature Toggle**: Sistema consulta dinamicamente a feature `ft_boolean_boleto_baixa_via_job` para determinar comportamento de baixa de boletos

7. **Tratamento Especial**: Lançamentos de saque banco digital (liquidação 36) e compras com cartões têm tratamento diferenciado de dados de favorecido

8. **Versionamento**: Projeto na versão 0.20.0, indicando maturidade mas ainda em evolução

9. **Build**: Configurado para deploy em WebSphere com classloader PARENT_LAST e bibliotecas compartilhadas (arqt-base-lib, fjee-base-lib)