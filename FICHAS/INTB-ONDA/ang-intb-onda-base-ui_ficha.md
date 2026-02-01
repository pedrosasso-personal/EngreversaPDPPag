# Ficha Técnica do Sistema

## 1. Descrição Geral

Este é um projeto de **biblioteca de componentes UI reutilizáveis** desenvolvido em **Angular** (framework TypeScript para aplicações web SPA - Single Page Application). A biblioteca fornece componentes visuais padronizados e estilizados para aplicações frontend, incluindo notificações, modais, datepickers, loaders, spinners, barras de progresso, drag-and-drop, toolbars e máscaras de entrada de dados. O projeto é estruturado como uma biblioteca Angular modular (`@intb/ui`) e está preparado para deploy em ambiente OpenShift com configurações para múltiplos ambientes (des, qa, uat, prd).

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `OndaMasks` | Classe utilitária para aplicação de máscaras em campos de entrada (ex: telefone) |
| `OndaInlineNotificationComponent` | Componente de notificações inline (avisos, sucessos, erros) |
| `OndaInlineNotificationService` | Serviço para gerenciar e exibir notificações inline |
| `OndaErrorNotificationComponent` | Componente específico para notificações de erro |
| `OndaNotificationService` | Serviço para gerenciar notificações padrão (warn, success, error) |
| `OndaDatepickerHeaderComponent` | Componente customizado de cabeçalho para datepicker |
| `OndaDragAndDropComponent` | Componente para upload de arquivos via drag-and-drop ou botão |
| `OndaDragAndDropDirective` | Diretiva para capturar eventos de drag-and-drop |
| `OndaLoaderComponent` | Componente de loader/spinner com overlay |
| `OndaLoaderOverlayService` | Serviço para gerenciar exibição do loader com overlay |
| `OndaModalComponent` | Componente de modal de confirmação/diálogo |
| `OndaProgressBarComponent` | Componente de barra de progresso com informações de etapas |
| `OndaProgressBarService` | Serviço para controlar progresso e atualizar barra |
| `OndaSpinnerComponent` | Componente de spinner simples |
| `OndaToolbarComponent` | Componente de toolbar com logo, usuário e logout |

---

## 3. Tecnologias Utilizadas

- **Angular** (~7.1.0) - Framework frontend
- **TypeScript** - Linguagem de programação
- **Angular Material** (~7.1.0) - Biblioteca de componentes UI
- **Angular CDK** - Kit de desenvolvimento de componentes
- **Material Icons** - Ícones do Google Material Design
- **Moment.js** (~2.22.2) - Manipulação de datas
- **@angular/material-moment-adapter** - Adaptador de datas para Material
- **RxJS** - Programação reativa (Observables)
- **SCSS/Sass** - Pré-processador CSS
- **@arqt/spa-framework** (~1.0.0) - Framework interno BV para SPAs
- **Apache HTTP Server** - Servidor web (configuração de proxy reverso)
- **OpenShift** - Plataforma de deploy e orquestração de containers

---

## 4. Principais Endpoints REST

**não se aplica** - Este é um projeto de biblioteca de componentes frontend (Angular), não possui endpoints REST próprios. As configurações de proxy reverso apontam para um backend externo:

| Ambiente | Backend Proxy |
|----------|---------------|
| DES/QA/UAT/PRD | `https://springboot-arqt-refe-conecta-techday.appdes.bvnet.bv` (via `/api`) |

---

## 5. Principais Regras de Negócio

**N/A** - Por se tratar de uma biblioteca de componentes UI reutilizáveis, não há regras de negócio específicas implementadas. Os componentes fornecem funcionalidades genéricas de interface:

- Validação e formatação de entrada de dados (máscaras)
- Gerenciamento de estado de notificações (sucesso, erro, aviso)
- Controle de progresso em processos multi-etapas
- Upload de arquivos com validação de drag-and-drop
- Autenticação e logout (integrado com framework BV)

---

## 6. Relação entre Entidades

**não se aplica** - Este projeto não possui entidades de domínio ou modelos de dados de negócio. Os modelos existentes são apenas interfaces TypeScript para configuração de componentes UI:

- `OndaDragAndDropConfigModel` - Configuração de drag-and-drop
- `OndaDragAndDropEmitModel` - Dados emitidos pelo drag-and-drop
- `LoaderDialogConfigModel` - Configuração do loader
- `ModalDialogConfigModel` - Configuração de modais
- `ProgressBarConfigModel` - Configuração de barra de progresso
- `ToolbarConfigModel` - Configuração da toolbar
- `UserModel` - Modelo de usuário (do framework BV)

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica** - Biblioteca de componentes frontend sem acesso direto a banco de dados.

---

## 8. Estruturas de Banco de Dados Atualizadas

**não se aplica** - Biblioteca de componentes frontend sem acesso direto a banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `rotas.conf` | Leitura | Apache HTTP Server (ConfigMap OpenShift) | Arquivo de configuração de proxy reverso para roteamento de requisições `/api` |
| Arquivos de upload (diversos) | Leitura | `OndaDragAndDropComponent` | Arquivos selecionados/arrastados pelo usuário para upload |
| Fontes Frutiger (*.woff, *.ttf, etc) | Leitura | Componentes Angular (assets) | Arquivos de fontes customizadas |
| Material Icons (*.woff, *.ttf, etc) | Leitura | Componentes Angular (assets) | Arquivos de ícones Material Design |

---

## 10. Filas Lidas

**não se aplica** - Biblioteca de componentes frontend sem integração com filas de mensagens.

---

## 11. Filas Geradas

**não se aplica** - Biblioteca de componentes frontend sem integração com filas de mensagens.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| `springboot-arqt-refe-conecta-techday.appdes.bvnet.bv` | API REST Backend | Backend Spring Boot integrado via proxy reverso Apache (rota `/api`) |
| `@arqt/spa-framework` | Biblioteca NPM | Framework interno BV para SPAs, fornece serviços de login, roles e componentes base |
| Angular Material | Biblioteca NPM | Biblioteca de componentes UI do Google |
| Moment.js | Biblioteca NPM | Biblioteca para manipulação de datas |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa modularização com separação clara de responsabilidades (cada componente em seu módulo)
- Uso adequado de serviços para lógica compartilhada
- Documentação JSDoc presente em várias classes
- Uso de TypeScript com interfaces/models bem definidos
- Aplicação de padrões Angular (ChangeDetectionStrategy, OnDestroy, Observables)
- Estrutura de projeto organizada e padronizada
- Configuração adequada para múltiplos ambientes (OpenShift)

**Pontos de Melhoria:**
- Código comentado não removido (ex: `onda-loader-overlay.service.ts`)
- Falta de testes unitários implementados (arquivos `.spec.ts` marcados como NAO_ENVIAR)
- Inconsistência na documentação (alguns componentes bem documentados, outros não)
- Uso de `any` em alguns tipos (ex: `data: any` em vários lugares)
- Falta de tratamento de erros em alguns observables
- Código em português misturado com inglês (comentários e nomes de variáveis)
- Algumas práticas podem ser melhoradas (ex: uso de `document.getElementById` no drag-and-drop)

---

## 14. Observações Relevantes

1. **Biblioteca Corporativa**: Este é um projeto de biblioteca de componentes UI reutilizável para uso interno no Banco Votorantim (BV), seguindo padrões de design system próprios (tema "Onda").

2. **Múltiplos Temas**: Suporta temas customizados (atacado, digital-express) com variáveis SCSS configuráveis.

3. **Deploy OpenShift**: Configurado para deploy em containers OpenShift com ConfigMaps para configuração de proxy reverso por ambiente.

4. **Dependência de Framework Interno**: Forte dependência do `@arqt/spa-framework`, framework proprietário do BV para SPAs.

5. **Fontes Customizadas**: Utiliza família tipográfica Frutiger (licenciada) como padrão visual.

6. **Integração com Material Design**: Extende e customiza componentes do Angular Material mantendo compatibilidade.

7. **Publicação NPM**: Estruturado como biblioteca Angular publicável via `ng-packagr` com múltiplos entry points.

8. **Versão Angular**: Projeto baseado em Angular 7.x (versão relativamente antiga, lançada em 2018).