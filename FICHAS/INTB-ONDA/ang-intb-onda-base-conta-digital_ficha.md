# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web de **Onboarding Digital** do Banco Votorantim para abertura de contas digitais de Pessoa Física (PF) e Pessoa Jurídica (PJ). A aplicação implementa um fluxo wizard multi-etapas com validações complexas, integração com APIs backend para consulta de dados cadastrais, upload de documentos, geração de contratos em PDF e aceite de termos. Suporta dois perfis de usuário: **OFFICER** (uso interno do banco) e **INTERNET** (cliente externo). Possui funcionalidades de continuação de cadastro, edição contextual por fase e dashboard de acompanhamento de prospects.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **DadosBasicosComponent** | Formulário inicial de dados básicos PF (CPF, nome, email, telefone, officer) |
| **PjDadosBasicosComponent** | Formulário inicial de dados básicos PJ (CNPJ, razão social, contato, officer) |
| **DadosPessoaisComponent** | Coleta dados pessoais PF (sexo, naturalidade, documentos, estado civil, PPE) |
| **DadosResidenciaisComponent** | Endereço residencial PF com busca CEP e flags domicílio fiscal |
| **DadosProfissionaisComponent** | Dados profissionais PF (ocupação, profissão, cargo, endereço comercial) |
| **DadosFinanceirosComponent** | Renda anual, patrimônio e origem de recursos PF |
| **InfoAdicionaisComponent** | Tipo investidor, terceiros autorizados, conta destino, gestão patrimonial PF |
| **DadosConfirmacaoComponent** | Tela de revisão e confirmação de todos os dados PF (read-only) |
| **PjDadosEmpresaComponent** | Dados da empresa PJ (data constituição, natureza jurídica, atividade econômica) |
| **PjInfoAdicionaisComponent** | Empresas controladas/coligadas, sócios PPE, GIIN, renda passiva PJ |
| **PjServicosComponent** | Orquestrador de 5 sub-componentes de serviços bancários PJ |
| **ServicoContaComponent** | Tipo de conta e cheque empresarial PJ |
| **ServicoInternetBankingComponent** | Configuração IB, usuários admin e assinaturas obrigatórias PJ |
| **ServicoInvestimentosComponent** | Investimentos, DTVM, carteira administrada e autorizados PJ |
| **PjDadosConfirmacaoComponent** | Revisão completa dados PJ antes envio final |
| **DocumentosPjComponent** | Upload de documentos obrigatórios PJ (estatuto, balanço, etc) |
| **TermosPjComponent** | Aceite de termos contratuais PJ com representantes legais |
| **DashboardComponent** | Listagem de prospects com filtros e ações contextuais |
| **DadosKycComponent** | Cadastro KYC para operações de câmbio internacional |
| **ApiPreAnaliseService** | Integração com API backend para CRUD de prospects e listas de domínio |
| **ApiContratosService** | Geração de PDF de contratos e upload de documentos |
| **ApiDashboardService** | Listagem de prospects por usuário |
| **RotasService** | Controle de navegação entre etapas do fluxo cadastral |
| **FormStepsGuard** | Guard de rotas que valida permissões de acesso por fase |
| **OndaLoaderInterceptor** | Interceptor HTTP que exibe loader durante requisições |

---

## 3. Tecnologias Utilizadas

- **Frontend**: Angular 7.1.4, TypeScript 3.1
- **UI Framework**: Angular Material 7.1, Bootstrap Grid 4
- **Bibliotecas Internas BV**: @intb/spa-framework 1.25, @intb/ui 0.37, @arqt/libs
- **Formulários**: Reactive Forms, Angular Text Mask, ngx-currency
- **HTTP**: HttpClient, RxJS 6.3
- **SSR**: Angular Universal (@nguniversal/express-engine)
- **Servidor**: Express.js, Domino (mock DOM server-side)
- **Segurança**: jsencrypt (criptografia RSA), cookie-parser
- **Utilitários**: Moment.js (manipulação datas), Hammerjs (gestos touch)
- **Testes**: Jest, Protractor (E2E - desabilitados)
- **Build**: Angular CLI, Webpack, AOT Compilation
- **Qualidade**: TSLint, Codelyzer, SonarQube
- **Containerização**: Docker (Apache 2.4 Alpine, Node 8)
- **PWA**: Service Worker, Web App Manifest
- **Mock Server**: json-server (desenvolvimento)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/documento/contrato/{doc}` | ApiContratosService | Gera PDF do contrato de abertura de conta |
| POST | `/documento/upload/incluir` | ApiContratosService | Upload de documentos com tracking de progresso |
| POST | `/documento/salvar/upload` | ApiContratosService | Finaliza e persiste upload de documentos |
| POST | `/listarProspect/{user}` | ApiDashboardService | Lista prospects por usuário logado |
| POST | `/incluirDadosProspect` | ApiPreAnaliseService | Cria novo prospect (dados iniciais) |
| POST | `/alterarDadosProspect` | ApiPreAnaliseService | Atualiza dados de prospect existente |
| POST | `/consultarDadosProspect` | ApiPreAnaliseService | Consulta dados completos de prospect |
| POST | `/obterPessoa` | ApiPreAnaliseService | Obtém dados de pessoa por documento |
| GET | `/listarEstadoCivil` | ApiPreAnaliseService | Lista estados civis |
| GET | `/listarTipoDocumento` | ApiPreAnaliseService | Lista tipos de documento |
| GET | `/listarFaixaPatrimonio` | ApiPreAnaliseService | Lista faixas de patrimônio |
| GET | `/listarPais` | ApiPreAnaliseService | Lista países |
| GET | `/listarCidade` | ApiPreAnaliseService | Lista cidades |
| GET | `/listarOfficer` | ApiPreAnaliseService | Lista officers do banco |
| GET | `/listarOcupacaoProfissional` | ApiPreAnaliseService | Lista ocupações profissionais |
| GET | `/listarProfissao` | ApiPreAnaliseService | Lista profissões |
| GET | `/listarCargo` | ApiPreAnaliseService | Lista cargos |
| GET | `/listarBanco` | ApiPreAnaliseService | Lista bancos |
| GET | `/listarAtividadeEconomica` | ApiPreAnaliseService | Lista atividades econômicas |
| GET | `/listarNaturezaJuridica` | ApiPreAnaliseService | Lista naturezas jurídicas |
| GET | `/buscarCep/{cep}` | ApiPreAnaliseService | Busca endereço por CEP |
| POST | `/obterRotas` | ApiPreAnaliseService | Obtém rotas de navegação por fase |
| POST | `/obterTermos` | ApiPreAnaliseService | Obtém termos contratuais para aceite |
| POST | `/enviarDadosEmail` | ApiPreAnaliseService | Envia link de cadastro por email |

---

## 5. Principais Regras de Negócio

- **Validação CPF/CNPJ**: Algoritmo de validação de dígitos verificadores
- **Nome Completo**: Obrigatório sem abreviações para campos de filiação e cônjuge
- **Data Nascimento PF**: Entre 01/01/1918 e data atual
- **Data Constituição PJ**: Entre 01/01/1500 e data atual
- **Telefone**: Mínimo 10 dígitos (PF) ou 11 dígitos (PJ)
- **Estado Civil**: Campos cônjuge obrigatórios se casado/união estável
- **Cidadania USA**: Campo NIF obrigatório se cidadão americano
- **PPE (Pessoa Politicamente Exposta)**: Validação e coleta de informações adicionais
- **Patrimônio**: Cálculo automático baseado em renda, bens imóveis e mercado financeiro
- **Origem Patrimônio**: Mínimo 1 origem selecionada (múltipla escolha)
- **Terceiros Autorizados PF**: Máximo 3 pessoas com permissões granulares
- **Empresas Controladas/Coligadas PJ**: Máximo 5 de cada tipo
- **Sócios PPE PJ**: Máximo 3 sócios politicamente expostos
- **Usuários Admin IB PJ**: Máximo 4, com validação de assinaturas obrigatórias ≥ usuários selecionados
- **Pessoas Autorizadas Investimentos PJ**: Máximo 3
- **Upload Documentos PJ**: Validação de formato PDF, documentos obrigatórios por natureza jurídica (SA/LTDA)
- **Aceite Termos PJ**: Até 4 representantes legais com CPF e email
- **Navegação Contextual**: Rotas dinâmicas baseadas em fase, tipo edição (novo/continuação/confirmação) e perfil (Officer/Internet)
- **Modo Edição**: Permite edição de seções específicas após confirmação inicial
- **KYC Câmbio**: Mínimo 1 país e 1 natureza de operação cambial
- **Cheque Empresarial**: Disponível apenas para Conta Corrente (não Conta Transitória)
- **Pacotes de Serviços**: Mapeamento código tarifador (ex: BV_CASH_PAY=142)

---

## 6. Relação entre Entidades

**Entidade Principal: Prospect**
- Representa um cadastro em andamento (PF ou PJ)
- Contém dados básicos, pessoais, residenciais, profissionais, financeiros, info adicionais
- Relaciona-se com:
  - **Documento** (1:N) - RG, CNH, passaporte, etc
  - **Endereco** (1:N) - residencial, comercial, matriz
  - **PessoaAutorizada** (1:N) - terceiros autorizados PF
  - **ContaDestino** (1:N) - contas para transferências recorrentes
  - **Empresa** (1:1) - dados empresa PJ
  - **EmpresaControlada** (1:N) - empresas controladas PJ
  - **EmpresaColigada** (1:N) - empresas coligadas PJ
  - **SocioPPE** (1:N) - sócios politicamente expostos PJ
  - **UsuarioAdministrador** (1:N) - admins Internet Banking PJ
  - **PessoaAutorizadaInvestimento** (1:N) - autorizados investimentos PJ
  - **Conta** (1:1) - dados da conta bancária
  - **KYC** (1:1) - dados Know Your Customer
  - **Officer** (N:1) - gerente responsável

**Hierarquia de Modelos de Transformação:**
- **ProspectModel** (backend) ↔ **DadosBasicosModel/PJDadosBasicosModel** (view)
- **ProspectModel** ↔ **DadosPessoaisModel** (view)
- **ProspectModel** ↔ **DadosResidenciaisModel** (view)
- **ProspectModel** ↔ **DadosProfissionaisModel** (view)
- **ProspectModel** ↔ **DadosFinanceirosModel** (view)
- **ProspectModel** ↔ **InfoAdicionaisModel** (view)
- **ProspectModel** ↔ **PJDadosEmpresaModel** (view)
- **ProspectModel** ↔ **PJInfoAdicionaisModel** (view)
- **ProspectModel** ↔ **PJDadosServicoModel** (view)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Prospect | Tabela | SELECT | Consulta dados de prospects por documento/ID |
| EstadoCivil | Tabela | SELECT | Lista estados civis disponíveis |
| TipoDocumento | Tabela | SELECT | Lista tipos de documento (RG, CNH, Passaporte) |
| FaixaPatrimonio | Tabela | SELECT | Lista faixas de patrimônio |
| Pais | Tabela | SELECT | Lista países |
| Cidade | Tabela | SELECT | Lista cidades por UF |
| Officer | Tabela | SELECT | Lista gerentes/officers do banco |
| OcupacaoProfissional | Tabela | SELECT | Lista ocupações profissionais |
| Profissao | Tabela | SELECT | Lista profissões |
| Cargo | Tabela | SELECT | Lista cargos |
| Banco | Tabela | SELECT | Lista bancos para conta destino |
| AtividadeEconomica | Tabela | SELECT | Lista atividades econômicas (CNAE) |
| NaturezaJuridica | Tabela | SELECT | Lista naturezas jurídicas (SA, LTDA, etc) |
| Termos | Tabela | SELECT | Consulta termos contratuais para aceite |
| Rotas | Tabela | SELECT | Consulta rotas de navegação por fase |
| CEP (API externa) | API | SELECT | Busca endereço por CEP via integração |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Prospect | Tabela | INSERT | Criação de novo prospect (dados iniciais) |
| Prospect | Tabela | UPDATE | Atualização de dados de prospect existente (todas as fases) |
| Documento | Tabela | INSERT | Upload de documentos (estatuto, balanço, RG, etc) |
| Upload | Tabela | INSERT | Registro de uploads de documentos |
| TermosAceite | Tabela | INSERT | Registro de aceite de termos contratuais |
| EmailEnviado | Tabela | INSERT | Log de envio de emails com link de cadastro |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **contrato_{documento}.pdf** | Gravação | ApiContratosService / ConclusaoComponent | PDF do contrato de abertura de conta gerado pelo backend |
| **estatuto.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de estatuto social (PJ SA) |
| **eleicao_diretoria.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de ata de eleição de diretoria (PJ SA) |
| **balanco.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de balanço patrimonial (PJ) |
| **documentos_beneficiarios.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de documentos de beneficiários finais (PJ) |
| **procuracao.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de procuração (PJ) |
| **substabelecimento.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de substabelecimento (PJ) |
| **contrato_social.pdf** | Leitura | DocumentosPjComponent / CaixaDocumentoComponent | Upload de contrato social (PJ LTDA) |
| **manifest.json** | Leitura | index.html | Manifesto PWA para instalação como app |
| **ngsw-worker.js** | Leitura | index.html | Service Worker para cache offline (PWA) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ).

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Backend Pré-Análise** | REST API | CRUD de prospects, listas de domínio, validações, rotas de navegação |
| **API Contratos** | REST API | Geração de PDF de contratos, upload e persistência de documentos |
| **API Dashboard** | REST API | Listagem de prospects por usuário |
| **API ViaCEP** | REST API | Busca de endereço por CEP (integração via backend) |
| **BvLoginService** | Biblioteca Interna | Autenticação de usuários (framework @intb/spa-framework) |
| **BvRolesService** | Biblioteca Interna | Controle de perfis e permissões (OFFICER/INTERNET) |
| **BvSecurityAccessService** | Biblioteca Interna | Validação de chaves de acesso e controle de sessão |
| **BvErrorService** | Biblioteca Interna | Tratamento centralizado de erros e notificações |
| **json-server** | Mock Server | Servidor mock para desenvolvimento local (porta 4000) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (componentes, services, models)
- Uso consistente de Reactive Forms e validações customizadas
- Implementação de guards para controle de navegação
- Padrão de parse bidirecional entre models de view e backend bem definido
- Interceptor HTTP centralizado para loader
- Configuração SSR (Server-Side Rendering) para melhor SEO e performance inicial
- PWA habilitado com service worker
- Testes unitários configurados (Jest)
- Análise de qualidade com SonarQube e TSLint
- Documentação inline razoável

**Pontos de Melhoria:**
- Testes E2E desabilitados (xdescribe) - falta cobertura de testes de integração
- Alguns componentes com alta complexidade ciclomática (ex: InfoAdicionaisComponent, PjServicosComponent)
- Lógica de negócio misturada com lógica de apresentação em alguns componentes
- Falta de tratamento de erros mais robusto em algumas chamadas HTTP
- Código duplicado em validações customizadas (ex: validação de nome completo)
- Alguns magic numbers e strings hardcoded (ex: códigos de pacotes, fases)
- Falta de interfaces TypeScript para alguns models (uso de classes quando interfaces seriam suficientes)
- Comentários em português misturados com código em inglês (inconsistência)
- Alguns componentes muito grandes que poderiam ser refatorados em sub-componentes menores

---

## 14. Observações Relevantes

1. **Perfis de Usuário**: O sistema possui dois perfis distintos (OFFICER e INTERNET) com fluxos e permissões diferentes. Officers têm acesso ao dashboard e podem editar qualquer fase, enquanto usuários Internet seguem fluxo linear restrito.

2. **Modo Edição Contextual**: Implementa três modos de edição (novo/continuação/confirmação) que alteram comportamento de validações, navegação e persistência.

3. **Navegação Dinâmica**: O sistema usa `RotasService` para determinar próxima/anterior etapa baseado em fase atual, tipo edição e perfil, permitindo fluxos não-lineares.

4. **Upload com Progress Tracking**: Implementação de upload de arquivos com barra de progresso usando `HttpEventType.UploadProgress`.

5. **Validações Complexas**: Validadores customizados para CPF, CNPJ, nome completo, autocomplete, datas, e validações condicionais baseadas em outros campos.

6. **Integração com Bibliotecas Internas BV**: Forte dependência de bibliotecas proprietárias (@intb/spa-framework, @intb/ui, @arqt) que encapsulam autenticação, autorização, notificações e componentes UI.

7. **SSR e PWA**: Aplicação preparada para produção com Server-Side Rendering (melhor SEO) e Progressive Web App (instalável, cache offline).

8. **Docker Multi-Stage**: Dockerfiles separados para ambiente de produção (Apache) e desenvolvimento (json-server mock).

9. **Proxy API**: Configuração de proxy para backend em OpenShift durante desenvolvimento, facilitando CORS.

10. **Listas Estáticas**: Algumas listas (UFs, órgãos emissores, tratamentos) são mantidas como constantes no frontend, reduzindo chamadas ao backend.

11. **Formatação Monetária**: Uso de `ngx-currency` para formatação e entrada de valores monetários com máscara.

12. **Máscaras de Input**: Implementação de máscaras para CPF, CNPJ, telefone, CEP usando `angular2-text-mask`.

13. **Material Design**: UI baseada em Angular Material 7 com customizações de tema corporativo BV.

14. **Gestão de Estado**: Uso de `BehaviorSubject` para compartilhamento de estado entre componentes (ex: rotas, dados de prospect).

15. **Segurança**: Criptografia RSA (jsencrypt) para dados sensíveis, validação de tokens, controle de sessão via cookies.