## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação batch desenvolvida em Java utilizando o framework Spring Batch. Seu objetivo é realizar a conciliação de transações de arquivos TIF, processando dados de entrada e inserindo registros conciliados em um banco de dados SQL Server.

### 2. Principais Classes e Responsabilidades
- **SpringBatchApplication**: Classe principal que inicia a aplicação Spring Batch.
- **BatchConfiguration**: Configura o job de processamento batch.
- **StepConfiguration**: Define o passo de processamento, incluindo leitura, processamento e escrita de dados.
- **ReadersConfiguration**: Configura o leitor de dados do banco de dados.
- **WritersConfiguration**: Configura o escritor de dados para o banco de dados.
- **ConciliacaoProcessor**: Processa cada item de entrada, convertendo-o para o formato necessário para inserção.
- **ConciliacaoWriter**: Escreve os dados processados no banco de dados.
- **ConciliacaoTifInsertConverter**: Converte objetos de domínio para o formato de inserção.
- **ConciliacaoArquivoTifMapper**: Mapeia resultados de consultas SQL para objetos de domínio.
- **DateUtil**: Utilitário para manipulação de datas.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Batch
- Spring Boot
- SQL Server
- Docker
- Prometheus
- Grafana
- Maven

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Conciliação de transações de arquivos TIF.
- Processamento de dados de entrada e inserção de registros conciliados no banco de dados.
- Verificação de integridade e preenchimento de campos nulos durante o processamento.

### 6. Relação entre Entidades
- **ConciliacaoArquivoTif**: Entidade de domínio representando os dados de conciliação de arquivos TIF.
- **ConciliacaoTifInsert**: Entidade de domínio para inserção de dados conciliados.
- **TrnsoPayload**: Dados adicionais associados a uma transação, encapsulados dentro de ConciliacaoArquivoTif.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConciliacaoTransacao      | tabela | SELECT | Tabela de transações para conciliação. |
| TbComplementoConciliacaoTrnso | tabela | SELECT | Tabela de complementos de conciliação. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbConciliacaoTransacaoDebito | tabela | INSERT | Tabela onde são inseridos os dados conciliados. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Banco de dados SQL Server para leitura e escrita de dados.
- Prometheus e Grafana para monitoramento de métricas.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de padrões de projeto. A documentação e os testes são adequados, mas poderia haver uma melhor descrição dos objetivos do projeto no README.

### 13. Observações Relevantes
- A aplicação utiliza Docker para facilitar o deploy e execução de serviços como Prometheus e Grafana.
- O projeto possui integração com Jenkins para automação de builds e deploys.
- A configuração de segurança está desativada, conforme indicado no arquivo `application.yml`.