## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação Angular que serve como referência para a arquitetura SPA (Single Page Application) do Banco BV. Ele utiliza diversas funcionalidades do Angular, como módulos, componentes, serviços e roteamento, além de integrar com APIs externas e suportar renderização no servidor (SSR) e pré-renderização. O sistema também está preparado para ser executado em ambientes Docker.

### 2. Principais Classes e Responsabilidades
- **AppComponent**: Componente principal da aplicação que gerencia a inicialização e configuração de serviços de erro e segurança.
- **ShellComponent**: Gerencia o layout e navegação principal da aplicação.
- **LoginComponent**: Gerencia a tela de login, incluindo autenticação de usuários.
- **ClientesService**: Serviço responsável pelo tratamento de funções relacionadas a clientes, como salvar, listar e excluir.
- **UniversalInterceptor**: Interceptor HTTP para manipulação de requisições e respostas no servidor.
- **PushNotificationsService**: Serviço para gerenciar notificações push via Service Worker.

### 3. Tecnologias Utilizadas
- Angular 7
- Node.js
- Docker
- Jest para testes unitários
- Jasmine para testes de componentes
- Protractor para testes end-to-end
- Angular Material para componentes de UI
- NgRx para gerenciamento de estado
- Universal para SSR
- JSON Server para mock de APIs
- Webpack para bundling

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /api/notifications | PushNotificationsService | Adiciona um usuário à lista de notificações push |
| POST   | /api/pushnotifications | PushNotificationsService | Envia notificações push para usuários |

### 5. Principais Regras de Negócio
- Autenticação de usuários via login.
- Gerenciamento de clientes, incluindo cadastro, edição e exclusão.
- Integração com APIs externas para funcionalidades de backend.
- Suporte a notificações push para interação com usuários.

### 6. Relação entre Entidades
- **ClienteModel**: Representa um cliente com atributos como id, nome, email, estado civil, sexo, data de nascimento e CPF.
- **EstadoCivilModel**: Representa o estado civil de um cliente.
- **IconOptions**: Model para opções de ícones usados em componentes de UI.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| clientes                    | tabela | SELECT | Lista de clientes cadastrados |
| estadoCivil                 | tabela | SELECT | Lista de estados civis disponíveis |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| cliente                     | tabela | INSERT/UPDATE | Cadastro e atualização de informações de clientes |

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- Integração com APIs REST para operações de clientes e notificações.
- Uso de Service Worker para notificações push.
- Configuração de ambiente via arquivos JSON.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, com uso adequado de módulos e componentes do Angular. As práticas de codificação são seguidas, como a separação de responsabilidades e uso de serviços para lógica de negócios. No entanto, a complexidade de algumas partes poderia ser reduzida para melhorar a manutenibilidade.

### 13. Observações Relevantes
- O sistema está configurado para suportar renderização no servidor (SSR) e pré-renderização, o que é útil para SEO e performance.
- O uso de Docker facilita a implantação em diferentes ambientes.
- A aplicação utiliza Angular Material para componentes de UI, proporcionando uma interface moderna e responsiva.