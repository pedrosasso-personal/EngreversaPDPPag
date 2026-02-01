## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Verificar Condições de Débito" é um serviço atômico desenvolvido em Java utilizando o framework Spring Boot. Ele tem como objetivo consultar e atualizar informações relacionadas a transações de débito, verificando condições específicas e interagindo com um banco de dados SQL Server.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal que inicia a aplicação Spring Boot.
- **DataBaseConfiguration**: Configura o Jdbi para interagir com o banco de dados.
- **VerificarCondicoesDebitoConfiguration**: Configura os beans necessários para o funcionamento do serviço de verificação de condições de débito.
- **CheckList**: Representa um checklist de transações de cartão de débito.
- **ConsultaInfoTransacaoCompleta**: Contém informações completas sobre uma transação de cartão de débito.
- **ConsultarCondicoesResponse**: Representa a resposta da consulta de condições de débito.
- **ValidatorException**: Exceção lançada durante a validação de dados.
- **CCBDRepositoryImpl**: Implementação do repositório para acesso ao banco de dados.
- **CheckListMapper**: Mapeia objetos de requisição para objetos de domínio.
- **VerificarCondicoesDebitoMapper**: Mapeia respostas de consulta para representações de resposta.
- **VerificarCondicoesDebitoController**: Controlador REST que expõe endpoints para consulta e atualização de condições de débito.
- **VerificarCondicoesDebitoServiceImpl**: Implementação do serviço que contém a lógica de negócio para verificação de condições de débito.
- **VerificarCondicoesDebitoValidator**: Valida dados de entrada para as operações de verificação de condições de débito.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- SQL Server
- Swagger para documentação de API
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/verificar-condicoes-debito/consultar | VerificarCondicoesDebitoController | Consulta condições de débito por NSU ou identificador de transação. |
| GET    | /v1/verificar-condicoes-debito/visa-consultar | VerificarCondicoesDebitoController | Consulta condições de débito Visa por autorizador, data, valor, número de conta e tipo de transação. |
| PUT    | /v1/update-check-list | VerificarCondicoesDebitoController | Atualiza o checklist notificando a chegada de arquivos. |
| GET    | /v1/consulta/transacao | VerificarCondicoesDebitoController | Consulta transações completas por número de conta e outros parâmetros. |

### 5. Principais Regras de Negócio
- Validação de entrada para consultas de condições de débito.
- Consulta de condições de débito por NSU ou identificador de transação.
- Filtragem de transações Visa por autorizador.
- Atualização de checklist de transações de débito.

### 6. Relação entre Entidades
- **CheckList** e **ConsultaInfoTransacaoCompleta**: Ambas as entidades representam informações sobre transações de débito, com o CheckList focando em estados de recebimento e a ConsultaInfoTransacaoCompleta em detalhes da transação.
- **ConsultarCondicoesResponse**: Utilizada para retornar informações de condições de débito consultadas.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbControleTransacaoCartao   | tabela | SELECT | Armazena informações sobre transações de cartão de débito. |
| TbCheckListTransacaoArquivo | tabela | SELECT | Armazena o checklist de transações de arquivo. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbCheckListTransacaoArquivo | tabela | UPDATE | Atualiza o checklist de transações de arquivo. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com SQL Server para operações de leitura e atualização de dados de transações de débito.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de interfaces para abstração. A documentação via Swagger é um ponto positivo. No entanto, algumas áreas poderiam ter comentários mais detalhados para facilitar a compreensão de lógica complexa.

### 13. Observações Relevantes
- O sistema utiliza Docker para facilitar a implantação e execução em ambientes controlados.
- A configuração de segurança JWT está presente para proteger os endpoints expostos.
- A documentação do Swagger facilita a interação com os endpoints REST.