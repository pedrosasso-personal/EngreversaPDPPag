# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-agenda-pagamento** é um componente Java EE responsável pelo agendamento de pagamentos no contexto do sistema SPAG (Sistema de Pagamentos). Ele recebe solicitações de agendamento de diversos tipos de transações financeiras (TED, DOC, Boletos, Transferências, Tributos, Concessionárias), valida as informações, persiste os dados de agendamento em banco de dados e controla o status dos lançamentos. O sistema verifica se o pagamento deve ser agendado com base na data informada, trata situações de saldo insuficiente considerando horários limites específicos por tipo de transação, e mantém o histórico de agendamentos e favorecidos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **AgendaPagamentoBean** | EJB Stateless que orquestra o processo de agendamento, validando datas, verificando saldo, inserindo/atualizando agendamentos e tratando exceções |
| **AgendaPagamentoServiceImpl** | Implementação do serviço de negócio que converte objetos de domínio, valida se pagamento deve ser agendado, e coordena operações de persistência |
| **AgendamentoPagamentoDAOImpl** | DAO responsável por operações de banco de dados relacionadas a agendamentos (inserção, atualização, consulta de existência) |
| **AgendamentoFavorecidoDAOImpl** | DAO responsável por persistir informações dos favorecidos associados aos agendamentos |
| **AgendaPagamento (REST)** | Endpoint REST que expõe a funcionalidade de agendamento via API JSON |
| **AgendamentoPagamentoDTO** | DTO que representa a entidade de agendamento de pagamento com todos os atributos necessários |
| **AgendamentoFavorecidoDTO** | DTO que representa os favorecidos de um agendamento (suporta múltiplos favorecidos) |
| **Util** | Classe utilitária com métodos de conversão de tipos, manipulação de datas e tratamento de valores nulos |

---

## 3. Tecnologias Utilizadas

- **Java EE 7** (EJB 3.1, CDI, JAX-RS, JAX-WS)
- **IBM WebSphere Application Server** (runtime)
- **Maven** (gerenciamento de dependências e build)
- **Spring JDBC** (acesso a dados via JDBC Template)
- **Gson** (serialização/deserialização JSON)
- **Apache Commons Lang3** (utilitários)
- **Joda-Time** (manipulação de datas)
- **SLF4J/Log4j2** (logging)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **Swagger/OpenAPI** (documentação de APIs REST)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/agendaPagamento/ | AgendaPagamento | Recebe solicitação de agendamento de pagamento em formato JSON e retorna o resultado do processamento |

---

## 5. Principais Regras de Negócio

1. **Validação de Data de Agendamento**: Pagamentos só são agendados se a data for futura ou igual à data atual
2. **Horários Limites por Tipo**: 
   - Tributos e Concessionárias: limite até 14:45
   - Demais tipos (Boleto, TED, DOC, etc): limite até 15:30
3. **Tratamento de Saldo Insuficiente**: Se o saldo for insuficiente e o horário atual ultrapassar o limite do tipo de transação, gera ocorrência de erro e cancela o agendamento
4. **Antecipação de Pagamento**: Sistema suporta flag de antecipação de pagamento
5. **Mesma Titularidade**: Identifica se remetente e favorecido são a mesma pessoa
6. **Múltiplos Favorecidos**: Suporta até 2 favorecidos por agendamento
7. **Atualização de Status**: Atualiza status do lançamento na tabela TbLancamento (10=Agendado, 99=Erro)
8. **Verificação de Duplicidade**: Verifica se já existe agendamento para o mesmo lançamento, data e tipo de transação
9. **Conversão de Tipos de Liquidação**: Mapeia códigos ITP para tipos de agendamento (CC, DOC, TED, Boleto, etc)

---

## 6. Relação entre Entidades

**AgendamentoPagamento** (1) -----> (N) **AgendamentoFavorecido**

- Um agendamento de pagamento pode ter múltiplos favorecidos (até 2)
- Relacionamento através do campo `CdAgendamentoPagamento`
- AgendamentoPagamento contém dados da transação, valores, datas, contas origem/destino
- AgendamentoFavorecido contém dados dos beneficiários (nome, CPF/CNPJ, ordem de titularidade)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamentoPagamento | tabela | SELECT | Consulta existência de agendamento por data, tipo e código de lançamento |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbAgendamentoPagamento | tabela | INSERT | Insere novo registro de agendamento de pagamento |
| TbAgendamentoPagamento | tabela | UPDATE | Atualiza status e data de alteração de agendamento existente |
| TbAgendamentoFavorecido | tabela | INSERT | Insere registros de favorecidos associados ao agendamento |
| TbLancamento | tabela | UPDATE | Atualiza status do lançamento (10=Agendado, 99=Erro) |

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
| java-spag-base-pagamentos-commons | Biblioteca | Utiliza classes de domínio compartilhadas (DicionarioPagamento, OcorrenciaDTO, enums) |
| Banco de Dados Oracle/SQL Server | JDBC | Acesso direto via Spring JDBC Template para persistência de agendamentos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, domain, commons)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Implementação de testes unitários com boa cobertura
- Uso de DTOs para transferência de dados
- Logging adequado com SLF4J
- Tratamento de exceções estruturado

**Pontos de Melhoria:**
- Presença de "magic numbers" e strings hardcoded (ex: "nova_esteira", status 10 e 99)
- Métodos muito longos com múltiplas responsabilidades (ex: `convertDicionarioToAgendamento`)
- Falta de constantes para valores repetidos
- Comentários em português misturados com código
- Uso de `StringUtils.left()` para truncar strings poderia ser melhor documentado
- Tratamento genérico de exceções em alguns pontos
- Dependência forte de classes de bibliotecas externas (DicionarioPagamento)
- Código de teste com alguns métodos vazios ou incompletos

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está bem estruturado em módulos Maven (business, commons, domain, persistence, integration, jms, ws, rs, ear)

2. **Deployment**: Aplicação empacotada como EAR para deploy em WebSphere Application Server

3. **Segurança**: Utiliza roles de segurança Java EE ("spag-integracao", "intr-middleware") e autenticação BASIC

4. **Horário de Verão**: Código possui tratamento específico para horário de verão brasileiro

5. **Datasource JNDI**: Utiliza datasource `jdbc/spagBaseDBSPAGDS` configurado no servidor

6. **Versionamento**: Projeto na versão 0.16.0, indicando estar em desenvolvimento/evolução

7. **Pipeline CI/CD**: Possui arquivo `jenkins.properties` configurado para integração contínua

8. **Documentação API**: Configurado Swagger para documentação automática dos endpoints REST

9. **Compatibilidade**: Código compilado para Java 1.7, indicando necessidade de compatibilidade com versões antigas

10. **Queries Externalizadas**: SQLs mantidos em arquivos XML separados, facilitando manutenção