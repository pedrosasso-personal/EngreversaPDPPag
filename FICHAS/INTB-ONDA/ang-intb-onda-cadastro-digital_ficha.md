# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web de cadastro digital de clientes Pessoa Física (PF) e Pessoa Jurídica (PJ) do Banco Votorantim. Trata-se de uma aplicação de onboarding que permite o cadastro completo de prospects através de um fluxo multi-etapas, incluindo coleta de dados pessoais/empresariais, informações profissionais e financeiras, KYC (Know Your Customer), upload de documentos obrigatórios e geração de contratos em PDF. O sistema possui validações complexas, integração com BFF (Backend For Frontend) para persistência de dados e consultas a serviços externos (CEP, listas de domínio), além de suportar modo de edição e continuação de cadastros iniciados.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **DadosBasicosComponent/Service** | Cadastro inicial PF: CPF, nome, email, telefone, seleção de officer |
| **DadosPessoaisComponent/Service** | Dados pessoais PF: sexo, data nascimento, filiação, documentos (RG/CNH), estado civil, nacionalidade |
| **DadosResidenciaisComponent/Service** | Endereço residencial, domicílio fiscal, validação CEP, países de residência |
| **DadosProfissionaisComponent/Service** | Ocupação, profissão, cargo, dados da empresa, endereço comercial |
| **DadosFinanceirosComponent/Service** | Patrimônio total, renda mensal/anual, origem do patrimônio |
| **InfoAdicionaisComponent/Service** | Tipo investidor, DVTM, pessoas autorizadas (até 3), conta destino, gestão patrimonial |
| **DadosConfirmacaoComponent** | Revisão consolidada de todos os dados antes do envio final |
| **DadosKycComponent/Service** | KYC: países de negociação, naturezas de câmbio, propósito operação |
| **PJDadosBasicosComponent/Service** | Cadastro inicial PJ: CNPJ, razão social, país constituição, contato, officer |
| **PJDadosEmpresaComponent/Service** | Dados empresa: data fundação, natureza jurídica, atividade econômica, endereço, contatos |
| **PJInfoAdicionaisComponent/Service** | Empresas controladas/coligadas (até 5 cada), sócios PPE (até 3), FATCA (GIIN, renda passiva) |
| **PJServicosComponent/Service** | Orquestrador de 5 sub-formulários: Conta, Internet Banking, Cobrança, Pacotes, Investimentos |
| **ServicoContaComponent/Service** | Configuração conta corrente PJ, cheque empresarial |
| **ServicoInternetBankingComponent/Service** | Config IB: valor transações, assinaturas obrigatórias, usuários admin (até 10) |
| **ServicoInvestimentosComponent/Service** | Investimentos: valor, carteira administrada, pessoas autorizadas (até 10) |
| **DocumentosPjComponent/Service** | Upload múltiplos documentos PJ (estatuto, atas, balanço, RG beneficiários, procurações) com progress tracking |
| **TermosPjComponent/Service** | Aceite termos contratuais PJ, cadastro representantes (até 4) |
| **CaixaDocumentoComponent** | Componente reutilizável upload com drag-drop, preview, validação PDF |
| **ApiPreAnaliseService** | Integração BFF: CRUD prospects, listas domínio, validações, CEP |
| **ApiContratosService** | Geração contratos PDF, upload documentos, consulta relacionamento CNPJ |
| **NovoCadastroService** | Validação hash de acesso temporal, obtenção dados acesso prospect |
| **RotasService** | Controle navegação dinâmica entre etapas baseado em contexto usuário/fase |
| **ProspectModel** | Modelo central agregando todos dados cadastro PF/PJ |
| **OndaLoaderInterceptor** | Interceptor HTTP global para controle de loader overlay |

---

## 3. Tecnologias Utilizadas

- **Frontend Framework:** Angular 7+
- **UI Components:** Angular Material Design, @intb/ui (biblioteca interna)
- **State Management:** RxJS (BehaviorSubject para sincronização entre componentes)
- **Formulários:** Reactive Forms com validações customizadas
- **Máscaras:** ngx-mask (CPF, telefone), ngx-currency (valores monetários)
- **HTTP Client:** HttpClient Angular com interceptors
- **Testes:** Jest (testes unitários), Protractor (E2E)
- **SSR:** Angular Universal (Server-Side Rendering)
- **Roteamento:** Angular Router com RouteReuseStrategy customizada
- **Upload:** HttpEventType para tracking de progresso
- **PDF:** Geração via BFF, download como Blob
- **Containerização:** Docker
- **Mock Server:** json-server (desenvolvimento)
- **Arquitetura:** @arqt/spa-framework (framework interno)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/incluirCadastroProspect` | ApiPreAnaliseService | Inclusão inicial de prospect (dados básicos) |
| POST | `/alterarDadosProspect` | ApiPreAnaliseService | Atualização dados prospect (todas etapas) |
| POST | `/obterDadosProspect` | ApiPreAnaliseService | Consulta dados prospect por número documento |
| POST | `/validarHashAcesso` | NovoCadastroService | Validação hash temporal de acesso ao cadastro |
| POST | `/validarProspect` | NovoCadastroService | Validação existência prospect |
| GET | `/listarEstadoCivil` | ApiPreAnaliseService | Lista estados civis |
| POST | `/listarPais` | ApiPreAnaliseService | Lista países |
| POST | `/listarCidade` | ApiPreAnaliseService | Lista cidades por UF |
| POST | `/listarOfficer/{login}` | ApiPreAnaliseService | Lista officers disponíveis |
| POST | `/obterEnderecoCep/` | ApiPreAnaliseService | Busca endereço por CEP |
| POST | `/listarOcupacaoProfissional` | ApiPreAnaliseService | Lista ocupações profissionais |
| POST | `/listarProfissao` | ApiPreAnaliseService | Lista profissões |
| POST | `/listarCargo` | ApiPreAnaliseService | Lista cargos |
| POST | `/listarBanco` | ApiPreAnaliseService | Lista bancos para conta destino |
| POST | `/listarAtividadeEconomica` | ApiPreAnaliseService | Lista atividades econômicas (PJ) |
| POST | `/listarNaturezaJuridica` | ApiPreAnaliseService | Lista naturezas jurídicas (PJ) |
| GET | `/documento/contrato/{numeroHash}` | ApiContratosService | Download contrato PDF gerado |
| POST | `/documento/upload/incluir` | ApiContratosService | Upload documento com progress tracking |
| POST | `/documento/salvar/upload` | ApiContratosService | Finalização envio documentos |
| POST | `/gerarContrato` | ApiContratosService | Geração contrato PDF assinado |
| POST | `/consultarRelacionamento` | ApiContratosService | Validação CNPJ existente (PJ) |
| POST | `/obterTermos` | ApiPreAnaliseService | Obtenção conteúdo HTML termos contratuais |
| POST | `/rotas` | RotasService | Obtenção rotas dinâmicas navegação |

---

## 5. Principais Regras de Negócio

- **Validação Hash Acesso:** Hash temporal obrigatório para iniciar cadastro, validado via `/validarHashAcesso`
- **CPF/CNPJ Único:** Validação de prospect existente antes inclusão
- **Fluxo Sequencial Obrigatório:** Etapas cadastrais devem ser completadas em ordem (dados básicos → pessoais → residenciais → profissionais → financeiros → info adicionais → confirmação)
- **Campos Cônjuge:** Obrigatórios se estado civil = casado/união estável
- **Cidadania Americana:** Exige preenchimento NIF (Número Identificação Fiscal)
- **Cálculo Patrimônio:** Soma automática de bens + mercado financeiro
- **Origem Patrimônio:** Mínimo 1 origem selecionada obrigatoriamente
- **Validação Idade:** Data nascimento entre 1918 e data atual
- **Gestão Patrimonial:** Diferenciação carteira discricionária vs não-discricionária
- **Documentos PJ Obrigatórios:** Estatuto/Contrato Social, Balanço Patrimonial, RG representantes legais (conforme natureza jurídica)
- **Empresas Controladas/Coligadas:** Máximo 5 de cada tipo
- **Sócios PPE:** Máximo 3 pessoas politicamente expostas
- **Usuários Admin IB:** Até 10 usuários, validação assinaturas obrigatórias ≤ usuários marcados
- **Pessoas Autorizadas Investimentos:** Máximo 10 procuradores
- **Terceiros Autorizados (PF):** Máximo 3 pessoas
- **FATCA (PJ):** GIIN obrigatório se residente fiscal EUA = 'S'
- **Naturezas Câmbio (KYC):** Mínimo 1 selecionada
- **Pacotes Tarifador:** Mapeamento códigos (SP=0, PAY=142, STANDARD=143, CLASSIC=144, PLUS=145, COLLECTION=146)
- **Validação CNPJ Relacionamento:** CNPJ não pode ter relacionamento ativo (tipo 11) antes cadastro
- **Modo Edição:** Suporta edição parcial via flags `tipoEdicao` e `faseAtualizacao`
- **Rotas Dinâmicas:** Navegação baseada em contexto (tipoUsuario, fase, tipoEdicao)

---

## 6. Relação entre Entidades

```
Prospect (entidade central)
├── Officer (N:1) - relacionamento com gestor responsável
├── EnderecoResidencial (1:1) - endereço principal
├── EnderecoComercial (1:1) - endereço empresa (PF) ou sede (PJ)
├── DomicilioFiscal (1:1) - endereço fiscal se diferente residencial
├── Documento (1:1) - RG/CNH pessoa física
├── EstadoCivil (N:1) - referência tabela domínio
├── Nacionalidade (N:1) - país origem
├── Naturalidade (N:1) - cidade nascimento
├── Profissao (N:1) - referência tabela domínio
├── OcupacaoProfissional (N:1) - referência tabela domínio
├── Cargo (N:1) - referência tabela domínio
├── PessoasAutorizadas (1:N) - terceiros autorizados operações (PF)
│   └── TipoVinculo (N:1)
├── ContasDestino (1:N) - contas transferência recorrente
│   └── Banco (N:1)
├── EmpresasControladas (1:N) - empresas controladas (PJ)
├── EmpresasColigadas (1:N) - empresas coligadas (PJ)
├── SociosPPE (1:N) - pessoas politicamente expostas (PJ)
│   └── TipoVinculo (N:1)
├── NaturezaJuridica (N:1) - tipo empresa (PJ)
├── AtividadeEconomica (N:1) - CNAE (PJ)
├── ServicoConta (1:1) - configuração conta corrente (PJ)
├── ServicoInternetBanking (1:1) - configuração IB (PJ)
│   └── UsuariosAdmin (1:N) - usuários administradores IB
├── ServicoCobranca (1:1) - configuração cobrança bancária (PJ)
├── ServicoPacotes (1:1) - pacote tarifário selecionado (PJ)
├── ServicoInvestimentos (1:1) - configuração investimentos (PJ)
│   └── PessoasAutorizadas (1:N) - procuradores investimentos
├── DadosKYC (1:1) - Know Your Customer
│   ├── PaisesNegociacao (N:N)
│   ├── PaisesRelacionamento (N:N)
│   ├── PaisesOrigemRecursos (N:N)
│   └── NaturezasCambio (N:N)
└── Documentos (1:N) - arquivos upload (estatuto, balanço, RG, etc)
    └── TipoDocumento (N:1)
```

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Prospects | Tabela | SELECT | Consulta dados prospect existente para edição/continuação |
| Officers | Tabela | SELECT | Lista gestores disponíveis para atribuição |
| EstadoCivil | Tabela | SELECT | Lista estados civis (solteiro, casado, etc) |
| Paises | Tabela | SELECT | Lista países para nacionalidade, domicílio fiscal, KYC |
| Cidades | Tabela | SELECT | Lista cidades por UF para naturalidade, endereços |
| UF | Tabela | SELECT | Lista unidades federativas |
| TipoDocumento | Tabela | SELECT | Tipos documentos (RG, CNH, Passaporte) |
| OcupacaoProfissional | Tabela | SELECT | Lista ocupações profissionais |
| Profissao | Tabela | SELECT | Lista profissões |
| Cargo | Tabela | SELECT | Lista cargos |
| Bancos | Tabela | SELECT | Lista bancos para conta destino |
| NaturezaJuridica | Tabela | SELECT | Lista naturezas jurídicas (SA, LTDA, etc) |
| AtividadeEconomica | Tabela | SELECT | Lista CNAEs atividades econômicas |
| Relacionamento | Tabela | SELECT | Validação CNPJ com relacionamento ativo (tipo 11) |
| Termos | Tabela | SELECT | Conteúdo HTML termos contratuais |
| Rotas | Tabela | SELECT | Configuração rotas dinâmicas por perfil/fase |
| LISTA_DOCUMENTO (constante) | Constante | READ | Metadados documentos obrigatórios por natureza jurídica |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Prospects | Tabela | INSERT | Inclusão inicial prospect via `/incluirCadastroProspect` |
| Prospects | Tabela | UPDATE | Atualização dados prospect via `/alterarDadosProspect` (todas etapas) |
| Prospects.faseAtualizacao | Coluna | UPDATE | Controle etapa atual cadastro (1-7 PF, 1-6 PJ) |
| Prospects.tipoEdicao | Coluna | UPDATE | Flag modo edição ('S') vs continuação ('N') |
| Prospects.dadosBasicos | Coluna | UPDATE | Dados iniciais (CPF/CNPJ, nome, contato, officer) |
| Prospects.dadosPessoais | Coluna | UPDATE | Dados pessoais PF (sexo, filiação, documentos, estado civil) |
| Prospects.endereco | Coluna | UPDATE | Endereços residencial/comercial/fiscal |
| Prospects.dadosProfissionais | Coluna | UPDATE | Ocupação, profissão, cargo, empresa |
| Prospects.dadosFinanceiros | Coluna | UPDATE | Patrimônio, renda, origem recursos |
| Prospects.infoAdicionais | Coluna | UPDATE | Terceiros, contas destino, gestão patrimonial, empresas ctrl/colig, PPE, FATCA |
| Prospects.servicosPJ | Coluna | UPDATE | Configurações serviços PJ (conta, IB, cobrança, pacotes, investimentos) |
| Prospects.dadosKYC | Coluna | UPDATE | Países negociação/relacionamento, naturezas câmbio |
| Documentos | Tabela | INSERT | Upload arquivos via `/documento/upload/incluir` |
| Documentos | Tabela | UPDATE | Finalização upload via `/documento/salvar/upload` |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Estatuto Social / Contrato Social (PDF) | Leitura | CaixaDocumentoComponent, DocumentosPjComponent | Upload documento constitutivo PJ (código tipo 7) |
| Ata Eleição Diretoria (PDF) | Leitura | CaixaDocumentoComponent, DocumentosPjComponent | Upload ata eleição (código tipo 6) |
| Balanço Patrimonial (PDF) | Leitura | CaixaDocumentoComponent, DocumentosPjComponent | Upload balanço (código tipo 23) |
| RG Beneficiários (PDF) | Leitura | CaixaDocumentoComponent, DocumentosPjComponent | Upload RG representantes legais (código tipo 4) |
| Procurações (PDF) | Leitura | CaixaDocumentoComponent, DocumentosPjComponent | Upload procurações (códigos tipo 97, 9) |
| RG/CNH Pessoa Física (imagem/PDF) | Leitura | CaixaDocumentoComponent | Upload documento identidade PF |
| Contrato Abertura Conta (PDF) | Gravação | ApiContratosService, PjConclusaoComponent, ConclusaoComponent | Geração PDF contrato via `/gerarContrato`, download como `{CNPJ/CPF}_{razaoSocial/nome}.pdf` |
| Logs aplicação | Gravação | Console, LogService (não detalhado) | Logs erros/debug navegador |

---

## 10. Filas Lidas

Não se aplica.

---

## 11. Filas Geradas

Não se aplica.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo Integração | Breve Descrição |
|-----------------|-----------------|-----------------|
| **springboot-intb-onda-bff-cadastro-digital** | API REST (BFF) | Backend For Frontend principal: CRUD prospects, listas domínio, validações, geração contratos |
| **Serviço Busca CEP** | API REST | Consulta endereço por CEP via `/obterEnderecoCep/` (provavelmente ViaCEP ou similar) |
| **GED (Gestão Eletrônica Documentos)** | API REST | Sistema armazenamento documentos via `/documento/upload/incluir` e `/documento/salvar/upload` |
| **Serviço Validação Hash** | API REST | Validação temporal hash acesso via `/validarHashAcesso` |
| **Serviço Relacionamento** | API REST | Consulta relacionamento CNPJ ativo via `/consultarRelacionamento` |
| **Serviço Termos Contratuais** | API REST | Obtenção conteúdo HTML termos via `/obterTermos` |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**

**Pontos Positivos:**
- **Separação de Responsabilidades:** Arquitetura bem definida com separação clara entre componentes (UI), services (lógica negócio/integração) e models (DTOs)
- **Testes Unitários:** Cobertura de testes com Jest presente em praticamente todos services e components
- **Validações Robustas:** Uso extensivo de Reactive Forms com validações customizadas (CPF, nome completo, CEP, telefone)
- **Reutilização:** Componentes reutilizáveis como `CaixaDocumentoComponent` (drag-drop upload)
- **Tipagem Forte:** Uso consistente de TypeScript com interfaces e models tipados
- **Interceptors:** Implementação de interceptor global para loader e tratamento HTTP
- **State Management:** Uso adequado de RxJS BehaviorSubject para sincronização entre componentes
- **Validações Condicionais:** Lógica complexa de validações dinâmicas baseadas em flags (ex: FATCA, transferenciaRecorrente)
- **Progress Tracking:** Implementação de tracking upload com HttpEventType
- **Modo Edição:** Suporte completo a edição parcial e continuação de cadastros

**Pontos de Melhoria:**
- **Complexidade Componentes:** Alguns componentes (ex: `PJServicosComponent`, `DadosConfirmacaoComponent`) possuem muita lógica, poderiam ser refatorados em sub-componentes menores
- **Duplicação Código:** Lógica de parse Prospect ↔ Form repetida em múltiplos services, poderia ser centralizada em mappers genéricos
- **Documentação:** Falta de JSDoc em métodos complexos, dificultando manutenção
- **Magic Numbers:** Uso de códigos hardcoded (ex: tipo relacionamento 11, códigos pacotes 142-146) sem constantes nomeadas
- **Tratamento Erros:** Tratamento de erros HTTP poderia ser mais robusto com retry logic e mensagens específicas
- **Acessibilidade:** Falta de atributos ARIA em alguns componentes Material customizados

---

## 14. Observações Relevantes

- **Multi-Ambiente:** Configuração para múltiplos ambientes (des, qa, uat, prd) via `environment.ts`
- **SSR Habilitado:** Server-Side Rendering configurado para SEO e performance inicial
- **Mock Server:** json-server configurado para desenvolvimento local sem dependência do BFF
- **E2E Tests:** Testes end-to-end com Protractor configurados
- **Progress Bar Multi-Step:** Componente visual indicando progresso cadastral (7 etapas PF, 6 etapas PJ)
- **Validações Custom:** Implementação de validators customizados (CPF, nome completo, CEP, telefone brasileiro)
- **Guards Navegação:** Controle de navegação impedindo acesso a etapas sem completar anteriores
- **Modo Edição vs Continuação:** Sistema diferencia edição completa (`tipoEdicao='S'`) de continuação cadastro interrompido
- **Upload com Progress:** Tracking real-time de upload com barra de progresso por arquivo
- **Rotas Dinâmicas:** Navegação adaptativa baseada em contexto usuário (officer vs prospect), fase atual e tipo edição
- **RouteReuseStrategy:** Estratégia customizada para reuso de componentes e manutenção de estado
- **Máscaras Monetárias:** Uso de ngx-currency para formatação valores com R$ e separadores
- **Autocomplete Inteligente:** Listas de domínio com filtro em tempo real (profissões, cidades, bancos)
- **Validação Interdependente:** Campos com validações que dependem de outros campos (ex: cheque empresarial só para conta corrente)
- **Limite Arrays Dinâmicos:** Controle de máximo de itens em FormArrays (terceiros, empresas, usuários)
- **Preview Documentos:** Visualização prévia de PDFs/imagens antes do upload
- **Drag-and-Drop:** Interface intuitiva para upload de múltiplos arquivos
- **Geração PDF Server-Side:** Contrato gerado no backend e retornado como Blob para download
- **Hash Temporal:** Segurança via hash com validade temporal para acesso ao cadastro
- **Framework Interno:** Uso de bibliotecas internas `@intb/ui` e `@arqt/spa-framework` do Banco Votorantim