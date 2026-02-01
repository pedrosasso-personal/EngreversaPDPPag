# Ficha Técnica do Sistema

## 1. Descrição Geral

Este é um projeto de aplicação web Angular 7 (versão 7.2.15) desenvolvido como uma aplicação de referência para o Banco BV. Trata-se de uma Single Page Application (SPA) com suporte a Server-Side Rendering (SSR) e Pre-rendering, containerizada com Docker. A aplicação demonstra boas práticas de desenvolvimento, incluindo exemplos de componentes UI/UX, segurança, gerenciamento de estado, e integração com APIs backend. O projeto utiliza a arquitetura de módulos lazy-loaded do Angular e está preparado para Progressive Web App (PWA).

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AppComponent** | Componente raiz da aplicação, gerencia subscrições de erros e eventos de segurança |
| **ShellComponent** | Componente de layout principal, gerencia navegação e estrutura da aplicação |
| **LoginComponent** | Gerencia autenticação de usuários |
| **DashboardComponent** | Página inicial após login |
| **ClientesService** | Serviço para operações CRUD de clientes |
| **ClientesDataSource** | Data source para gerenciamento de dados de clientes em tabelas |
| **BvToolbarComponent** | Barra de ferramentas superior da aplicação |
| **BvNavbarComponent** | Barra de navegação lateral |
| **AppConfigService** | Gerenciamento de configurações da aplicação |
| **AppMetatagsService** | Gerenciamento de metatags para SEO |
| **UniversalInterceptor** | Interceptor HTTP para SSR |
| **PushNotificationsService** | Gerenciamento de notificações push (PWA) |
| **CameraComponent** | Acesso à câmera do dispositivo (PWA) |

## 3. Tecnologias Utilizadas

- **Framework Frontend**: Angular 7.2.15
- **Linguagem**: TypeScript 3.1.6
- **UI Components**: Angular Material 7.1.1
- **Bibliotecas Internas**: @arqt/spa-framework 1.12.0, @arqt/ui 1.5.0
- **State Management**: RxJS 6.3.3
- **Testes**: Jest 23.6.0, Protractor 5.4.0
- **Build Tools**: Angular CLI 7.3.9, Webpack
- **SSR/Pre-rendering**: Angular Universal 7.0.2
- **Server**: Express 4.16.0, Node.js 8+
- **Containerização**: Docker
- **PWA**: @angular/service-worker 7.2.15
- **Segurança**: JSEncrypt 3.0.0-rc.1, crypto-js 3.3.0
- **Estilização**: SCSS, Bootstrap Grid
- **Documentação**: Compodoc 1.1.7
- **Qualidade de Código**: TSLint 5.11.0, Codelyzer 4.5.0, SonarQube
- **Mock Server**: json-server 0.14.0

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /api-utils/status | N/A (Backend) | Health-check do backend |
| POST | /api-utils/logger | N/A (Backend) | Envio de logs |
| GET | /v2/api-docs | N/A (Backend) | Documentação da API |
| GET | /api-security/user/roles | N/A (Backend) | Obter roles do usuário |
| GET | /api-security/me | N/A (Backend) | Obter dados do usuário logado |
| POST | /api-security/logout | N/A (Backend) | Realizar logout |
| GET | /clientes | ClientesService | Listar clientes |
| GET | /clientes/:id | ClientesService | Obter cliente por ID |
| POST | /cliente | ClientesService | Criar novo cliente |
| PUT | /cliente/:id | ClientesService | Atualizar cliente |
| DELETE | /clientes/:id | ClientesService | Excluir cliente |
| GET | /estadoCivil | ClientesService | Listar estados civis |
| POST | /api/notifications | PushNotificationsService | Registrar subscrição de notificações |
| POST | /api/pushnotifications | PushNotificationsService | Enviar notificação push |

## 5. Principais Regras de Negócio

- **Autenticação e Autorização**: Sistema de login com validação de credenciais, controle de acesso baseado em roles (ADMIN, USER, FUNC, ESTAG)
- **Validação de CPF**: Validação customizada de CPF nos formulários de cadastro
- **Validação de Formulários**: Validações de campos obrigatórios, formato de email, datas
- **Gerenciamento de Clientes**: CRUD completo com validações de dados pessoais
- **Criptografia**: Dados sensíveis são criptografados usando chave pública RSA
- **Controle de Sessão**: Gerenciamento de sessão com cookies e tokens
- **Tratamento de Erros**: Sistema centralizado de captura e notificação de erros (runtime e HTTP)
- **Controle de Acesso a Conteúdo**: Diretivas customizadas para controle de visibilidade baseado em permissões
- **SEO**: Gerenciamento dinâmico de metatags para otimização em motores de busca
- **PWA**: Suporte a funcionalidades offline, notificações push e acesso à câmera

## 6. Relação entre Entidades

**ClienteModel**:
- id: number
- nome: string
- email: string
- estadoCivil: string (relacionado com EstadoCivilModel)
- sexo: string
- dataNascimento: Date
- cpf: string

**EstadoCivilModel**:
- id: number
- nome: string

**UserDataModel** (exemplo de tabela):
- id: string
- name: string
- progress: string
- color: string

**Relacionamentos**:
- Cliente possui um EstadoCivil (relacionamento 1:1)
- Sistema de roles: Usuário pode ter múltiplas roles (ADMIN, USER, FUNC, ESTAG)

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| clientes | tabela/endpoint | SELECT | Lista de clientes cadastrados |
| estadoCivil | tabela/endpoint | SELECT | Lista de estados civis disponíveis |
| roles | tabela/endpoint | SELECT | Roles/permissões do usuário |
| userAndRoles | tabela/endpoint | SELECT | Dados do usuário com suas roles |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| clientes | tabela/endpoint | INSERT | Criação de novos clientes |
| clientes | tabela/endpoint | UPDATE | Atualização de dados de clientes |
| clientes | tabela/endpoint | DELETE | Exclusão de clientes |
| log | tabela/endpoint | INSERT | Registro de logs da aplicação |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| env.vars.json | leitura | src/assets/ | Variáveis de ambiente por ambiente (DES, QA, UAT, PRD) |
| list.txt | gravação | src/assets/ | Arquivo criptografado com variáveis de ambiente |
| sitemap.xml | gravação | src/assets/sitemap-*/ | Sitemap gerado para SEO |
| index.html | leitura/gravação | dist/browser/ | Template HTML principal |
| manifest.json | leitura | src/ | Manifesto PWA |
| ngsw-config.json | leitura | src/ | Configuração do Service Worker |
| data.json | leitura | mocks/ | Dados mockados para desenvolvimento |
| routes.json | leitura | mocks/ | Rotas mockadas para desenvolvimento |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Backend (SpringBoot) | REST API | Integração com backend para autenticação, CRUD de clientes, logs |
| Google Search Console | SEO | Submissão de sitemap para indexação |
| Service Worker | PWA | Gerenciamento de cache e notificações push |
| json-server | Mock Server | Servidor mock para desenvolvimento local |
| SonarQube | Análise Estática | Análise de qualidade de código |
| Nexus | Repositório NPM | Repositório de pacotes NPM interno |

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada com separação clara de responsabilidades (core, features, shared, shell)
- Uso adequado de padrões Angular (módulos lazy-loaded, guards, interceptors, services)
- Implementação de testes unitários com Jest e E2E com Protractor
- Documentação com JSDoc em componentes principais
- Configuração de análise estática (TSLint, SonarQube)
- Suporte a SSR e PWA demonstra maturidade técnica
- Uso de bibliotecas internas padronizadas (@arqt/*)
- Implementação de segurança (criptografia, controle de acesso)

**Pontos de Melhoria:**
- Alguns componentes com lógica complexa que poderiam ser refatorados (ex: ShellComponent com configuração extensa)
- Presença de código comentado em alguns arquivos
- Alguns testes com mocks muito específicos que podem dificultar manutenção
- Falta de tratamento de erros em algumas promises/observables
- Configurações hardcoded em alguns lugares (ex: chaves públicas)

## 14. Observações Relevantes

1. **Ambiente Multi-Plataforma**: A aplicação está preparada para rodar em múltiplos ambientes (DES, QA, UAT, PRD) com configurações específicas por ambiente

2. **Docker**: Possui configuração para dois tipos de deployment: Apache (estático) e SSR (Node.js)

3. **SEO**: Implementa estratégias avançadas de SEO com SSR, pre-rendering e geração automática de sitemap

4. **Segurança**: Implementa criptografia RSA para dados sensíveis e controle de acesso baseado em roles

5. **PWA**: Suporte completo a PWA incluindo Service Worker, notificações push e acesso a recursos nativos (câmera)

6. **Temas**: Suporte a múltiplos temas (corporativo e financeira)

7. **Internacionalização**: Estrutura preparada para i18n, embora não completamente implementada

8. **Performance**: Uso de lazy loading, pre-rendering e estratégias de cache para otimização

9. **Desenvolvimento**: Ambiente de desenvolvimento bem estruturado com mock server, hot reload e ferramentas de debug

10. **CI/CD**: Configuração para Jenkins com propriedades específicas para pipeline

11. **Monitoramento**: Integração com sistema de logs centralizado

12. **Acessibilidade**: Uso de componentes Angular Material que seguem padrões de acessibilidade