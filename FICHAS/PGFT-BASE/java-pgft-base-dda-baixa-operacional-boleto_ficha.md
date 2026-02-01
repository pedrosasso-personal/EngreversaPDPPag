# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema responsável por processar avisos de baixa operacional de títulos DDA (Débito Direto Autorizado) provenientes da CIP (Câmara Interbancária de Pagamentos). O sistema consome mensagens de uma fila JMS contendo informações sobre baixas operacionais de boletos, valida os dados, atualiza o status dos títulos no banco de dados e registra todas as informações relacionadas à baixa (pagamento, referências e dados do portador).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `AvisarBaixaOperacional` (MDB) | Message-Driven Bean que consome mensagens da fila JMS e orquestra o processamento |
| `AvisarBaixaOperacionalBean` | EJB Stateless que contém a lógica de negócio para processar avisos de baixa operacional |
| `AvisarBaixaOperacionalDAO` / `AvisarBaixaOperacionalDAOImpl` | Interface e implementação para acesso aos dados de títulos e baixas operacionais |
| `ConverterUtil` | Utilitário para conversão de mensagens JMS (TextMessage/BytesMessage) e desserialização XML para objetos Java |
| `DebitoDiretoAutorizadoDDA0108R2Mensagem` | Entidade de domínio gerada via JAXB representando a mensagem de baixa operacional |
| `TituloOUT` | DTO para transporte de informações básicas do título (código e valor) |
| `AvisarBaixaOperacionalStoreProcedure` | Stored Procedure (não utilizada na implementação atual) |
| `DataTypesUtil` | Utilitário para conversão de tipos de dados (String para BigDecimal/Integer) |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JMS, JAX-WS, JAX-RS, CDI)
- **WebSphere Application Server** (IBM)
- **Spring Framework** (Spring JDBC para acesso a dados)
- **JAXB 2.x** (para binding XML/Java)
- **Maven** (gerenciamento de dependências e build)
- **SLF4J** (logging)
- **JUnit 4** e **Mockito** (testes unitários)
- **Microsoft SQL Server** (banco de dados - schema DBPGF_TES)
- **IBM MQ** (JMS provider)
- **Log4j2** (configuração de logs)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Título**: Antes de processar a baixa, o sistema verifica se o título existe na base DDA através do número de identificação. Se não existir, registra erro e não processa.

2. **Atualização de Status do Título**: 
   - Se a baixa for integral (tipo 0 ou 1), o status do título passa para "Pago" (código 2)
   - Se a baixa for parcial (tipo 2 ou 3), o status permanece "Aberto" (código 1)

3. **Controle de Saldo**: O sistema atualiza o valor do saldo atual do título com base no valor da baixa operacional recebido.

4. **Registro Completo da Baixa**: Para cada baixa operacional são registrados:
   - Dados da baixa operacional (valor, tipo, código de barras, data/hora)
   - Referência da baixa
   - Informações de pagamento (meio, canal, data de processamento)
   - Dados da pessoa/portador (ISPB, CPF/CNPJ, nome/razão social)

5. **Transacionalidade**: Todas as operações de inserção/atualização são executadas em uma única transação. Em caso de erro, é realizado rollback.

6. **Retry de Mensagens**: O sistema utiliza o contador `JMSXDeliveryCount` para controlar tentativas de reprocessamento em caso de falha.

7. **Auditoria**: Todas as operações registram o login do sistema (`java-pgft-base-dda-baixa-operacional-boleto`) e timestamps de inclusão/alteração.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **TbTituloDDA**: Entidade central representando o título DDA
  - Relacionamento 1:N com **TbTituloDDABaixaOperacional**

- **TbTituloDDABaixaOperacional**: Registra cada baixa operacional do título
  - Relacionamento 1:1 com **TbTituloDDABaixaReferencia**
  - Relacionamento 1:1 com **TbTituloDDABaixaPagamento**
  - Relacionamento 1:1 com **TbTituloDDABaixaPessoa**

- **TbTituloDDABaixaReferencia**: Armazena referências da baixa operacional

- **TbTituloDDABaixaPagamento**: Contém informações sobre o meio e canal de pagamento

- **TbTituloDDABaixaPessoa**: Armazena dados do portador/pagador da baixa

**Relacionamentos:**
```
TbTituloDDA (1) ----< (N) TbTituloDDABaixaOperacional
                              |
                              +----(1:1)---- TbTituloDDABaixaReferencia
                              |
                              +----(1:1)---- TbTituloDDABaixaPagamento
                              |
                              +----(1:1)---- TbTituloDDABaixaPessoa
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | SELECT | Consulta título DDA pelo número de identificação para obter código e valor |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTituloDDA | Tabela | UPDATE | Atualiza saldo, quantidade de pagamentos parciais, situação do título e participante destinatário |
| TbTituloDDABaixaOperacional | Tabela | INSERT | Insere registro da baixa operacional com valores, datas e códigos |
| TbTituloDDABaixaReferencia | Tabela | INSERT | Insere referência da baixa operacional |
| TbTituloDDABaixaPagamento | Tabela | INSERT | Insere informações de meio e canal de pagamento da baixa |
| TbTituloDDABaixaPessoa | Tabela | INSERT | Insere dados do portador/pagador da baixa operacional |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| AvisarBaixaOperacionalDAOImpl-sql.xml | Leitura | AvisarBaixaOperacionalDAOImpl | Arquivo XML contendo as queries SQL utilizadas pelo DAO |
| errorMessages.properties | Leitura | commons/resources | Arquivo de propriedades com mensagens de erro do sistema |
| roles.properties | Leitura | commons/resources | Arquivo de propriedades com definição de roles de segurança |
| DebitoDiretoAutorizadoDDA0108R2Mensagem.xsd | Leitura (build) | domain/resources/XSD | Schema XSD para geração das classes de domínio via JAXB |
| log4j2.xml | Leitura | Diversos módulos (test) | Configuração de logging para ambiente de testes |

---

## 10. Filas Lidas

- **queue/PGFTBaixaOperTituloClienteDdaCipQueue**: Fila JMS de onde o sistema consome mensagens XML contendo avisos de baixa operacional de títulos DDA provenientes da CIP. A fila é configurada através do activation spec `as/PGFTBaixaOperTituloClienteDdaCipAS` no WebSphere.

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| CIP (Câmara Interbancária de Pagamentos) | Mensageria JMS | Recebe mensagens de baixa operacional de títulos DDA através de fila JMS |
| Banco de Dados SQL Server (DBPGF_TES) | JDBC | Acesso ao banco de dados para consulta e atualização de títulos e baixas operacionais via DataSource `jdbc/PgftCobrancaDDADS` |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura modular bem organizada (separação em módulos business, domain, persistence, jms, integration)
- Uso adequado de padrões Java EE (EJB, MDB, CDI)
- Implementação de segurança com roles declarativas
- Uso de Spring JDBC para acesso a dados de forma estruturada
- Separação de queries SQL em arquivo XML externo
- Tratamento de exceções com logging detalhado
- Uso de transações declarativas

**Pontos Negativos:**
- **Logging excessivo e mal estruturado**: Muitos logs de debug em produção, impressão de objetos completos, concatenação de strings em logs
- **Tratamento de exceções genérico**: Captura de `Exception` genérica em vários pontos, dificultando diagnóstico
- **Código comentado**: Presença de código comentado (ex: stored procedure não utilizada, módulo RS comentado)
- **Falta de validações**: Não há validação consistente dos dados de entrada antes do processamento
- **Acoplamento**: Classe `AvisarBaixaOperacionalBean` imprime todos os campos do título via reflection, o que é desnecessário e impacta performance
- **Nomenclatura inconsistente**: Mistura de português e inglês, abreviações não padronizadas
- **Testes unitários incompletos**: Testes com código comentado e cobertura limitada
- **Falta de documentação**: Ausência de JavaDoc nas classes e métodos principais
- **Hardcoded values**: Login do sistema hardcoded como constante

---

## 14. Observações Relevantes

1. **Ambiente de Execução**: O sistema foi projetado especificamente para WebSphere Application Server, utilizando recursos específicos da IBM (ibm-ejb-jar-bnd.xml, ibm-application-bnd.xml).

2. **Segurança**: Toda a aplicação está protegida pela role `intr-middleware`, com autenticação configurada para "ALL_AUTHENTICATED_USERS".

3. **Políticas de Segurança WS-Security**: Embora o módulo não exponha web services, há configuração de políticas de segurança (BvWsSecurityUsernameToken, BvWsSecurityCertificate) preparadas para diferentes níveis de classificação (Low, Medium, High).

4. **Classloader**: A aplicação utiliza classloader com política PARENT_LAST e depende de bibliotecas compartilhadas (`arqt-base-lib-1.0`, `fjee-base-lib-1.1`).

5. **Versionamento**: Versão atual do sistema é 0.2.0, indicando que ainda está em fase de desenvolvimento/estabilização.

6. **Stored Procedure Não Utilizada**: Existe uma classe `AvisarBaixaOperacionalStoreProcedure` que não é utilizada na implementação atual, sugerindo que houve mudança de abordagem durante o desenvolvimento (de stored procedure para queries SQL diretas).

7. **Módulo RS Desabilitado**: O módulo REST (rs) está comentado no EAR, indicando que não está em uso na versão atual.

8. **Dependências de Teste**: O projeto utiliza Spring Framework apenas em escopo de teste, não em runtime.

9. **Geração de Código**: As classes de domínio são geradas automaticamente via plugin JAXB a partir do XSD, com customizações de binding para conversão de datas.

10. **Retry Mechanism**: O sistema conta com mecanismo de retry automático do JMS (via JMSXDeliveryCount), mas não há configuração explícita de DLQ (Dead Letter Queue) visível no código fornecido.