# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de login para Internet Banking (IB) do Banco BV desenvolvido em Angular 7. A aplicação implementa um fluxo de autenticação em duas etapas: validação de CPF e senha com teclado virtual. Suporta Server-Side Rendering (SSR) com Angular Universal, Progressive Web App (PWA) e possui configuração para deploy em containers Docker/OpenShift.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `LoginComponent` | Componente principal que orquestra o fluxo de login e detecta tipo de dispositivo |
| `AuthContainerComponent` | Container responsável pela interface de autenticação |
| `CpfFormComponent` | Formulário de validação de CPF com máscara e validação |
| `PasswordFormComponent` | Formulário de senha com teclado virtual e controle de tentativas |
| `BannerSliderComponent` | Carrossel de banners promocionais na tela de login |
| `LoginService` | Serviço de comunicação com APIs de autenticação |
| `AuthInterceptor` | Interceptor HTTP para gerenciamento de tokens JWT e refresh |
| `AppConfigService` | Serviço de configuração da aplicação |
| `AppMetatagsService` | Gerenciamento de metatags para SEO |
| `UserRepresentationModel` | Modelo de representação de usuário |
| `UserResponseModel` | Modelo de resposta da API de usuário |

## 3. Tecnologias Utilizadas
- **Framework Frontend**: Angular 7.2.15
- **UI Components**: Angular Material 7.1.1, @intb/commons (biblioteca interna)
- **State Management**: RxJS 6.3.3
- **SSR**: Angular Universal (@nguniversal/express-engine 7.0.2)
- **Server**: Express.js 4.16.0
- **Autenticação**: JWT (jsencrypt 3.0.0-rc.1)
- **Criptografia**: crypto-js 3.3.0
- **Testes**: Jest 23.6.0, Protractor 5.4.0
- **Build**: Webpack, Angular CLI 7.3.9
- **Containerização**: Docker
- **Orquestração**: OpenShift (configuração em infra-as-code)
- **Mock Server**: json-server 0.14.0
- **Device Detection**: ngx-device-detector
- **PWA**: @angular/service-worker 7.2.15

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/login/usuario` | LoginService | Valida CPF e retorna dados do usuário |
| POST | `/v1/ib/login` | LoginService | Autentica usuário com senha (grupo/sequência) |
| GET | `/v1/ib/login/banner` | LoginService | Retorna imagens do carrossel de banners |
| POST | `/api-utils/logger` | BvLogService | Envia logs para o backend |
| GET | `/api-utils/status` | - | Health check do backend |
| POST | `/api-security/refresh` | BvLoginService | Renova token de autenticação |
| POST | `/api-security/logout` | BvLoginService | Realiza logout do usuário |

## 5. Principais Regras de Negócio
- Validação de CPF com algoritmo de dígito verificador
- Limite de 3 tentativas de senha incorreta antes do bloqueio
- Redirecionamento para sistema legado em caso de falha na validação de CPF
- Autenticação em duas etapas: CPF + senha com teclado virtual
- Opção de "lembrar CPF" armazenada em localStorage
- Detecção de dispositivo móvel para exibição de landing page específica
- Controle de sessão com JWT e refresh token
- Bloqueio automático de conta após tentativas excedidas ou senha expirada
- Criptografia de variáveis de ambiente com AES-256
- Suporte a múltiplos ambientes (DES, QA, UAT, PRD)

## 6. Relação entre Entidades

**UserRepresentationModel**
- nome: string
- numeroDocumento: string
- tentativaLogin: number
- trocarSenha: boolean

**UserResponseModel**
- numeroDocumento: string
- nome: string
- flagAtivo: boolean
- listaEmail: Email[]
- listaTelefone: Telefone[]
- listaGrupo: Grupo[]
- statusSenha: EstadoSenha

**EstadoSenha**
- flagExpira: boolean
- flagDeveMudar: boolean
- flagBloqueada: boolean
- tentativaLogin: number

Relacionamento: UserResponseModel é transformado em UserRepresentationModel para uso interno da aplicação.

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| `env.vars.json` | Leitura/Gravação | prerender.ts | Variáveis de ambiente por ambiente (DES/QA/UAT/PRD) |
| `list.txt` | Gravação | prerender.ts | Arquivo criptografado com variáveis de ambiente |
| `index.html` | Leitura/Gravação | Universal SSR | Template HTML para renderização server-side |
| `manifest.json` | Leitura | Service Worker | Configuração PWA |
| `ngsw-config.json` | Leitura | Service Worker | Configuração de cache do service worker |
| localStorage `login.cpf` | Leitura/Gravação | CpfFormComponent | Armazenamento do CPF quando usuário marca "lembrar" |
| sessionStorage `Authorization` | Leitura/Gravação | AuthInterceptor | Token JWT de autenticação |
| sessionStorage `Refresh` | Leitura/Gravação | AuthInterceptor | Token de refresh |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Backend BV | REST API | APIs de autenticação, validação de usuário e banners |
| Sistema Legado | HTTP POST | Redirecionamento para sistema antigo em casos específicos (begin.do) |
| Analytics | HTTP | Integração com ferramenta de analytics (configurável por ambiente) |
| Sonar | HTTP | Análise estática de código e cobertura de testes |
| Nexus | NPM Registry | Repositório de pacotes NPM interno do banco |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular seguindo padrões Angular (core, shared, feature modules)
- Uso adequado de TypeScript com interfaces e modelos tipados
- Implementação de interceptors para tratamento centralizado de autenticação
- Separação de responsabilidades entre componentes, serviços e modelos
- Configuração robusta para múltiplos ambientes
- Implementação de SSR e PWA demonstra preocupação com performance
- Testes unitários configurados com Jest
- Uso de bibliotecas internas padronizadas (@arqt, @intb)

**Pontos de Melhoria:**
- Código comentado em vários arquivos (ex: AppComponent, server.ts)
- Algumas funções privadas poderiam ter melhor documentação
- Lógica de redirecionamento para sistema legado poderia ser mais clara
- Tratamento de erros genérico em alguns pontos (handleErrorResponse)
- Falta de validação mais robusta em alguns formulários
- Alguns componentes com responsabilidades múltiplas (ex: PasswordFormComponent)
- Configurações hardcoded em alguns lugares (ex: número máximo de tentativas)

## 14. Observações Relevantes

1. **Arquitetura Híbrida**: O sistema suporta tanto renderização client-side quanto server-side (SSR), com configuração para pré-renderização de rotas estáticas.

2. **Segurança**: Implementa criptografia AES-256 para variáveis de ambiente e utiliza JSEncrypt para criptografia assimétrica com chave pública RSA.

3. **Compatibilidade**: Possui fallback para sistema legado, indicando processo de migração gradual.

4. **DevOps**: Configuração completa para CI/CD com Jenkins (jenkins.properties) e deploy em OpenShift com Docker.

5. **Monitoramento**: Integração com SonarQube para análise de qualidade de código e cobertura de testes.

6. **Responsividade**: Detecta tipo de dispositivo e ajusta interface (landing page para mobile).

7. **Acessibilidade**: Uso de teclado virtual para entrada de senha aumenta segurança.

8. **Mock Server**: Ambiente de desenvolvimento com json-server facilita desenvolvimento sem dependência do backend.

9. **Documentação**: Configurado Compodoc para geração automática de documentação técnica.

10. **Performance**: Implementa lazy loading, tree shaking, e otimizações de bundle para produção.