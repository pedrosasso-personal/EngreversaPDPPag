# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema Angular de monitoramento de boletos e desbloqueio de cartões múltiplos (crédito/débito). Trata-se de uma aplicação frontend (SPA - Single Page Application) que fornece dashboards e relatórios analíticos para acompanhamento de operações de desbloqueio de cartões, com filtros por data, funcionalidade (crédito, débito ou ambos) e canal (APP ou Corporativo). O projeto também inclui uma biblioteca Angular (`monitoramento-boletos`) que pode ser empacotada e distribuída como componente reutilizável, inclusive com suporte a integração com aplicações AngularJS via Micro Frontend (MFE).

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `DesbloqueioCartaoMultiploComponent` | Componente principal de filtros e orquestração da tela de monitoramento |
| `DesbloqueioCartaoDashComponent` | Componente de visualização em dashboard (gráficos) |
| `DesbloqueioCartaoMultiploAnaliticoComponent` | Componente de visualização analítica (tabela detalhada) com exportação |
| `DesbloqueioCartaoMultiploService` | Serviço de integração com API backend para consultas de desbloqueio |
| `MonitoramentoDashService` | Serviço para buscar dados de parceiros no dashboard |
| `filterDesbloqueioReducer` | Reducer NgRx para gerenciar estado dos filtros de pesquisa |
| `funcionalidadeDesbloqueioReducer` | Reducer NgRx para gerenciar estado da funcionalidade selecionada |
| `AppComponent` | Componente raiz da aplicação |
| `AppConfigurationService` | Serviço de configuração da aplicação |

## 3. Tecnologias Utilizadas
- **Framework Frontend:** Angular 7.1.4
- **Gerenciamento de Estado:** NgRx Store 10.0.1
- **UI Components:** Angular Material 7.1.1, Angular CDK 7.1.1
- **Gráficos:** ng2-charts 2.2.0 (Chart.js 2.9.3), ngx-charts 14.0.0, ng-apexcharts 1.7.0 (ApexCharts 3.33.1)
- **Layout:** Angular Flex Layout 7.0.0-beta.24
- **Build/Deploy:** Docker (httpd-24-rhel7)
- **Servidor Web:** Apache HTTP Server (httpd)
- **Orquestração:** OpenShift
- **Linguagem:** TypeScript 3.1.6
- **Estilização:** SCSS (node-sass 4.11.0)
- **Bibliotecas Internas:** @arqt/spa-framework 1.8.5, @arqt/ui 1.5.0, @cpbd/commons 0.12.0
- **Testes:** Jest 23.6.0, jest-preset-angular 7.0.0, jest-junit 12.0.0
- **Qualidade de Código:** TSLint 5.11.0, @arqt/tslint 1.0.0, Stylelint 9.9.0, SonarQube (@arqt/sonar-scanner 1.0.0)
- **Documentação:** Compodoc 1.1.7
- **Utilitários:** Moment.js 2.22.2, HammerJS 2.0.8, JSEncrypt 3.0.0-rc.1, XLSX 0.16.7
- **Storage:** ngx-webstorage-service 3.1.1
- **Mock Server:** json-server 0.14.0
- **Build Tools:** Angular CLI 7.1.4, ng-packagr 4.4.0, webpack-bundle-analyzer 3.0.0
- **SSR (Server-Side Rendering):** @nguniversal/express-engine 7.0.2
- **PWA:** @angular/service-worker 7.1.4
- **Node.js:** >= 8.9.3
- **NPM:** >= 5.5.1

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/cpbd/cartao-multiplo/v1/consulta/{funcionalidade}/desbloqueio` | DesbloqueioCartaoMultiploService | Consulta dados agregados de desbloqueio (dashboard) |
| GET | `/cpbd/cartao-multiplo/v1/consulta/{funcionalidade}/desbloqueio-analitico` | DesbloqueioCartaoMultiploService | Consulta dados analíticos detalhados de desbloqueio |
| GET | `/v1/dash-monitoramento/visao-geral/1` | MonitoramentoDashService | Busca dados de parceiros para visão geral |
| GET | `/api-utils/status` | N/A (configuração) | Health check do backend |
| POST | `/api-utils/logger` | N/A (configuração) | Envio de logs |
| POST | `/j_security_check` | N/A (mock) | Autenticação |
| GET | `/api-security/user/roles` | N/A (mock) | Consulta roles do usuário |
| GET | `/api-security/me` | N/A (mock) | Consulta dados do usuário logado |

**Nota:** Os endpoints com `{funcionalidade}` aceitam valores: `multiplo`, `credito` ou `debito`.

## 5. Principais Regras de Negócio
- Filtro de desbloqueios por intervalo de datas (data inicial e final obrigatórias)
- Segmentação por funcionalidade: Ambos (crédito+débito), apenas Crédito ou apenas Débito
- Segmentação por canal de origem: APP (BVPD) ou Corporativo (SFDC)
- Classificação de situações: Sucesso, Processo, Erro
- Ocultação dinâmica de colunas na visualização analítica conforme funcionalidade selecionada
- Exportação de dados analíticos para formato XLSX
- Conversão e formatação de datas para padrão brasileiro (DD/MM/YYYY HH:mm:ss)
- Concatenação de códigos de erro e detalhes para exibição unificada
- Paginação e ordenação de dados na visualização analítica
- Filtro de busca textual na tabela analítica
- Validação de intervalo de datas antes de permitir pesquisa

## 6. Relação entre Entidades

**Entidades Principais:**

- **DesbloqueioCartaoMultiploFilter:** Filtro de pesquisa (dataInicial, dataFinal)
- **DesbloqueioCartaoFuncionalidade:** Configuração de funcionalidade e canal
- **DesbloqueioCartao:** Dados agregados (sucesso, processo, erro, total)
- **DesbloqueioCartaoMultiploAnalitico:** Dados detalhados de cada desbloqueio
- **Parceiro:** Dados de parceiros (nome, cor, valor, quantidade)

**Relacionamentos:**
- Um filtro (DesbloqueioCartaoMultiploFilter) + uma funcionalidade (DesbloqueioCartaoFuncionalidade) geram múltiplos registros analíticos (DesbloqueioCartaoMultiploAnalitico)
- Cada registro analítico contém informações de cartão, CPF/CNPJ, conta, produto, datas de solicitação/retorno para crédito e/ou débito

## 7. Estruturas de Banco de Dados Lidas
não se aplica (aplicação frontend consome APIs REST)

## 8. Estruturas de Banco de Dados Atualizadas
não se aplica (aplicação frontend consome APIs REST)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Arquivos de configuração de ambiente (dev/prod) |
| angular-httpd.conf | leitura | Docker/Apache | Configuração do servidor HTTP Apache |
| rotas.conf | leitura | OpenShift ConfigMap | Configuração de proxy reverso para APIs |
| manifest.json | leitura | Service Worker | Manifesto PWA da aplicação |
| *.xlsx (gerado dinamicamente) | gravação | ExportarXlsxService | Exportação de dados analíticos para Excel |
| package.json | leitura | NPM/Build | Configuração de dependências e scripts do projeto |
| tsconfig.json | leitura | TypeScript Compiler | Configuração do compilador TypeScript |
| tslint.json | leitura | TSLint | Configuração de regras de linting |
| sonar-project.properties | leitura | SonarQube Scanner | Configuração de análise estática de código |
| tslint.report.json | gravação | TSLint | Relatório de linting em formato JSON para SonarQube |
| test-report.xml | gravação | Jest | Relatório de execução de testes para SonarQube |
| coverage/lcov.info | gravação | Jest | Relatório de cobertura de testes |
| mocks/data.json | leitura | json-server | Dados mockados para desenvolvimento local |
| mocks/routes.json | leitura | json-server | Configuração de rotas mockadas |
| dist/pgft/monitoramento-boletos/mfe-example.js | gravação | Build MFE | Bundle consolidado para integração Micro Frontend |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| API Backend (springboot-arqt-refe-conecta-techday) | REST API | Backend principal para consultas de desbloqueio de cartões |
| sboot-pgft-base-atom-dash-boleto | REST API | Serviço de dashboard para visão geral de parceiros |
| /api-utils/status | REST API | Serviço de health check |
| /api-utils/logger | REST API | Serviço de logging centralizado |
| /api-security/* | REST API | Serviços de autenticação e autorização |
| Nexus NPM Registry | NPM Repository | Repositório corporativo de pacotes NPM (https://nexus.bvnet.bv/repository/npm-group/) |
| SonarQube | Análise Estática | Plataforma de qualidade de código (https://sonar.appdes.bvnet.bv) |

## 13. Avaliação da Qualidade do Código

**Nota:** 7.5/10

**Justificativa:**
- **Pontos Positivos:** 
  - Boa organização modular com separação de responsabilidades (componentes, serviços, models, reducers)
  - Uso adequado de padrões Angular (NgRx para gerenciamento de estado)
  - Tipagem TypeScript consistente
  - Componentização adequada
  - Uso de Observables e RxJS
  - Infraestrutura completa de testes (Jest com cobertura)
  - Integração com ferramentas de qualidade (TSLint, SonarQube)
  - Documentação automatizada (Compodoc)
  - Suporte a múltiplos formatos de build (SPA, biblioteca, MFE)
  - Configuração de análise de bundle (webpack-bundle-analyzer)
  - Exclusões bem definidas para análise de cobertura
  
- **Pontos de Melhoria:** 
  - Presença de código comentado
  - URLs hardcoded em serviços (deveria usar configuração)
  - Lógica de negócio complexa dentro de componentes (deveria estar em serviços)
  - Falta de tratamento de erro mais robusto
  - Alguns métodos muito extensos (ex: obterDesbloqueios)
  - Uso de `any` em alguns tipos
  - Conversão de datas poderia ser centralizada em um pipe/service
  - Versões de algumas dependências desatualizadas (Angular 7 já possui versões mais recentes)

## 14. Observações Relevantes
- Aplicação configurada para deploy em OpenShift com Docker
- Suporte a PWA (Progressive Web App) com Service Worker
- Configuração de proxy reverso Apache para rotear chamadas `/api` para backend
- Uso de compressão GZIP para otimização de assets
- Cache desabilitado para index.html (sempre busca versão mais recente)
- Aplicação multi-ambiente (dev, qa, uat, prd)
- Tema corporativo do Banco Votorantim
- Suporte a múltiplos idiomas (pt-BR configurado)
- Lazy loading de fontes para otimização de performance
- Mocks configurados para desenvolvimento local via json-server (porta 3200)
- Projeto configurado para geração de biblioteca Angular reutilizável (`monitoramento-boletos`)
- Suporte a Micro Frontend (MFE) para integração com aplicações AngularJS legadas
- Servidor de desenvolvimento na porta 4200
- Servidor de distribuição (http-server) na porta 8090
- Documentação interativa via Compodoc na porta 9080
- Requisitos mínimos: Node.js >= 8.9.3, NPM >= 5.5.1
- Recomendação de uso do NVM para gerenciamento de versões do Node.js
- Configuração de SSL desabilitada para repositório NPM corporativo
- Análise de cobertura de testes configurada para 100% (compodoc:coverage)
- Relatórios de teste em formato JUnit para integração CI/CD
- Exclusões de cobertura bem definidas (models, DTOs, modules, resolvers, interfaces, environments)

## 15. Histórico da Iteração

### Iteração 1
- Análise inicial da estrutura do projeto Angular
- Documentação de componentes principais de monitoramento de boletos e desbloqueio de cartões
- Identificação de tecnologias (Angular 7, NgRx, Material, ng2-charts)
- Mapeamento de endpoints REST consumidos
- Documentação de regras de negócio de filtros e visualizações
- Identificação de integrações com APIs backend
- Documentação de configurações Docker e OpenShift
- Avaliação inicial da qualidade do código

### Iteração 2 (atual)
- Análise detalhada do `package.json` com identificação completa de dependências e versões
- Documentação de bibliotecas de gráficos adicionais (ngx-charts, ApexCharts)
- Identificação de ferramentas de qualidade e testes (Jest, TSLint, SonarQube, Compodoc)
- Mapeamento de scripts NPM disponíveis (build, test, lint, sonar, lib, mfe)
- Documentação de arquivos de configuração (sonar-project.properties, tsconfig, tslint)
- Identificação de suporte a biblioteca Angular reutilizável e Micro Frontend
- Documentação de integração com Nexus NPM Registry corporativo
- Detalhamento de requisitos de ambiente (Node.js, NPM)
- Atualização da avaliação de qualidade do código (7.0 → 7.5) considerando infraestrutura de testes e qualidade
- Documentação de portas utilizadas pelos servidores (4200, 3200, 8090, 9080)
- Identificação de arquivos gerados (relatórios de teste, cobertura, lint, bundles MFE)