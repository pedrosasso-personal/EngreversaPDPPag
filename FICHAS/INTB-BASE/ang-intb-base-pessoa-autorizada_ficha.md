# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema Angular para gerenciamento de pessoas autorizadas em contas bancárias do Internet Banking (IB). Permite cadastrar, listar e excluir pessoas autorizadas a realizar operações específicas em uma conta, como atualizar cadastro, consultar extratos, emitir ordens e movimentar/transacionar. O sistema implementa fluxo completo de cadastro com validação de CPF, conferência de dados, seleção de autorizações e validação por token de segurança.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **ListagemPessoaAutorizadaComponent** | Página principal que exibe listagem de pessoas autorizadas e gerencia cadastro/exclusão |
| **TabelaPessoaAutorizadaComponent** | Componente de tabela responsiva para exibir pessoas autorizadas com ação de exclusão |
| **ModalNovaPessoaAutorizadaComponent** | Modal principal que orquestra o fluxo de cadastro de nova pessoa autorizada |
| **ConfereCpfComponent** | Valida e confere CPF da pessoa a ser autorizada |
| **FormularioPessoaComponent** | Formulário para preenchimento de dados cadastrais (nome, email, RG, celular, data nascimento) |
| **AutorizaPessoaComponent** | Seleção de permissões/autorizações a serem concedidas |
| **ConfirmaTokenComponent** | Validação de token de segurança para confirmação do cadastro |
| **PessoaAutorizadaService** | Serviço para comunicação com API backend (GET, POST, DELETE) |
| **AlertToasterComponent** | Exibição de mensagens toast de sucesso/erro |
| **ModalConfirmComponent** | Modal de confirmação genérico |
| **ModalInfoComponent** | Modal informativo genérico |

## 3. Tecnologias Utilizadas

- **Framework Frontend**: Angular 7.1.4
- **Linguagem**: TypeScript 3.1.6
- **UI Components**: Angular Material 7.1.1, @intb/commons (biblioteca interna)
- **Gerenciamento de Estado**: RxJS 6.3.3
- **Formulários**: Angular Reactive Forms
- **HTTP Client**: Angular HttpClient
- **Detecção de Dispositivo**: ngx-device-detector 1.4.1
- **Testes**: Jest 23.6.0
- **Build**: Angular CLI 7.1.4, ng-packagr 4.4.0
- **Arquitetura**: @arqt/spa-framework 1.8.5 (framework SPA interno)
- **Validação de Token**: @intb/commons (TokenModule)
- **Criptografia**: jsencrypt 3.0.0-rc.1

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/pessoa-autorizada` | PessoaAutorizadaService | Lista todas as pessoas autorizadas da conta |
| POST | `/v1/ib/pessoa-autorizada/confere` | PessoaAutorizadaService | Confere se CPF já está cadastrado e retorna dados |
| POST | `/v1/ib/pessoa-autorizada` | PessoaAutorizadaService | Cadastra nova pessoa autorizada (com validação de token) |
| POST | `/v1/ib/pessoa-autorizada/excluir` | PessoaAutorizadaService | Exclui pessoa autorizada pelo código |

## 5. Principais Regras de Negócio

1. **Validação de CPF**: CPF deve ser válido (dígitos verificadores), não pode ser o próprio CPF do usuário logado e não pode estar já cadastrado como pessoa autorizada
2. **Conferência de Pessoa**: Sistema verifica se CPF já existe na base e se já está relacionado à conta antes de prosseguir
3. **Cadastro Condicional**: Se pessoa já existe no sistema, apenas vincula à conta; caso contrário, solicita dados completos (nome, email, RG, celular, data nascimento)
4. **Seleção de Autorizações**: Usuário deve selecionar pelo menos uma autorização entre: atualizar cadastro, consultar extrato (emitir ordens e movimentar/transacionar estão comentados no código)
5. **Validação por Token**: Todo cadastro requer validação de token de segurança antes da confirmação
6. **Limite de Consultas**: Sistema controla quantidade máxima de consultas de CPF por período (retorna erro 403)
7. **Validação de Data**: Data de nascimento deve ser válida, considerando anos bissextos e limites de 150 anos no passado
8. **Formatação de Dados**: Nomes são capitalizados automaticamente antes do envio

## 6. Relação entre Entidades

**PessoaAutorizada**
- cdPessoa: number (identificador único)
- nome: string
- cpf: string

**NovaPessoaAutorizada** (extensão para cadastro)
- pessoaExiste: boolean
- cpf: string
- nome: string
- email: string
- rg: string
- celular: string
- dataNascimento: string
- atualizarCadastro: boolean
- consultarExtrato: boolean
- emitirOrdens: boolean
- movimentarTransacionar: boolean

**PessoaAutorizadaConfere** (resposta de conferência)
- pessoaExiste: boolean
- pessoaRelacionada: boolean
- contaRelacionada: boolean
- nomePessoa: string
- cpfPessoa: string (opcional)

**OperationResponse** (resposta padrão de operações)
- sucesso: boolean
- mensagem: string

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema consome apenas APIs REST, não acessa banco diretamente |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema consome apenas APIs REST, não acessa banco diretamente |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| icon-delete.svg | leitura | TabelaPessoaAutorizadaComponent | Ícone SVG para ação de exclusão na tabela |
| icon-user.svg | leitura | assets/images | Ícone de usuário (uso não identificado no código fornecido) |
| icon-building-money.svg | leitura | assets/images | Ícone de banco/dinheiro (uso não identificado no código fornecido) |
| manifest.json | leitura | Service Worker | Manifesto PWA para instalação da aplicação |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **API Backend BV** | API REST principal para operações de pessoa autorizada (endpoints `/v1/ib/pessoa-autorizada/*`) |
| **API Utils** | Serviços utilitários: health-check (`/api-utils/status`), logger (`/api-utils/logger`), documentação (`/v2/api-docs`) |
| **Token Service** | Serviço de validação de token de segurança (integrado via @intb/commons) |
| **@arqt/spa-framework** | Framework SPA interno do banco para configuração, logging e gerenciamento de aplicação |
| **@intb/commons** | Biblioteca de componentes UI e serviços compartilhados do Internet Banking |

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (components, services, models, utils)
- Uso adequado de TypeScript com tipagem forte
- Implementação de validações customizadas robustas (CPF, data)
- Componentização bem estruturada com comunicação via @Input/@Output
- Uso de Reactive Forms para gerenciamento de formulários
- Tratamento de erros HTTP com retry
- Responsividade implementada (detecção de dispositivo e layouts adaptativos)
- Utilitários de formatação e validação bem isolados

**Pontos de Melhoria:**
- Código comentado em vários locais (emitirOrdens, movimentarTransacionar) indica funcionalidades incompletas ou em transição
- Mensagens de erro hardcoded em múltiplos componentes (deveria estar centralizado)
- Lógica de negócio misturada com lógica de apresentação em alguns componentes
- Falta de tratamento consistente de erros (alguns lugares usam toast, outros não)
- Timeouts hardcoded (4000ms, 8000ms) para mensagens toast
- Uso de `any` em alguns lugares (ex: `data: any[]`)
- Falta de documentação JSDoc em métodos complexos
- Alguns componentes com responsabilidades múltiplas (ex: ModalNovaPessoaAutorizadaContentComponent orquestra todo o fluxo)
- Configurações de altura/largura de modal hardcoded em constants

## 14. Observações Relevantes

1. **Arquitetura de Biblioteca**: O projeto está estruturado como uma biblioteca Angular (`projects/intb/pessoa-autorizada`) que pode ser empacotada e reutilizada em outras aplicações

2. **Fluxo Multi-Step**: O cadastro de pessoa autorizada segue um fluxo wizard de 4 etapas: conferência de CPF → formulário de dados → seleção de autorizações → validação de token

3. **Funcionalidades Desabilitadas**: As autorizações "Emitir Ordens" e "Movimentar/Transacionar" estão comentadas no código, sugerindo que não estão disponíveis na versão atual

4. **Segurança**: Sistema implementa validação por token de segurança e criptografia com chave pública RSA (jsencrypt)

5. **PWA Ready**: Aplicação configurada como Progressive Web App com Service Worker e manifest.json

6. **Ambiente de Desenvolvimento**: Utiliza json-server/nodemon para mock de API em desenvolvimento local

7. **Testes**: Configurado com Jest para testes unitários, incluindo cobertura e relatórios para SonarQube

8. **Build Otimizado**: Configuração de build produção com AOT, tree-shaking, service worker e otimizações avançadas

9. **Nexus Interno**: Projeto depende de repositório NPM interno do banco (nexus.bvnet.bv) para bibliotecas proprietárias

10. **Responsividade**: Sistema adapta layout e comportamento para desktop/mobile usando ngx-device-detector