# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sitp-base-notifica-pagamento** é um componente de integração responsável por receber notificações de pagamentos do sistema SPAG e registrá-las na base de dados ITP (Sistema de Pagamentos). O sistema atua como um middleware que converte objetos `DicionarioPagamento` em entidades `CaixaEntradaSPB`, verifica duplicidades, persiste os dados e atualiza o status no sistema de origem (SPAG). É um componente crítico no fluxo de processamento de pagamentos, suportando diversos tipos de liquidação (DOC, TED, CIP, STR, boletos, etc.).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `NotificaPagamentoBean` | EJB Stateless que orquestra o processo de notificação de pagamentos, validando duplicidades e coordenando a persistência |
| `NotificaPagamentoServiceImpl` | Implementa a lógica de negócio para conversão de dados, verificação de lançamentos e atualização no SPAG |
| `NotificaPagamentoDAOImpl` | Implementa operações de persistência na tabela `TBL_CAIXA_ENTRADA_SPB` (banco ITP) |
| `DbSpagDAOImpl` | Implementa operações de atualização na tabela `TbLancamento` (banco SPAG) |
| `NotificaPagamentoSITP` | Endpoint REST que expõe a operação de notificação de pagamento |
| `CaixaEntradaSPB` | Entidade de domínio representando um lançamento na caixa de entrada do SPB |
| `RestExceptionMapper` | Tratador de exceções para endpoints REST |

---

## 3. Tecnologias Utilizadas

- **Java EE 6+** (EJB 3.1, JAX-RS, JAX-WS, CDI)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados via JDBC Template)
- **IBM WebSphere Application Server** (servidor de aplicação)
- **Oracle JDBC** (driver de banco de dados)
- **SLF4J + Log4j2** (logging)
- **Apache Commons Lang3** (utilitários)
- **Swagger/OpenAPI** (documentação de APIs REST)
- **JUnit + PowerMock + Mockito** (testes unitários)
- **Arquitetura Votorantim** (fjee-base-lib, arqt-base-lib - frameworks internos)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/notificarPagamentoSITP/` | `NotificaPagamentoSITP` | Recebe notificação de pagamento do SPAG e registra no ITP |

---

## 5. Principais Regras de Negócio

1. **Verificação de Duplicidade**: Antes de inserir um novo lançamento, o sistema verifica se já existe um registro com os mesmos critérios (Cod_Liquidacao, Dt_Movimento, CNPJ_CPF_Remetente, CdLancamentoOrigem)

2. **Exclusão de Devoluções TED**: Lançamentos com código de liquidação 31 ou 32 e código de transação 7400, ou código 36 com ocorrências, não são registrados (são devoluções)

3. **Conversão de Dados**: Transforma o objeto `DicionarioPagamento` em `CaixaEntradaSPB`, aplicando regras específicas por tipo de liquidação (ex: saque banco digital, compras com cartões)

4. **Status Pré-Confirmado**: Todos os lançamentos são inseridos com status 3 (confirmado pela tesouraria) e flag `FlPreConfirmado = 'S'`

5. **Atualização Bidirecional**: Após inserção no ITP, atualiza o protocolo gerado de volta na tabela do SPAG

6. **Busca de Protocolo Cliente**: Recupera o número de protocolo de solicitação do cliente no SPAG para vincular ao lançamento ITP

7. **Canal de Pagamento**: Define canal padrão (23) para tipos de liquidação DOC, CIP, STR e STR26 quando não informado

8. **Tratamento de Erros**: Captura exceções e registra ocorrências no objeto de resposta com flag de erro específico

---

## 6. Relação entre Entidades

**CaixaEntradaSPB** (entidade principal):
- Representa um lançamento de pagamento na caixa de entrada do SPB
- Contém dados completos de remetente, favorecido, valores, datas e metadados
- Relaciona-se com o sistema SPAG através dos campos `CdLancamentoSPAG` e `CdLancamentoOrigem`
- Possui mais de 100 atributos cobrindo diversos cenários de pagamento

**DicionarioPagamento** (objeto de transferência):
- Estrutura de dados recebida do sistema SPAG
- Contém informações do pagamento a ser notificado
- É convertido para `CaixaEntradaSPB` antes da persistência

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | SELECT | Consulta para verificar duplicidade de lançamentos (query: checaLancamento) |
| TbLancamento | tabela | SELECT | Busca o número de protocolo de solicitação do cliente no SPAG |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | INSERT | Insere novos lançamentos de pagamento no ITP (query: incluirLancamento) |
| TBL_CAIXA_ENTRADA_SPB | tabela | UPDATE | Atualiza lançamentos existentes (query: alterarCaixaEntradaSPB) - código comentado |
| TbLancamento | tabela | UPDATE | Atualiza o número de protocolo ITP no lançamento SPAG (query: atualizarLancamentoSpag) |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| NotificaPagamentoDAOImpl-sql.xml | leitura | NotificaPagamentoDAOImpl | Arquivo XML contendo as queries SQL para operações no banco ITP |
| DbSpagDAOImpl-sql.xml | leitura | DbSpagDAOImpl | Arquivo XML contendo as queries SQL para operações no banco SPAG |
| errorMessages.properties | leitura | commons/resources | Arquivo de mensagens de erro do sistema |
| roles.properties | leitura | commons/resources | Definição de roles de segurança da aplicação |

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
| SPAG (Sistema de Pagamentos) | Banco de Dados | Sistema de origem que envia notificações de pagamento e recebe atualizações de protocolo |
| ITP (Sistema de Pagamentos Interno) | Banco de Dados | Sistema de destino onde os lançamentos são registrados na tabela TBL_CAIXA_ENTRADA_SPB |

**DataSources configurados:**
- `jdbc/spagBaseDBSPAGDS` - Conexão com banco SPAG
- `jdbc/sitpBaseDbItpDS` - Conexão com banco ITP

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, service, persistence, domain, rs)
- Uso adequado de injeção de dependências (CDI/EJB)
- Implementação de DAO com Spring JDBC Template
- Logging estruturado com SLF4J
- Tratamento de exceções com mapeadores específicos
- Uso de arquivos XML externos para queries SQL (facilita manutenção)

**Pontos Negativos:**
- Classe `CaixaEntradaSPB` com mais de 100 atributos (violação do princípio de responsabilidade única)
- Método `convertDicionarioToCaixaEntrada` extremamente longo (mais de 150 linhas) com lógica complexa
- Código comentado não removido (atualização de lançamento)
- Falta de validações de entrada nos endpoints REST
- Ausência de DTOs específicos para request/response (reutilização de entidades de domínio)
- Nomenclatura inconsistente (mix de português e inglês)
- Falta de documentação JavaDoc nas classes principais
- Método `paramMapCaixaEntradaSPB` com mais de 100 linhas (repetitivo)
- Uso de valores mágicos (números hardcoded como 3, 7400, 23, 31, 32, 36)
- Tratamento genérico de exceções em alguns pontos

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo Maven**: O projeto está organizado em 9 módulos (commons, domain, persistence, integration, business, jms, ws, rs, ear), seguindo boas práticas de modularização

2. **Segurança**: Utiliza autenticação BASIC e roles declarativas (`intr-middleware`, `spag-integracao`)

3. **Transações**: Configurado com `TransactionAttributeType.NOT_SUPPORTED`, indicando que as transações são gerenciadas externamente ou de forma manual

4. **Handlers de Trilha de Auditoria**: Implementa handlers customizados para captura de trilha de auditoria em requisições inbound/outbound (padrão da arquitetura Votorantim)

5. **Versionamento**: Sistema na versão 0.23.0, indicando que ainda está em evolução

6. **Dependências Corporativas**: Forte dependência de bibliotecas internas Votorantim (fjee-base, arqt-base, spag-base)

7. **Swagger**: Configuração presente mas comentada no pom.xml do módulo RS

8. **Banco de Dados**: Utiliza SQL Server (sintaxe GETDATE() presente nas queries)

9. **Tipos de Liquidação Suportados**: DOC, CIP, STR, STR26, Saque Banco Digital, Compras com Cartões, entre outros (enum `TipoLiquidacaoEnum`)

10. **Protocolo Gerado**: O sistema gera um código de protocolo único (BigDecimal) através de sequence/identity do banco de dados