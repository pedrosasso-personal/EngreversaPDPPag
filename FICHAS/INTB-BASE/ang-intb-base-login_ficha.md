# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de autenticação e login para Internet Banking do Banco BV, desenvolvido em Angular 7. Trata-se de uma biblioteca de componentes reutilizáveis (`@intb/login`) que implementa fluxos de autenticação incluindo: login por CPF, validação de senha com teclado virtual, recuperação/troca de senha, validação por token (SMS/e-mail), migração de usuários e integração com reCAPTCHA. O sistema suporta diferentes perfis de usuários (clientes private e varejo) e possui funcionalidades de primeiro acesso.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **LoginService** | Serviço principal de autenticação: validação de CPF, verificação de senha, obtenção de cookies de acesso, migração de usuários |
| **PasswordService** | Gerenciamento de senhas: obtenção de contatos para token, envio/validação de tokens, reset de senha |
| **AuthPageComponent** | Página principal de autenticação, controla exibição de landing mobile vs desktop |
| **CpfFormComponent** | Formulário de entrada de CPF com validação e integração reCAPTCHA |
| **PasswordFormComponent** | Formulário de senha com teclado virtual e validação de tentativas |
| **ChangePasswordFormComponent** | Formulário de troca/criação de senha com validação de regras de negócio |
| **TokenAuthComponent** | Componente de autenticação por token (SMS/e-mail) |
| **MigrateUserPageComponent** | Página de migração de usuários CA (Corporate Access) |
| **AdobeTagging** | Serviço de tagueamento Adobe Analytics para rastreamento de eventos |
| **BvCryptographyService** | Serviço de criptografia de senhas usando chave pública RSA |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **RxJS 6.3.3** - Programação reativa
- **ng-recaptcha 7.0.1** - Integração Google reCAPTCHA
- **ngx-device-detector 1.4.1** - Detecção de dispositivos
- **@arqt/spa-framework 1.8.5** - Framework interno BV
- **@intb/commons** - Biblioteca de componentes compartilhados BV
- **JSEncrypt 3.0.0-rc.1** - Criptografia RSA
- **Jest 23.6.0** - Framework de testes
- **TypeScript 3.1.6** - Linguagem de programação
- **Node.js 8+** - Ambiente de execução
- **Apache HTTP Server (httpd24)** - Servidor web (produção)
- **Docker** - Containerização

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/jwt-auth/usuario` | LoginService | Obtém dados do usuário por CPF (com reCAPTCHA) |
| POST | `/v1/ib/jwt-auth` | LoginService | Valida senha do usuário |
| POST | `/v1/ib/jwt-auth/senha/acessar` | LoginService | Obtém cookie de acesso após autenticação |
| POST | `/v1/ib/jwt-auth/senha/trocar` | LoginService | Troca senha do usuário |
| POST | `/v1/ib/usuarios` | LoginService | Migração de usuário CA |
| POST | `/v1/ib/senha/token/contato` | PasswordService | Obtém contatos disponíveis para envio de token |
| POST | `/v1/ib/senha/token/enviar` | PasswordService | Envia token de validação (SMS/e-mail) |
| POST | `/v1/ib/senha/token/validar` | PasswordService | Valida token informado pelo usuário |
| POST | `/v1/ib/senha/resetar` | PasswordService | Reseta senha usando token validado |
| GET | `/v1/ib/jwt-auth/banner` | LoginService | Obtém imagens de banner (funcionalidade comentada) |
| GET | `/api-utils/status` | N/A | Health check do backend |
| POST | `/api-utils/logger` | N/A | Endpoint de logging |

---

## 5. Principais Regras de Negócio

1. **Validação de CPF**: Verificação de dígitos verificadores e formato válido
2. **Regras de senha**: 
   - Deve ter 6 a 8 números
   - Não pode conter sequências (ex: 123, 321)
   - Não pode conter repetições (ex: 1111, 2222)
   - Deve ser diferente da senha anterior
3. **Bloqueio por tentativas**: Após 3 tentativas incorretas de senha, o acesso é bloqueado
4. **Autenticação por token**: Validação em duas etapas via SMS ou e-mail
5. **Clientes Private**: Tratamento diferenciado para clientes do segmento private (bloqueio específico)
6. **Migração de usuários CA**: Fluxo específico para migração de usuários Corporate Access
7. **Primeiro acesso**: Usuários sem senha cadastrada são direcionados para criação de senha
8. **Aceite de termos**: Obrigatório aceitar termos de uso e política de privacidade na troca de senha
9. **Timeout de token**: Tokens possuem validade de 60 segundos
10. **Criptografia de senha**: Senhas são criptografadas com RSA antes do envio

---

## 6. Relação entre Entidades

**UserRepresentationModel**
- nome: string
- numeroDocumento: string (CPF)
- hasSignature: boolean (possui senha cadastrada)
- unsubscribe: boolean (deve resetar senha)
- group: boolean (é cliente private)

**UserResponseModel** (resposta da API)
- Estende UserRepresentationModel
- Contém informações adicionais de email, telefone, estado da senha e grupos

**ContatosTokenModel**
- contato: Array de Contato
  - codigo: string
  - tipo: string (telefone/email)
  - valor: string (valor mascarado)

**TokenResponseModel**
- success: boolean
- type: string (tipo de contato usado)
- code: string (código do token)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| localStorage (login.cpf) | leitura/gravação | CpfFormComponent | Armazena CPF para funcionalidade "lembrar CPF" |
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Configurações de ambiente (URLs de API, chaves públicas) |
| data.json | leitura | Mock Server | Dados mockados para desenvolvimento local |
| routes.json | leitura | Mock Server | Rotas mockadas para desenvolvimento local |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **Google reCAPTCHA** | Validação anti-bot no formulário de CPF |
| **Adobe Analytics** | Tagueamento e rastreamento de eventos de usuário |
| **Sistema Legado (begin.do)** | Redirecionamento para sistema antigo em caso de falha de autenticação |
| **API Backend BV** | Todas as operações de autenticação, validação e gerenciamento de senha |
| **Serviço de Criptografia** | Criptografia RSA de senhas usando chave pública |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades entre componentes e serviços
- Uso adequado de TypeScript com tipagem forte
- Implementação de testes unitários (Jest)
- Documentação básica presente (README)
- Uso de padrões Angular (módulos, injeção de dependência)
- Validações de formulário bem estruturadas
- Integração com ferramentas de qualidade (SonarQube, TSLint)

**Pontos de Melhoria:**
- Código comentado em produção (ex: BannerSliderComponent)
- Mensagens de erro hardcoded em constantes dentro dos componentes
- Lógica de negócio complexa em componentes (deveria estar em serviços)
- Alguns componentes muito extensos (ChangePasswordFormComponent com 300+ linhas)
- Uso de `console.log` em código de produção
- Falta de tratamento de erro mais robusto em alguns pontos
- Comentários em português misturados com código em inglês
- Algumas validações poderiam ser extraídas para validators reutilizáveis
- Dependência de versões específicas e antigas (Angular 7)

---

## 14. Observações Relevantes

1. **Biblioteca Reutilizável**: O projeto é estruturado como uma biblioteca Angular (`@intb/login`) para ser consumida por outras aplicações
2. **Mock Server**: Possui servidor mock completo (Node.js) para desenvolvimento local independente do backend
3. **PWA**: Configurado como Progressive Web App com service worker
4. **Docker**: Possui Dockerfile para containerização com Apache HTTP Server
5. **CI/CD**: Integrado com Jenkins (jenkins.properties)
6. **Análise Estática**: Configurado com SonarQube para análise de qualidade de código
7. **Responsividade**: Tratamento específico para mobile com landing page diferenciada
8. **Segurança**: Implementa criptografia RSA para senhas e validação reCAPTCHA
9. **Acessibilidade**: Uso de componentes Material Design com suporte a acessibilidade
10. **Versionamento**: Projeto versionado (0.28.0) com controle de dependências
11. **Migração**: Suporta migração de usuários de sistema legado (Corporate Access)
12. **Analytics**: Integração completa com Adobe Analytics para tracking de eventos