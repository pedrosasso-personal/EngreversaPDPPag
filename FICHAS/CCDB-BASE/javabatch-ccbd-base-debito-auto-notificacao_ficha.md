# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por processar notificações de vencimento de débito automático. O sistema consulta lançamentos agendados no banco de dados MySQL (tabela `TbPagamentoDebitoAutomatico`) com vencimento em D+1, D+4 e D+7, e publica mensagens em filas RabbitMQ para notificar clientes sobre os vencimentos próximos. O processamento diferencia produtos de crédito pessoal/fácil (tipos 3 e 4) dos demais produtos (cartão e financiamento), direcionando para filas distintas.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ItemReader` | Lê lançamentos agendados do banco de dados para as datas D+1, D+4 e D+7 |
| `ItemProcessor` | Processa os lançamentos (atualmente apenas repassa os dados) |
| `ItemWriter` | Publica mensagens JSON nas filas RabbitMQ apropriadas conforme tipo de produto |
| `NotificacaoRepository` / `NotificacaoRepositoryImpl` | Acesso aos dados de lançamentos no banco MySQL |
| `NotificacaoMapper` | Mapeia ResultSet do banco para objetos `Lancamento` |
| `MyResumeStrategy` | Estratégia de retomada do job em caso de falha |
| `Lancamento` | Value Object representando um lançamento de débito automático |
| `Dados` | Value Object com dados detalhados do lançamento |
| `NotificacaoUtil` | Utilitários para cálculo de datas e leitura de queries SQL |
| `ExitCodeEnum` | Enumeração dos códigos de saída do batch |
| `ProdutoEnum` | Enumeração dos tipos de produto (Cartão, Financiamento, Crédito Pessoal, Crédito Fácil) |

---

## 3. Tecnologias Utilizadas

- **Java** com **Maven** para gerenciamento de dependências
- **Spring Framework** (configuração XML) para injeção de dependências
- **Spring Batch** (framework BV customizado: `bv-framework-batch`)
- **MySQL 8.0.22** como banco de dados
- **RabbitMQ** via Spring AMQP para mensageria
- **Bitronix** para gerenciamento de transações XA
- **Jackson 2.12.7** para serialização JSON
- **Log4j** para logging
- **JUnit** para testes
- **BV Crypto** para criptografia de senhas

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch sem endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Seleção de Lançamentos**: Busca lançamentos com vencimento em D+1, D+4 e D+7 dias úteis
2. **Filtro por Status**: Apenas lançamentos com status = 1 (agendado) são processados
3. **Diferenciação por Produto**: 
   - Produtos tipo 3 (Crédito Pessoal) e 4 (Crédito Fácil) são enviados para fila específica de notificação CP
   - Produtos tipo 1 (Cartão) e 2 (Financiamento) são enviados para fila padrão de débito automático
4. **Validação de Data**: Sistema valida se a data de vencimento é dia útil
5. **Notificação Antecipada**: Para produtos CP/CF, notificações são enviadas com 4 e 7 dias de antecedência
6. **Tratamento de Erros**: Códigos de saída específicos para diferentes tipos de erro (10, 20, 30)

---

## 6. Relação entre Entidades

**Entidades principais:**

- **Lancamento**: Entidade principal contendo canal, tipo de produto e dados do lançamento
  - Relacionamento 1:1 com **Dados**
  
- **Dados**: Contém informações detalhadas do lançamento (CPF/CNPJ, ID, NSU, data vencimento, valor)

**Relacionamento no banco de dados:**
- `TbPagamentoDebitoAutomatico` (pagamento) → `TbPessoaDebitoAutomatico` (pessoa)
- `TbPagamentoDebitoAutomatico` (pagamento) → `TbConvenioDebitoAutomatico` (convênio)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbPagamentoDebitoAutomatico | Tabela | SELECT | Tabela principal de pagamentos agendados via débito automático |
| TbPessoaDebitoAutomatico | Tabela | SELECT | Tabela de pessoas/clientes vinculadas aos pagamentos |
| TbConvenioDebitoAutomatico | Tabela | SELECT | Tabela de convênios/produtos de débito automático |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas lê dados do banco, não realiza operações de INSERT/UPDATE/DELETE.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| NotificacaoRepositoryImpl-sql.xml | Leitura | NotificacaoUtil.getSqlFromFile() | Arquivo XML contendo queries SQL parametrizadas |
| log/statistics-${executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas de execução do batch |
| log/robo.log | Gravação | RollingFileAppender | Log geral da aplicação (ambiente produção) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Routing Key | Breve Descrição |
|----------------------|-------------|-----------------|
| ex.ccbd.debito.automatico | notificacao.vencimento | Fila para notificações de vencimento de produtos Cartão e Financiamento |
| ex.ccbd.notificacao.vencimentoDebitoAutomatico | noticacaoVencimentoDebitoAutomatico | Fila para notificações de vencimento de produtos Crédito Pessoal e Crédito Fácil |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Breve Descrição |
|-----------------|------|-----------------|
| MySQL CCBDDebitoAutomatico | Banco de Dados | Base de dados de débito automático (ambientes DES/UAT/PRD) |
| RabbitMQ | Mensageria | Broker de mensagens para publicação de notificações (hosts diferentes por ambiente) |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrão batch (Reader/Processor/Writer)
- Uso adequado de enums para códigos de saída e tipos de produto
- Separação de responsabilidades entre camadas (repository, mapper, batch)
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Uso de logging apropriado

**Pontos Negativos:**
- **ItemProcessor vazio**: não realiza nenhum processamento, apenas repassa dados
- **Hardcoded values**: exchanges e routing keys fixos no código
- **Falta de tratamento de exceções específico**: exceções genéricas em vários pontos
- **Comentários em português com caracteres especiais mal codificados**: "N�O ALTERAR", "�tiL"
- **Senha em texto claro** no arquivo de configuração local (job-resources.xml)
- **Falta de validações**: não valida se mensagem foi realmente publicada com sucesso
- **Código de teste básico**: teste de integração muito simples, sem asserções relevantes
- **Mistura de responsabilidades**: ItemWriter decide para qual fila enviar baseado em tipo de produto
- **Falta de documentação**: ausência de JavaDoc nas classes
- **Uso de framework legado**: dependência de framework BV customizado pode dificultar manutenção

---

## 14. Observações Relevantes

1. **Ambientes**: Sistema possui configurações específicas para DES, UAT e PRD com diferentes hosts MySQL e RabbitMQ
2. **Criptografia**: Senhas de banco são criptografadas usando BVCrypto em ambientes não-locais
3. **Dias úteis**: Sistema considera apenas dias úteis para notificações, mas a validação não está explícita no código fornecido
4. **Múltiplas notificações**: Um mesmo lançamento pode gerar até 3 notificações (D+1, D+4, D+7) dependendo do tipo de produto
5. **Transações**: Sistema configurado com `noTransactionJobTemplate`, indicando processamento sem controle transacional
6. **Estratégia de retomada**: Implementa `ResumeStrategy` que permite retomar job apenas se exitCode = 0
7. **Versionamento**: Projeto na versão 0.7.0, indicando ainda em fase de desenvolvimento/estabilização
8. **Deploy**: Propriedade `disableQADeploy=true` indica que deploy em QA está desabilitado