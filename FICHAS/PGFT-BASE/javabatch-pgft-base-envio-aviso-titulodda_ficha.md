## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um projeto Java que utiliza o framework Spring Batch para realizar o envio de avisos de cobrança de títulos DDA (Débito Direto Autorizado). Ele lê informações de um banco de dados, processa essas informações e envia notificações via e-mail e SMS para os destinatários. O sistema também integra-se com serviços externos para o envio de SMS.

### 2. Principais Classes e Responsabilidades
- **ItemProcessor**: Extende `AbstractItemProcessor` e processa objetos `AvisoVO`.
- **ItemReader**: Extende `AbstractItemReader` e lê objetos `AvisoVO` de uma fonte de dados.
- **ItemWriter**: Extende `AbstractItemWriter` e escreve objetos `AvisoVO`, enviando avisos.
- **MyResumeStrategy**: Implementa `ResumeStrategy` para definir a estratégia de retomada do batch.
- **EnvioAvisoBus**: Gerencia o envio de avisos, incluindo e-mails e SMS, e interage com o DAO para buscar e atualizar dados.
- **EnvioAvisoDAO**: Acessa o banco de dados para buscar e atualizar informações de avisos.
- **AvisoVO**: Classe de valor que representa os dados de um aviso.
- **EmailHelper**: Utiliza `JavaMailSenderImpl` para enviar e-mails.
- **ExitCode**: Enumeração que define códigos de saída para diferentes erros.
- **NotificacaoTechnicalServiceConsumer**: Consome o serviço técnico de notificação para enviar SMS.
- **StubExtended**: Extende `NotificacaoTechnicalServiceStub` para adicionar cabeçalhos SOAP.

### 3. Tecnologias Utilizadas
- Java
- Maven
- Spring Batch
- Spring Framework
- Apache Axis2
- JUnit
- JavaMail

### 4. Principais Endpoints REST
Não se aplica.

### 5. Principais Regras de Negócio
- Envio de avisos por e-mail e SMS para destinatários com títulos DDA pendentes.
- Verificação de pendência de envio de notificações antes de enviar.
- Atualização do status de pendência após o envio bem-sucedido.
- Tratamento de erros específicos para operações de busca e envio de avisos.

### 6. Relação entre Entidades
- **AvisoVO**: Representa um aviso com informações como e-mail, CPF/CNPJ, telefone, título e data de vencimento.
- **EnvioAvisoDAO**: Interage com tabelas de controle de notificações e clientes para buscar e atualizar avisos.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (SELECT/READ) | Breve Descrição |
|-----------------------------|----------------------------|------------------------|-----------------|
| TbTituloDDA                 | tabela                     | SELECT                 | Armazena informações sobre títulos DDA. |
| TbControleNotificacaoTituloDDA | tabela                  | SELECT                 | Armazena o controle de notificações de títulos DDA. |
| TbClienteDDA                | tabela                     | SELECT                 | Armazena informações sobre clientes DDA. |
| VwPessoa                    | view                       | SELECT                 | Armazena informações sobre pessoas. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo (tabela/view/coleção) | Operação (INSERT/UPDATE/DELETE) | Breve Descrição |
|-----------------------------|----------------------------|-------------------------------|-----------------|
| TbControleNotificacaoTituloDDA | tabela                  | UPDATE                        | Atualiza o status de pendência de envio de notificações. |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- **NotificacaoTechnicalService**: Serviço externo para envio de SMS, utilizando Apache Axis2 para comunicação SOAP.

### 12. Avaliação da Qualidade do Código
**Nota:** 7

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como a separação de responsabilidades em diferentes classes e o uso de padrões de projeto. No entanto, há algumas áreas que poderiam ser melhoradas, como a internacionalização de mensagens de erro e a documentação mais detalhada de métodos e classes.

### 13. Observações Relevantes
- O sistema utiliza um conjunto de arquivos WSDL para definir os serviços SOAP de notificação.
- A configuração do sistema é gerenciada por arquivos XML, incluindo definições de jobs e recursos de teste.
- O projeto é dividido em módulos, com um módulo principal para o core e outro para distribuição.