## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "springboot-sitp-base-gestao-fintech" é um serviço REST desenvolvido em Java utilizando o framework Spring Boot. Ele é projetado para gerenciar operações financeiras relacionadas a fintechs, incluindo cancelamento de transações, consulta de entidades, gestão de pagamentos e recebimentos, entre outros. O sistema também oferece endpoints para integração com serviços externos e utiliza um banco de dados para armazenar e recuperar informações financeiras.

### 2. Principais Classes e Responsabilidades
- **CancelamentoService**: Gerencia o cancelamento de transações financeiras.
- **ContigenciaService**: Lida com operações de contigência, como consulta de filiais e origens.
- **EntidadeService**: Responsável por obter informações de entidades.
- **ISPBService**: Fornece descrições de operações e consulta bancos ativos.
- **RcoService**: Consulta movimentos RCO e bancos ativos na CIP.
- **SITPGestaoFintechService**: Gerencia pagamentos e recebimentos de TEDs e boletos.
- **SumarizacaoDocService**: Lida com a sumarização de documentos de remessa.
- **DocketConfiguration**: Configurações do Swagger para documentação de APIs.
- **Server**: Classe principal para inicializar a aplicação Spring Boot.

### 3. Tecnologias Utilizadas
- Spring Boot
- Gradle
- Swagger
- Sybase JDBC
- Logback
- JUnit
- Mockito
- Jacoco
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /cancelamento/lancamento/transacao | CancelamentoApi | Cancela transações de lançamento. |
| PUT    | /cancelamento/lancamento/status/itp/{status} | CancelamentoApi | Atualiza status de lançamento de caixa entrada SPB. |
| PUT    | /cancelamento/lancamento/status/pgf/{status} | CancelamentoApi | Atualiza status de lançamento PGFTES. |
| GET    | /contigencia/filiais | ContigenciaApi | Consulta filiais ativas. |
| GET    | /entidade | EntidadeApi | Obtém entidades do PGFT. |
| GET    | /ispb/operation-description/{codigo} | ISPBApi | Obtém descrição de operação por código. |
| GET    | /rco/consultaMovimentosRco | RcoApi | Consulta movimentos RCO. |
| POST   | /sitp-gestao-fintech/ted-fintech | SITPGestaoFintechApi | Consulta TEDs efetuadas pelas fintechs. |
| GET    | /sumarizacao-doc | SumarizacaoDocApi | Obtém itens de remessa DOC. |

### 5. Principais Regras de Negócio
- Cancelamento de transações financeiras com atualização de status.
- Consulta de entidades e operações financeiras.
- Gestão de pagamentos e recebimentos de TEDs e boletos.
- Sumarização e conciliação de documentos de remessa.

### 6. Relação entre Entidades
- **LancamentoDTO**: Representa um lançamento financeiro, contendo informações gerais, remetente, favorecido, boleto e complementares.
- **FintechBeneficiario, FintechPagadora, FintechRemetente**: Representam entidades envolvidas em transações financeiras.
- **MovimentoRco**: Representa um movimento RCO com informações de débito/crédito e contra parte.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_TRANSACAO_SPB | tabela | SELECT | Consulta transações de lançamento. |
| TBL_SIST_ORIGEM_SPB | tabela | SELECT | Consulta origens de sistema. |
| TBL_FILIAL_SPB | tabela | SELECT | Consulta filiais ativas. |
| TBL_LANCAMENTO | tabela | SELECT | Consulta lançamentos financeiros. |
| TbBanco | tabela | SELECT | Consulta bancos ativos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TBL_CAIXA_ENTRADA_SPB | tabela | UPDATE | Atualiza status de lançamentos de caixa entrada SPB. |
| TBL_LANCAMENTO | tabela | UPDATE | Atualiza status de lançamentos PGFTES. |
| TbValidacaoOrigemPagamento | tabela | UPDATE/DELETE | Atualiza ou exclui validações de origem de pagamento. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com banco de dados Sybase para operações de consulta e atualização.
- Utilização de APIs REST para comunicação com serviços externos.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como injeção de dependências e uso de padrões de projeto. A documentação via Swagger é um ponto positivo. No entanto, poderia haver uma maior cobertura de testes unitários e integração.

### 13. Observações Relevantes
- O projeto utiliza Docker para facilitar o deployment e execução em ambientes controlados.
- A configuração de segurança é feita através de Spring Security, com suporte a autenticação básica.
- O sistema é configurado para rodar em diferentes ambientes (local, des, qa, uat, prd) através de perfis do Spring.