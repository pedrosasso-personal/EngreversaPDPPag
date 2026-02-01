# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema Angular 11 para gerenciamento de extrato de conta do Banco Votorantim (BV). Trata-se de uma aplicação SPA (Single Page Application) baseada na arquitetura corporativa do banco, utilizando o framework @arqt/spa-framework. O projeto está estruturado como uma biblioteca Angular reutilizável (@intb/extrato-conta) que pode ser consumida por outras aplicações ou exportada como micro-frontend (MFE) para integração com sistemas AngularJS legados.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AppComponent** | Componente raiz da aplicação, responsável por inicializar o sistema |
| **AppModule** | Módulo principal que configura a aplicação, importa BvCoreModule e ExtratoContaModule |
| **ExtratoContaModule** | Módulo da biblioteca que encapsula funcionalidades de extrato de conta |
| **ExampleComponent** | Componente de exemplo/demonstração da biblioteca |
| **ExampleService** | Serviço de exemplo para lógica de negócio |
| **AppRoutingModule** | Módulo de roteamento da aplicação (atualmente sem rotas configuradas) |

## 3. Tecnologias Utilizadas

- **Framework Frontend:** Angular 11.2.9
- **Linguagem:** TypeScript 4.1.5
- **UI Components:** 
  - Angular Material 11.2.9
  - Foundation UI (Stencil Components) 1.11.0
  - @arqt/ng-ui 0.1.0
- **Frameworks Corporativos:**
  - @arqt/spa-framework 2021.521.1244-SNAPSHOT
  - @arqt/ng-framework 0.1.0
  - @intb/commons 2021.629.1217-SNAPSHOT
- **Estilização:** SCSS/SASS 1.32.11
- **Testes:** Jest 26.6.3, Protractor 7.0.0
- **Build:** Angular CLI 11.2.9, ng-packagr 11.2.4
- **Utilitários:** RxJS 6.6.7, Moment.js 2.29.1, Crypto-js 4.0.0, JSEncrypt 3.2.0
- **Service Worker:** @angular/service-worker (PWA support)
- **Análise de Código:** TSLint 6.1.3, Stylelint 13.13.0, SonarQube

## 4. Principais Endpoints REST

Não se aplica. Esta é uma aplicação frontend Angular que consome APIs através de configurações centralizadas no BvCoreModule. Os endpoints são configurados via `environment.apiBvConfigs`:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| /api-utils/status | GET | Health-check do backend |
| /api-utils/logger | POST | Envio de logs para backend |
| /v2/api-docs | GET | Documentação Swagger da API |

## 5. Principais Regras de Negócio

Não há regras de negócio implementadas no código fornecido. O projeto contém apenas componentes e serviços de exemplo (ExampleComponent e ExampleService) sem lógica de negócio específica. Trata-se de uma estrutura base/template para desenvolvimento de funcionalidades de extrato de conta.

## 6. Relação entre Entidades

Não se aplica. O código fornecido não contém definição de entidades de domínio ou modelos de dados. Apenas componentes e serviços vazios de exemplo.

## 7. Estruturas de Banco de Dados Lidas

Não se aplica. A aplicação frontend não acessa diretamente banco de dados. O acesso a dados é realizado através de APIs REST configuradas no backend.

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. A aplicação frontend não realiza operações diretas em banco de dados.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts / environment.prod.ts | Leitura | AppModule (bootstrap) | Configurações de ambiente (URLs de API, chaves públicas, nível de log) |
| manifest.json | Leitura | Service Worker | Manifesto PWA para instalação da aplicação |
| lazy-fonts.css | Leitura | index.html | Carregamento lazy de fontes corporativas |
| foundation-ui.css | Leitura | angular.json | Estilos dos componentes Foundation UI |
| assets/icons/* | Leitura | index.html | Ícones da aplicação (PWA) |

## 10. Filas Lidas

Não se aplica. Não há evidências de consumo de filas (JMS, Kafka, RabbitMQ) no código fornecido.

## 11. Filas Geradas

Não se aplica. Não há evidências de publicação em filas no código fornecido.

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Backend API (apiBv) | REST API | Integração com APIs backend através de configuração centralizada no BvCoreModule |
| Foundation UI | Web Components | Biblioteca de componentes Stencil do BV |
| @arqt/spa-framework | Framework Corporativo | Framework SPA do Banco Votorantim |
| @intb/commons | Biblioteca Compartilhada | Componentes e utilitários comuns do Internet Banking |

**Ambiente de Desenvolvimento:** http://localhost:3200  
**Ambiente de Produção:** /api (path relativo)

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrões Angular
- Uso de bibliotecas corporativas padronizadas
- Configuração adequada de ambientes (dev/prod)
- Suporte a PWA e Service Workers
- Configuração de testes unitários (Jest) e E2E (Protractor)
- Build otimizado para produção com AOT e tree-shaking
- Uso de SCSS com arquitetura modular de estilos

**Pontos Negativos:**
- Código extremamente básico, apenas estrutura de exemplo sem implementação real
- Componentes e serviços vazios sem lógica de negócio
- Falta de documentação inline (comentários JSDoc)
- Ausência de tratamento de erros
- Nenhuma rota configurada no AppRoutingModule
- Falta de testes unitários implementados (apenas estrutura)
- Configuração de segurança exposta (chave pública hardcoded)
- Dependências com versões SNAPSHOT em produção

## 14. Observações Relevantes

1. **Projeto Template:** Este é claramente um projeto base/template gerado pela ferramenta de scaffolding do BV (versão 0.1.0), destinado a ser customizado para implementação de funcionalidades específicas de extrato de conta.

2. **Arquitetura de Biblioteca:** O projeto está estruturado como uma biblioteca Angular (@intb/extrato-conta) que pode ser:
   - Instalada como dependência NPM em outras aplicações Angular
   - Exportada como micro-frontend (MFE) para integração com AngularJS legado (comando `npm run build:lib:angularjs`)

3. **Segurança:** Utiliza criptografia RSA (JSEncrypt) com chave pública para comunicação segura. A chave está hardcoded nos arquivos de environment, o que pode ser um ponto de atenção para segurança.

4. **PWA Ready:** Aplicação configurada como Progressive Web App com suporte a Service Workers, manifesto e ícones para instalação em dispositivos móveis.

5. **Tema Corporativo:** Utiliza tema "corporativo" do BV com fontes e estilos padronizados da biblioteca @arqt/ng-ui.

6. **Pipeline CI/CD:** Configurado para Jenkins (jenkins.properties) e análise de código com SonarQube.

7. **Versão SNAPSHOT:** O projeto está em versão 1.0.0-SNAPSHOT, indicando desenvolvimento ativo e não recomendado para produção.

8. **Node.js:** Requer Node.js >= 10.24.1 e NPM >= 6.14.12, com recomendação de uso do Node 14.16.1.