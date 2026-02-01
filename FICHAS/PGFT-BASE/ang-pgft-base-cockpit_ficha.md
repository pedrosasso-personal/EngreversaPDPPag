# Ficha Técnica do Sistema

## 1. Descrição Geral

O **ang-pgft-base-cockpit** é uma aplicação front-end desenvolvida em Angular 7 que funciona como um cockpit (painel de controle) para o sistema PGFT (Plataforma de Gestão de Fluxo Transacional) do Banco Votorantim. A aplicação oferece uma interface centralizada para monitoramento e gestão de diversas operações bancárias, incluindo transações de débito, abertura e encerramento de contas, desbloqueio de cartões, consumo de tributos, saldo bloqueado e cobrança indevida. O sistema utiliza uma arquitetura modular com lazy loading, gerenciamento de estado via NgRx, e está preparado para funcionar como PWA (Progressive Web App).

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AppComponent** | Componente raiz da aplicação, responsável pelo bootstrap inicial |
| **MenuNavigationComponent** | Gerencia o menu lateral de navegação, controle de rotas e autenticação do usuário |
| **PainelGeralComponent** | Componente da página inicial (home) do sistema |
| **HttpLoadingInterceptor** | Interceptor HTTP que gerencia indicadores de carregamento durante requisições |
| **httpLoadingReducer** | Reducer do NgRx para gerenciamento do estado de loading das requisições HTTP |
| **AppConfigurationService** | Serviço de configuração da aplicação, gerencia variáveis de ambiente |
| **ItemMenu** | Modelo de dados para itens do menu de navegação |
| **HttpLoading** | Modelo de dados para controle de estado de carregamento |
| **AccessRoles** | Classe estática contendo todas as roles de acesso do sistema |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal para desenvolvimento front-end
- **TypeScript 3.1.6** - Linguagem de programação
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **NgRx Store 10.0.1** - Gerenciamento de estado da aplicação
- **RxJS 6.3.3** - Programação reativa
- **Angular Flex Layout 7.0.0** - Sistema de layout responsivo
- **Chart.js 2.9.3 / ng2-charts** - Visualização de gráficos
- **@arqt/spa-framework 1.8.5** - Framework interno do Banco Votorantim para SPAs
- **@cpbd/commons 0.14.0** - Biblioteca de componentes compartilhados
- **Jest 23.6.0** - Framework de testes unitários
- **Protractor 5.4.0** - Framework de testes E2E
- **Service Worker** - Suporte a PWA
- **Apache HTTP Server (httpd-24-rhel7)** - Servidor web para produção
- **Docker** - Containerização da aplicação
- **OpenShift** - Plataforma de deployment (configurações para DES, QA, UAT, PRD)
- **SonarQube** - Análise estática de código
- **json-server** - Mock server para desenvolvimento local

---

## 4. Principais Endpoints REST

Com base nos arquivos de mock e configuração, os principais endpoints consumidos são:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | /api-utils/status | Health check do backend |
| POST | /api-utils/logger | Envio de logs do frontend |
| GET | /api-security/user/roles | Obtenção de roles do usuário |
| GET | /api-security/me | Obtenção de dados do usuário autenticado |
| POST | /api-security/logout | Logout do usuário |
| GET | /pgft/painel-geral/v1/cartao/debito/home/card | Card de débito na home |
| GET | /pgft/painel-geral/v1/home/card-abertura-conta | Card de abertura de conta na home |
| GET | /pgft/painel-geral/v1/home/card-consumo-tributo | Card de consumo de tributo na home |
| GET | /pgft/painel-geral/v1/home/card-encerramento-conta | Card de encerramento de conta na home |
| GET | /pgft/painel-geral/v1/home/card-saldo-bloqueado | Card de saldo bloqueado na home |
| GET | /pgft/painel-geral/v1/home/card-cobranca-indevida | Card de cobrança indevida na home |
| GET | /pgft/monitoramento-esteiras/v1/monitoramento-esteiras/status-esteiras | Status das esteiras de processamento |
| GET | /v1/contaTransacao | Transações de conta |
| GET | /v1/contaTransacaoAnalitico | Detalhamento analítico de transações |

**Nota:** O backend real é acessado via proxy configurado em `/api`, apontando para `https://springboot-pgft-base-bff-cockpit.appdes.bvnet.bv/`

---

## 5. Principais Regras de Negócio

1. **Controle de Acesso Baseado em Roles**: O sistema implementa controle granular de acesso através de roles específicas para cada funcionalidade e ambiente (DES, UAT, PRD)

2. **Monitoramento de Transações**: Acompanhamento de transações de débito, incluindo aprovadas, negadas e análise PLD

3. **Gestão de Abertura de Contas**: Monitoramento do processo de abertura de contas com indicadores de solicitações aprovadas e contas abertas

4. **Gestão de Encerramento de Contas**: Controle de encerramentos por iniciativa do banco, cliente ou emergencial, com aging de dias

5. **Desbloqueio de Cartões**: Funcionalidade para desbloqueio múltiplo de cartões

6. **Saldo Bloqueado**: Monitoramento de valores e quantidades de saldos bloqueados

7. **Cobrança Indevida**: Acompanhamento de cobranças indevidas com valores e quantidades

8. **Consumo de Tributos**: Monitoramento de pagamentos de contas e tributos

9. **Indicadores de Alerta**: Sistema de warnings para situações que requerem atenção

10. **Logging Centralizado**: Captura e envio de logs de erro e informação para backend

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **ItemMenu**: Representa itens do menu de navegação
  - Atributos: icon, name, route, subItems[], roles[]
  - Relacionamento: auto-relacionamento (subItems)

- **HttpLoading**: Controla estado de carregamento
  - Atributos: isLoading, elements
  - Usado pelo interceptor e reducer

- **ActionModel**: Modelo de ações do NgRx
  - Atributos: type, payload
  - Implementa interface Action do NgRx

- **AccessRoles**: Classe estática com constantes de roles
  - Contém arrays de strings com roles por funcionalidade e ambiente

**Fluxo de Dados:**
1. Componentes disparam ações (Actions)
2. Interceptor HTTP captura requisições e atualiza estado de loading
3. Reducers processam ações e atualizam Store
4. Componentes observam mudanças no Store via Observables
5. Template renderiza dados através de bindings

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação:** Esta é uma aplicação front-end que não acessa diretamente banco de dados. Todas as operações de dados são realizadas através de APIs REST do backend.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação:** Esta é uma aplicação front-end que não realiza operações diretas em banco de dados. Atualizações são feitas via APIs REST do backend.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Arquivos de configuração de ambiente (dev/prod) |
| manifest.json | leitura | Service Worker | Manifesto PWA com configurações da aplicação |
| ngsw-config.json | leitura | Service Worker | Configuração do Service Worker para cache |
| angular-httpd.conf | leitura | Apache HTTPD | Configuração do servidor web em produção |
| rotas.conf | leitura | Apache HTTPD | Configuração de proxy reverso por ambiente |
| data.json | leitura | json-server (dev) | Mock de dados para desenvolvimento local |
| routes.json | leitura | json-server (dev) | Mapeamento de rotas para mock server |
| tslint.report.json | gravação | npm scripts | Relatório de análise de código |
| test-report.xml | gravação | Jest | Relatório de testes unitários |
| coverage/lcov.info | gravação | Jest | Relatório de cobertura de testes |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| springboot-pgft-base-bff-cockpit | API REST | Backend principal da aplicação (BFF - Backend For Frontend) |
| @arqt/spa-framework | Biblioteca | Framework SPA interno do Banco Votorantim para autenticação, autorização e utilitários |
| @cpbd/commons | Biblioteca | Biblioteca de componentes compartilhados do banco |
| @arqt/ui | Biblioteca | Biblioteca de componentes UI do banco |
| SonarQube | Ferramenta | Análise estática de código (https://sonar.appdes.bvnet.bv) |
| Nexus | Repositório | Repositório NPM interno (https://nexus.bvnet.bv/repository/npm-group/) |
| OpenShift | Plataforma | Plataforma de deployment e orquestração de containers |

---

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades
- Uso adequado de padrões Angular (componentes, serviços, guards, interceptors)
- Implementação de gerenciamento de estado com NgRx
- Configuração adequada para múltiplos ambientes
- Presença de testes unitários e configuração de cobertura
- Uso de TypeScript com tipagem
- Implementação de PWA com Service Worker
- Configuração de CI/CD com Jenkins e OpenShift
- Controle de acesso granular por roles

**Pontos de Melhoria:**
- Código comentado no routing (componente BoletoDashHome)
- Falta de documentação inline em alguns componentes
- Alguns componentes com responsabilidades que poderiam ser melhor distribuídas
- Navegação hardcoded no ngOnInit do MenuNavigationComponent
- Uso de `any` em alguns tipos (ActionModel)
- Falta de tratamento de erros mais robusto em alguns observables
- Logs de erro extensos no mock sugerem problemas de roteamento durante desenvolvimento
- Variável `usuario` inicializada com string hardcoded antes da chamada assíncrona

---

## 14. Observações Relevantes

1. **Arquitetura Multi-Ambiente**: O sistema possui configurações específicas para 4 ambientes (DES, QA, UAT, PRD) com config-maps e deployment-configs separados

2. **Sistema de Roles Complexo**: Implementa um sistema sofisticado de controle de acesso com roles específicas por funcionalidade e ambiente

3. **PWA Ready**: Aplicação configurada como Progressive Web App com Service Worker e manifest

4. **Containerização**: Aplicação dockerizada usando imagem Red Hat (rhscl/httpd-24-rhel7) com Apache HTTPD

5. **Proxy Reverso**: Configuração de proxy para rotear chamadas `/api` para o backend BFF

6. **Mock Server**: Ambiente de desenvolvimento com json-server para simular APIs

7. **Compressão HTTP**: Configuração de compressão GZIP para diversos tipos de conteúdo

8. **Cache Strategy**: Implementação de estratégias de cache diferenciadas para index.html (no-cache) e assets (lazy loading)

9. **Monorepo**: Estrutura de projeto com biblioteca interna em `projects/pgft/cockpit`

10. **Integração com Framework Interno**: Forte dependência do framework SPA interno do banco (@arqt/spa-framework) para funcionalidades core

11. **Análise de Qualidade**: Integração com SonarQube para análise contínua de qualidade de código

12. **Logs de Erro**: Os mocks contêm diversos logs de erro relacionados a rotas não encontradas, sugerindo evolução da estrutura de rotas durante o desenvolvimento