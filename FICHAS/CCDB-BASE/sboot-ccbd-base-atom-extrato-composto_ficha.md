## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é um serviço responsável pelo domínio de negócio de extrato composto, utilizando o modelo de microserviços atômicos. Ele permite a consulta de transações de contas correntes com contraparte do Banco Digital, oferecendo funcionalidades de paginação e integração com o Firestore para armazenamento de dados.

### 2. Principais Classes e Responsabilidades
- **Application**: Classe principal para inicialização do aplicativo Spring Boot.
- **ExtratoCompostoApiDelegateImpl**: Implementa a interface de API para consulta de extratos.
- **ExtratoCompostoService**: Serviço que gerencia operações de consulta e salvamento de extratos compostos.
- **ConsultarExtratoRepositoryImpl**: Implementação de repositório para consulta de extratos no Firestore.
- **ExtratoCompostoMapper**: Interface de mapeamento entre entidades de domínio e representações.
- **ListenerTransacoesContaCorrente**: Componente que escuta mensagens do Pub/Sub e processa transações de conta corrente.
- **FirestoreConfiguration**: Configuração do Firestore para acesso à coleção de extratos compostos.
- **PubSubConfiguration**: Configuração para integração com o Google Cloud Pub/Sub.
- **GeradorHash**: Utilitário para geração de hashes SHA-256 e codificação Base64.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Google Cloud Firestore
- Google Cloud Pub/Sub
- Maven
- Docker

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET    | /v1/extrato | ExtratoCompostoApiDelegateImpl | Consulta de transações de contas correntes com paginação. |

### 5. Principais Regras de Negócio
- Validação de parâmetros de entrada para consulta de extratos.
- Paginação de resultados de consulta.
- Salvamento de informações de transação somente se os detalhes estiverem completos.
- Geração de hash para identificação única de extratos compostos.

### 6. Relação entre Entidades
- **ExtratoComposto**: Entidade principal que contém identificador, transação, detalhes da transação e categoria.
- **Transacao**: Detalhes da operação financeira realizada.
- **DetalhesTransacao**: Informações adicionais sobre a transação, incluindo remetente e favorecido.
- **Categoria**: Classificação da transação.
- **Identificador**: Identificação única da transação.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| extrato-composto            | coleção | READ    | Coleção no Firestore para armazenar extratos compostos. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| extrato-composto            | coleção | INSERT/UPDATE | Coleção no Firestore para armazenar e atualizar extratos compostos. |

### 9. Filas Lidas
- **business-ccbd-base-extrato-composto-sub**: Fila do Google Cloud Pub/Sub para consumo de mensagens relacionadas a transações de conta corrente.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Google Cloud Firestore: Utilizado para armazenamento de dados de extratos compostos.
- Google Cloud Pub/Sub: Utilizado para processamento de mensagens de transações de conta corrente.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e utiliza boas práticas de programação, como injeção de dependências e uso de anotações do Spring. A documentação é clara e o uso de tecnologias modernas como Firestore e Pub/Sub é bem integrado. No entanto, poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza o padrão de microserviços atômicos, facilitando a escalabilidade e manutenção.
- A configuração do sistema é feita através de arquivos YAML, permitindo fácil adaptação a diferentes ambientes.
- O uso de Docker facilita a implantação e execução do serviço em ambientes controlados.