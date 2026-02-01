# Ficha Técnica do Sistema

## 1. Descrição Geral
O **ang-intb-onda-spa-framework** é uma biblioteca Angular (versão 7) desenvolvida para o Banco Votorantim, que fornece componentes, modelos, serviços e pipes reutilizáveis para aplicações SPA (Single Page Application). A biblioteca é focada em processos de pré-análise e cadastro de clientes (Pessoa Física e Pessoa Jurídica), incluindo funcionalidades de KYC (Know Your Customer), gestão de documentos, validações e fluxos de aprovação. Trata-se de um framework interno que padroniza a construção de interfaces para o ecossistema de aplicações do banco.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **ActionBarComponent** | Componente de barra de ação com navegação de retorno para lista de clientes |
| **FormTitleComponent** | Exibe título do formulário com nome e documento do cliente, permite edição de dados básicos |
| **FormTitleService** | Gerencia estado de edição de dados básicos através de Observables |
| **ActionBarGuard** | Guard de navegação que exibe modal de confirmação ao sair de fluxos de cadastro |
| **PreAnaliseService** | Serviço central que transporta dados do prospect entre componentes |
| **LoggedUserService** | Armazena informações do usuário logado (login, roles, tipo) |
| **EdicaoService** | Controla modos de edição (novo, continuação, dados-básicos, confirmação) |
| **StepsService** | Gerencia navegação entre etapas dos fluxos PF e PJ |
| **PdfService** | Utilitário para download e impressão de PDFs |
| **SafeHtmlPipe** | Pipe para sanitização de HTML recebido de serviços |
| **ProspectModel** | Modelo principal contendo todos os dados do cliente/prospect |
| **Diversos Models** | Modelos de dados (Endereço, Documento, Patrimônio, KYC, Conta, etc.) |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** (framework principal)
- **TypeScript 3.1.6**
- **Angular Material 7.1.1** (componentes UI)
- **RxJS 6.3.3** (programação reativa)
- **Angular Service Worker** (PWA)
- **Jest 23.6.0** (testes unitários)
- **Protractor 5.4.0** (testes E2E)
- **Node.js >= 8.9.3**
- **NPM >= 5.5.1**
- **Apache HTTP Server** (servidor web em produção via Docker)
- **Docker** (containerização com imagem RHEL7)
- **OpenShift** (orquestração e deployment)
- **Sonar** (análise estática de código)
- **Compodoc** (documentação)
- **Webpack Bundle Analyzer** (análise de bundles)
- **JSON Server** (mock de APIs em desenvolvimento)

---

## 4. Principais Endpoints REST

Não se aplica. Esta é uma biblioteca de componentes frontend Angular. A integração com APIs REST é feita pelas aplicações que consomem esta biblioteca, através de configurações em `environment.ts`:

- `/api-utils/status` (health check)
- `/api-utils/logger` (logs)
- `/v2/api-docs` (documentação Swagger)

As rotas de proxy são configuradas via Apache (`rotas.conf`) para redirecionar chamadas `/api` para backends específicos.

---

## 5. Principais Regras de Negócio

- **Fluxos de Cadastro Diferenciados**: Suporte a cadastro de Pessoa Física (PF) e Pessoa Jurídica (PJ) com etapas específicas
- **Modos de Edição**: Controle de estados (novo cadastro, continuação, edição de dados básicos, confirmação)
- **Validação de Perfis**: Diferenciação entre fluxo Officer (O) e Internet (I)
- **KYC (Know Your Customer)**: Coleta de informações sobre relacionamento com países, propósito de câmbio, visitas
- **Gestão de Patrimônio**: Captura de dados financeiros, origem de patrimônio, investimentos
- **PPE (Pessoa Politicamente Exposta)**: Identificação e registro de vínculos políticos
- **Autorização de Terceiros**: Gestão de pessoas autorizadas a operar contas
- **Validação de Documentos**: Controle de tipos de documentos por grupo
- **Navegação Condicional**: Guards que impedem perda de dados não salvos
- **Permissionamento por Roles**: Controle de acesso baseado em perfis de usuário

---

## 6. Relação entre Entidades

**ProspectModel** (entidade central) contém:
- **DocumentoModel**: Dados de identificação (RG, CNH, etc.)
- **EnderecoModel**: Endereço residencial e comercial
  - **ExteriorModel**: Domicílio fiscal no exterior
  - **OutrosDomiciliosModel**: Outros endereços fiscais
  - **ResidenciaPermanenteModel**: Residência permanente
- **PatrimonioModel**: Dados financeiros e renda
- **OrigemPatrimonioModel**: Origem dos recursos
- **OcupacaoProfissionalModel**: Dados profissionais
- **ProfissaoModel** / **CargoModel**: Ocupação
- **ContaDestinoModel**: Contas para transferência
  - **TitularContaCorrenteModel**: Titulares da conta
- **ContaModel**: Dados da conta bancária
  - **UsuarioAdministradorModel**: Administradores
- **GestaoPatrimonioModel**: Serviços de gestão
- **KycModel**: Dados de Know Your Customer
  - **PaisModel**: Países relacionados
- **PessoaAutorizadaModel**: Terceiros autorizados
- **PessoaAutorizadaInvestimentoModel**: Autorizados para investimentos
- **NaturezaJuridicaModel** / **AtividadeEconomicaModel**: Dados PJ
- **PPEModel**: Pessoas politicamente expostas

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

Esta biblioteca não acessa diretamente banco de dados. O acesso é feito por APIs REST consumidas pelas aplicações que utilizam esta biblioteca.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

Esta biblioteca não atualiza diretamente banco de dados. As operações de persistência são realizadas por APIs REST consumidas pelas aplicações que utilizam esta biblioteca.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `environment.ts` / `environment.prod.ts` | Leitura | Configuração Angular | Configurações de ambiente (URLs de API, log level, chaves públicas) |
| `mocks/data.json` | Leitura | JSON Server (dev) | Dados mockados para desenvolvimento |
| `mocks/routes.json` | Leitura | JSON Server (dev) | Mapeamento de rotas mockadas |
| `angular-httpd.conf` | Leitura | Apache HTTP Server | Configuração de proxy e compressão |
| `rotas.conf` | Leitura | Apache (ConfigMap) | Configuração de rotas por ambiente |
| `manifest.json` | Leitura | Service Worker | Manifesto PWA |
| `ngsw-config.json` | Leitura | Service Worker | Configuração de cache offline |
| PDFs gerados | Gravação | PdfService | Download de documentos via blob |

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
| **APIs Backend BV** | Integração com serviços REST do banco (via proxy `/api`) |
| **Nexus (NPM Registry)** | Repositório de pacotes NPM interno (`https://nexus.bvnet.bv/repository/npm-group/`) |
| **Sonar** | Análise estática de código (`https://sonar.appdes.bvnet.bv`) |
| **OpenShift** | Plataforma de deployment e orquestração de containers |
| **@arqt/spa-framework** | Framework base de arquitetura SPA do banco |
| **@intb/ui** | Biblioteca de componentes UI do banco |
| **Angular Material** | Biblioteca de componentes Material Design |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara entre models, services, pipes e componentes
- Uso adequado de TypeScript com interfaces e classes tipadas
- Documentação JSDoc presente em várias classes
- Implementação de guards para proteção de rotas
- Uso de Observables (RxJS) para gerenciamento de estado
- Configuração de testes unitários (Jest) e E2E (Protractor)
- Implementação de PWA com Service Worker
- Uso de ChangeDetectionStrategy.OnPush para otimização
- Configuração de análise estática (Sonar, TSLint)

**Pontos de Melhoria:**
- Alguns métodos com complexidade ciclomática alta (comentário `cyclomatic-complexity` no guard)
- Código comentado em alguns arquivos (ex: PdfService)
- Falta de tratamento de erros explícito em alguns serviços
- Alguns construtores com muitos parâmetros (ex: EnderecoModel com 12 parâmetros)
- Uso de `any` em alguns lugares (ex: SafeHtmlPipe)
- Falta de validações de entrada em alguns métodos
- Alguns models com lógica de inicialização no construtor que poderia ser factory methods
- Comentários TODO indicando funcionalidades incompletas

---

## 14. Observações Relevantes

1. **Biblioteca Angular (ng-packagr)**: Este é um projeto de biblioteca Angular, não uma aplicação standalone. É publicado como pacote NPM para consumo por outras aplicações.

2. **Multi-ambiente**: Suporte a múltiplos ambientes (DES, QA, UAT, PRD) com ConfigMaps específicos no OpenShift.

3. **Deployment Docker**: Utiliza imagem Red Hat Enterprise Linux 7 com Apache HTTP Server 2.4.

4. **Proxy Reverso**: Configuração de proxy Apache para roteamento de APIs backend.

5. **Compressão**: Configuração de compressão GZIP para diversos tipos de conteúdo.

6. **Cache Control**: Headers específicos para `index.html` evitando cache do shell da aplicação.

7. **Segurança**: Uso de chave pública RSA para criptografia (presente em environment).

8. **Versionamento**: Versão atual 1.27.0 (package.json).

9. **Fluxos Complexos**: Suporte a fluxos de cadastro PF (7 etapas) e PJ (7 etapas) com navegação condicional.

10. **Internacionalização**: Preparado para i18n (extract-i18n configurado).

11. **Bundle Analysis**: Ferramentas configuradas para análise de tamanho de bundles.

12. **Lazy Loading**: Configuração de lazy loading para fontes (lazy-fonts.css).

13. **Service Worker**: Estratégias de cache configuradas (prefetch para app, lazy para assets).

14. **Mocks**: Estrutura completa de mocks para desenvolvimento local sem backend.

15. **Jenkins**: Arquivo de propriedades para integração CI/CD (`jenkins.properties`).