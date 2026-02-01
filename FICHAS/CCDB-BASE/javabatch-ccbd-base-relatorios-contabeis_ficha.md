## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um projeto Java que utiliza o framework Spring Batch para gerar relatórios contábeis. Ele lê dados de um banco de dados, processa essas informações e escreve os resultados em arquivos XLSX. O sistema é configurado para diferentes ambientes (DES, PRD, UAT) e utiliza scripts de execução em batch para automatizar o processo.

### 2. Principais Classes e Responsabilidades
- **AbstractPagingItemReader**: Classe abstrata que implementa a leitura paginada de itens.
- **ItemProcessor**: Processa os itens do tipo `RelatorioContabil`.
- **ItemReader**: Lê os dados do banco de dados e inicializa o filtro de relatório contábil.
- **ItemWriter**: Escreve os dados processados em arquivos XLSX.
- **MyResumeStrategy**: Implementa a estratégia de retomada de execução de jobs.
- **BancoEnum**: Enumeração que representa bancos com seus códigos internos e de compensação.
- **MaioresSaldo**: Representa o saldo de uma pessoa em diferentes contas bancárias.
- **MovAnalitico**: Representa transações analíticas de contas bancárias.
- **RelatorioContabil**: Classe abstrata para geração de relatórios contábeis.
- **RelatorioContabilFiltro**: Filtro para consultas de relatórios contábeis.
- **RelatorioContabilParaMaioresSaldos**: Implementação de `RelatorioContabil` para maiores saldos.
- **RelatorioContabilParaMovAnaliticas**: Implementação de `RelatorioContabil` para movimentações analíticas.
- **ListaMaioresSaldosMapper**: Mapeia resultados de consulta para objetos `MaioresSaldo`.
- **ListaMovAnaliticoMapper**: Mapeia resultados de consulta para objetos `MovAnalitico`.
- **MovimentacaoMapper**: Mapeia objetos para linhas de arquivo XLSX.
- **RelatorioContabilRepositoryImpl**: Implementação do repositório para consultas de relatórios contábeis.
- **Queries**: Contém as consultas SQL utilizadas pelo sistema.
- **ConstantsUtils**: Define constantes de erro para o sistema.
- **DateUtils**: Utilitário para manipulação de datas.

### 3. Tecnologias Utilizadas
- Java
- Spring Batch
- Apache POI
- JUnit
- Mockito
- Sybase JDBC Driver
- Maven

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Geração de relatórios contábeis com base em movimentações bancárias.
- Processamento de dados para identificar maiores saldos e movimentações analíticas.
- Escrita de dados processados em arquivos XLSX.
- Configuração de parâmetros de execução para diferentes ambientes.

### 6. Relação entre Entidades
- `RelatorioContabil` é uma classe abstrata que possui implementações específicas para diferentes tipos de relatórios (`RelatorioContabilParaMaioresSaldos`, `RelatorioContabilParaMovAnaliticas`).
- `RelatorioContabilFiltro` é utilizado para definir critérios de consulta.
- `MaioresSaldo` e `MovAnalitico` são entidades que representam dados de saldo e movimentações, respectivamente.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbConta                     | tabela                     | SELECT                 | Contém informações de contas correntes. |
| TbHistoricoSaldo            | tabela                     | SELECT                 | Armazena histórico de saldos. |
| TbModalidadeConta           | tabela                     | SELECT                 | Detalhes sobre modalidades de conta. |
| TbPessoaTitularidade        | tabela                     | SELECT                 | Informações de titularidade de contas. |
| TbPessoa                    | tabela                     | SELECT                 | Dados de pessoas. |
| TbBanco                     | tabela                     | SELECT                 | Informações sobre bancos. |
| TbHistoricoMovimento        | tabela                     | SELECT                 | Histórico de movimentações. |
| TbMovimentoDia              | tabela                     | SELECT                 | Movimentações diárias. |

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Banco de dados Sybase para leitura de dados de contas e movimentações.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, com uso adequado de padrões de projeto e boas práticas de programação. A utilização de Spring Batch facilita o processamento de grandes volumes de dados. No entanto, a documentação poderia ser mais detalhada em algumas áreas para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza diferentes configurações de ambiente (DES, PRD, UAT) para conexão com o banco de dados.
- Scripts em batch (.bat e .sh) são utilizados para automatizar a execução dos jobs.
- A configuração de logs é feita através de arquivos log4j.xml.