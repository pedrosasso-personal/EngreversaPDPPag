## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de BaixaDebitoAuto" é um microserviço que realiza a baixa de débitos automáticos para contas correntes. Ele integra-se com o Kafka para consumir eventos de débito automático efetivado e utiliza o banco de dados para registrar e consultar informações relacionadas aos débitos.

### 2. Principais Classes e Responsabilidades
- **BaixaDebitoAutoConfiguration**: Configurações de beans para o sistema, incluindo FeatureToggle e Jdbi.
- **OpenApiConfiguration**: Configuração do Swagger para documentação de APIs.
- **RetornoDebitoAutomaticoEnum**: Enumeração para retorno de débitos automáticos.
- **TipoProdutoEnum**: Enumeração para tipos de produtos.
- **ContaConvenioRowMapper**: Mapeia resultados de consultas SQL para objetos `ConsultaContaConvenio`.
- **FluxoOnlineRowMapper**: Mapeia resultados de consultas SQL para objetos `FluxoOnline`.
- **RegistroDebitoRowMapper**: Mapeia resultados de consultas SQL para objetos `RegistroDebito`.
- **BaixaDebitoAutoRepositoryImpl**: Implementação do repositório para operações de banco de dados relacionadas a débitos automáticos.
- **DebitoAutomaticoEfetivadoConsumer**: Consumidor Kafka para eventos de débito automático efetivado.
- **AuditEventConsumerInterceptor**: Interceptor para auditoria de eventos consumidos do Kafka.
- **BaixaDebitoAutoMapper**: Mapeia representações de requisição para objetos de domínio.
- **BaixaDebitoAutoController**: Controlador REST para operações de baixa de débito automático.
- **BaixaDebitoAutoV2Controller**: Controlador REST para operações de baixa de débito automático com suporte a fluxo online.
- **ErrorFormat**: Utilitário para formatação de erros em respostas HTTP.
- **Application**: Classe principal para inicialização do Spring Boot.

### 3. Tecnologias Utilizadas
- **Java 11**
- **Spring Boot**
- **Kafka**
- **Avro**
- **Jdbi**
- **Swagger**
- **Sybase**

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v2/credito-pessoal/inserir/log-arquivo | BaixaDebitoAutoV2Controller | Realiza baixa de débito automático no fluxo de baixa online. |
| POST   | /v1/credito-pessoal/inserir/log-arquivo | BaixaDebitoAutoController | Realiza baixa de débito automático. |
| POST   | /v1/financiamento-veiculo/inserir/log-arquivo | BaixaDebitoAutoController | Realiza baixa de débito automático para financiamento de veículo. |

### 5. Principais Regras de Negócio
- Verificação de existência de arquivo de débito temporário antes de gravar novo evento.
- Validação de dados de contrato e parcela antes de processar eventos de débito automático.
- Utilização de FeatureToggle para ativar/desativar funcionalidades de fluxo online.

### 6. Relação entre Entidades
- **BaixaDebitoAuto**: Entidade principal para baixa de débitos automáticos.
- **ConsultaContaConvenio**: Representa informações de conta conveniada.
- **FluxoOnline**: Indica se o fluxo é online ou offline.
- **LogArquivoDebito**: Detalhes do evento de débito automático.
- **RegistroDebito**: Informações de registro de débito.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbContaConvenio | tabela | SELECT | Consulta código de conta conveniada. |
| TbRegistroDebito | tabela | SELECT | Consulta código de registro de débito. |
| tbArquivoDebitoTemp | tabela | SELECT | Verifica existência de arquivo de débito temporário. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbArquivoDebitoTemp | tabela | INSERT | Grava evento de baixa na tabela temporária. |

### 9. Filas Lidas
- **ccbd-base-debito-automatico-efetivado-v2**: Fila Kafka para consumo de eventos de débito automático efetivado.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **Kafka**: Consumo de eventos de débito automático.
- **Swagger**: Documentação de APIs.
- **Sybase**: Banco de dados para operações de débito.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado, utilizando boas práticas de programação como injeção de dependências e separação de responsabilidades. A documentação e os testes são adequados, mas poderiam ser mais detalhados em algumas áreas para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema utiliza FeatureToggle para controle de funcionalidades, permitindo flexibilidade na ativação de recursos.
- A integração com Kafka é central para o processamento de eventos de débito automático.
- O uso de Avro para esquemas de mensagens garante a compatibilidade e a eficiência na serialização de dados.