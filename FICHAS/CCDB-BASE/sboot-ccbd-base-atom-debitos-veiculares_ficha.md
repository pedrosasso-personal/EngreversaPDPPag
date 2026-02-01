## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço atômico de débitos veiculares, desenvolvido para gerenciar transações relacionadas a débitos de veículos, como IPVA, DPVAT, multas, licenciamento e RENAINF. Ele permite a consulta, gravação e atualização de débitos, além de gerar extratos e recibos de transações. O sistema utiliza o framework Spring Boot e está configurado para operar com um banco de dados MySQL.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **ConsultaDebitosServiceImpl**: Implementa a lógica de consulta de débitos veiculares, como DPVAT, IPVA, multas, RENAINF e licenciamento.
- **DebitosVeicularesServiceImpl**: Gerencia a gravação de débitos veiculares e a verificação de veículos.
- **ExtratoServiceImpl**: Responsável por inserir extratos de pagamentos.
- **PagamentoDebitoServiceImpl**: Gerencia a lógica de novos pagamentos de débitos veiculares e atualizações de transações.
- **TransacaoServiceImpl**: Implementa a lógica de consulta de transações por etapas, tanto de forma sintética quanto analítica.
- **DebitosVeicularesController**: Controlador REST que expõe endpoints para operações de débitos veiculares.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- JDBI
- MySQL
- Swagger
- MapStruct
- Lombok

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/transacao | DebitosVeicularesController | Nova transação de débitos veiculares. |
| POST | /v1/pagamento-debito | DebitosVeicularesController | Nova transação de pagamento de débitos veiculares. |
| GET | /v1/pagamento-debito/total | DebitosVeicularesController | Consultar total de pagamento de débitos veiculares. |
| GET | /v1/debito/ipva | DebitosVeicularesController | Consultar débito do tipo IPVA. |
| GET | /v1/debito/dpvat | DebitosVeicularesController | Consultar débito do tipo DPVAT. |
| GET | /v1/debito/multa | DebitosVeicularesController | Consultar débitos do tipo multa. |
| GET | /v1/debito/renainf | DebitosVeicularesController | Consultar débitos do tipo RENAINF. |
| GET | /v1/debito/licenciamento | DebitosVeicularesController | Consultar débitos do tipo licenciamento. |
| POST | /v1/atualizacao-transacao | DebitosVeicularesController | Atualizar status de transação de débitos veiculares. |
| POST | /v1/extrato | DebitosVeicularesController | Inserir extrato de pagamentos. |
| GET | /v1/veiculo | DebitosVeicularesController | Consulta de informações do veículo. |
| GET | /v1/monitor/etapas/sintetico | DebitosVeicularesController | Consultar transações segregadas por etapas (sintético). |
| GET | /v1/monitor/etapas/analitico | DebitosVeicularesController | Consultar transações segregadas por etapas (analítico). |
| POST | /v1/recibos | DebitosVeicularesController | Salvar recibos de débitos veiculares. |
| POST | /v1/erroPagamento | DebitosVeicularesController | Inserir erros de pagamentos do Banco Rendimento. |

### 5. Principais Regras de Negócio
- Verificação de existência de veículo antes de gravar débitos.
- Gravação de débitos veiculares por tipo (IPVA, DPVAT, multas, etc.).
- Atualização de transações de pagamento com base no status.
- Inserção de extratos de pagamentos apenas se não houver registros para a data atual.
- Tratamento de exceções específicas para consultas de veículos não encontrados.

### 6. Relação entre Entidades
- **Veiculo**: Entidade que representa um veículo, incluindo informações como placa, renavam, proprietário, etc.
- **DebitosVeiculares**: Agrega débitos de diferentes tipos associados a um veículo.
- **TransacaoDebitoEntity**: Representa uma transação de débito, incluindo detalhes de pagamento e status.
- **ExtratoDomain**: Representa um extrato de pagamento, incluindo detalhes financeiros e de transações.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbDebitoDpvat | tabela | SELECT | Consulta débitos DPVAT. |
| TbDebitoIPVA | tabela | SELECT | Consulta débitos IPVA. |
| TbDebitoLicenciamento | tabela | SELECT | Consulta débitos de licenciamento. |
| TbDebitoMulta | tabela | SELECT | Consulta débitos de multas. |
| TbDebitoRenainf | tabela | SELECT | Consulta débitos RENAINF. |
| TbVeiculo | tabela | SELECT | Consulta informações de veículos. |
| TbConsultaRenavam | tabela | SELECT | Consulta número de RENAVAM. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbVeiculo | tabela | UPDATE | Atualiza informações de veículos. |
| TbConsultaRenavam | tabela | INSERT | Insere consultas de RENAVAM. |
| TbDebitoDpvat | tabela | INSERT | Insere débitos DPVAT. |
| TbDebitoIPVA | tabela | INSERT | Insere débitos IPVA. |
| TbDebitoLicenciamento | tabela | INSERT | Insere débitos de licenciamento. |
| TbDebitoMulta | tabela | INSERT | Insere débitos de multas. |
| TbDebitoRenainf | tabela | INSERT | Insere débitos RENAINF. |
| TbComprovanteFiscal | tabela | INSERT | Insere recibos fiscais. |
| TbConsultaExtratoPagamento | tabela | INSERT | Insere consultas de extrato de pagamento. |
| TbExtratoPagamento | tabela | INSERT | Insere pagamentos de extrato. |
| TbTransacaoDebito | tabela | UPDATE | Atualiza transações de débito. |
| TbErroPagamentoRendimento | tabela | INSERT | Insere erros de pagamento do Banco Rendimento. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Banco Rendimento: Integração para inserção de erros de pagamento.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de desenvolvimento, como o uso de interfaces para serviços e repositórios, além de seguir o padrão de projeto RESTful. No entanto, algumas áreas poderiam ser melhoradas em termos de documentação e tratamento de exceções.

### 13. Observações Relevantes
- O projeto utiliza o Swagger para documentação de API, facilitando a integração e uso dos endpoints expostos.
- A configuração do banco de dados é feita através de variáveis de ambiente, permitindo flexibilidade em diferentes ambientes de execução.
- O sistema está preparado para ser executado em contêineres Docker, conforme o Dockerfile fornecido.