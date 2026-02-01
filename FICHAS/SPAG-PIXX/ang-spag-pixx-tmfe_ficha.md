# Ficha Técnica do Sistema

## 1. Descrição Geral

Este é um **Micro Frontend (TMFE)** desenvolvido em Angular 7 para o sistema SPAG-PIXX do Banco Votorantim. Trata-se de uma biblioteca Angular configurada como Web Component (Angular Elements) com suporte a Progressive Web App (PWA). O projeto segue a arquitetura SPA (Single Page Application) do banco e é empacotado como uma biblioteca reutilizável que pode ser integrada em outras aplicações. A aplicação é containerizada com Docker e implantada no OpenShift.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AppModule** | Módulo raiz da aplicação, responsável por inicializar o micro frontend |
| **TmfeModule** | Módulo principal da biblioteca, exporta componentes reutilizáveis |
| **ExampleComponent** | Componente de exemplo para demonstração da estrutura |
| **ExampleService** | Serviço de exemplo para lógica de negócio |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework frontend principal
- **Angular Elements** - Para criação de Web Components
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **Angular Service Worker** - Suporte a PWA
- **TypeScript 3.1.6** - Linguagem de programação
- **RxJS 6.3.3** - Programação reativa
- **@arqt/spa-framework 1.8.5** - Framework SPA customizado do Banco Votorantim
- **@arqt/ui 1.3.0** - Biblioteca de componentes UI do banco
- **Jest** - Framework de testes unitários
- **Docker** - Containerização
- **Apache HTTP Server (httpd-24-rhel7)** - Servidor web
- **OpenShift** - Plataforma de deployment
- **Jenkins** - CI/CD
- **SonarQube** - Análise estática de código
- **Protractor** - Testes E2E
- **ng-packagr** - Empacotamento de bibliotecas Angular

---

## 4. Principais Endpoints REST

**não se aplica** - Este é um projeto frontend (Micro Frontend/Biblioteca Angular). Não possui endpoints REST próprios, apenas consome APIs backend configuradas através do `environment`.

---

## 5. Principais Regras de Negócio

Como este é um projeto de biblioteca/micro frontend base (template/boilerplate), não possui regras de negócio específicas implementadas. O projeto fornece:

- Estrutura base para desenvolvimento de micro frontends
- Configuração de ambiente para desenvolvimento e produção
- Integração com APIs backend através de proxy reverso
- Suporte a PWA com service workers
- Sistema de logging centralizado
- Criptografia de dados sensíveis com chave pública RSA

---

## 6. Relação entre Entidades

**não se aplica** - Por ser uma biblioteca base/template sem implementação de domínio específico, não há entidades de negócio definidas. O projeto fornece apenas componentes e serviços de exemplo (ExampleComponent e ExampleService).

---

## 7. Estruturas de Banco de Dados Lidas

**não se aplica** - Este é um projeto frontend que não acessa diretamente banco de dados. O acesso a dados é feito através de APIs REST backend.

---

## 8. Estruturas de Banco de Dados Atualizadas

**não se aplica** - Este é um projeto frontend que não acessa diretamente banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **manifest.json** | leitura | src/manifest.json | Manifesto PWA com configurações do aplicativo |
| **environment.ts** | leitura | src/environments/ | Configurações de ambiente (dev/prod) |
| **rotas.conf** | leitura | openshift-as-code/config-map/*/arquivos/ | Configuração de proxy reverso Apache por ambiente |
| **tslint.report.json** | gravação | Raiz do projeto | Relatório de análise estática TSLint |
| **test-report.xml** | gravação | Raiz do projeto | Relatório de execução de testes |
| **coverage/lcov.info** | gravação | coverage/ | Relatório de cobertura de testes |
| **dist/** | gravação | dist/ | Artefatos compilados da aplicação |

---

## 10. Filas Lidas

**não se aplica** - O projeto não consome mensagens de filas.

---

## 11. Filas Geradas

**não se aplica** - O projeto não publica mensagens em filas.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Backend (springboot-arqt-refe-conecta-techday)** | REST API | APIs de backend acessadas via proxy reverso configurado em rotas.conf |
| **API Utils (/api-utils/status)** | REST API | Health check do backend |
| **API Utils (/api-utils/logger)** | REST API | Serviço de logging centralizado |
| **API Security (/api-security/*)** | REST API | Serviços de autenticação e autorização |
| **Nexus NPM Registry** | Repositório | Repositório de pacotes NPM do banco (https://nexus.bvnet.bv) |
| **SonarQube** | Análise Estática | Análise de qualidade de código (https://sonar.appdes.bvnet.bv) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Estrutura bem organizada seguindo padrões Angular
- Uso de TypeScript com tipagem
- Configuração adequada de testes (Jest) e análise estática (TSLint, SonarQube)
- Boa separação de ambientes (dev/prod)
- Documentação básica presente (README)
- Configuração de CI/CD e containerização bem estruturada
- Uso de bibliotecas corporativas padronizadas (@arqt/*)

**Pontos de Melhoria:**
- Código muito básico/template, com apenas componentes de exemplo vazios
- Falta de implementação real de funcionalidades
- Ausência de testes unitários implementados (apenas estrutura)
- Comentários em código muito escassos
- Falta de documentação técnica detalhada (apenas README básico)
- Configuração de proxy hardcoded para ambiente de desenvolvimento
- Chave pública RSA exposta em código (deveria estar em variável de ambiente)

---

## 14. Observações Relevantes

1. **Arquitetura Micro Frontend**: O projeto é estruturado como uma biblioteca Angular que pode ser empacotada e distribuída como Web Component, permitindo integração com outras aplicações (inclusive AngularJS legado).

2. **Multi-ambiente**: Possui configurações específicas para 4 ambientes (DES, QA, UAT, PRD) com proxy reverso Apache configurado individualmente.

3. **PWA Ready**: Configurado com Service Worker e manifest para funcionar como Progressive Web App offline.

4. **Build Otimizado**: Utiliza AOT compilation, tree-shaking e build optimizer em produção.

5. **Segurança**: Implementa criptografia RSA para dados sensíveis, mas a chave pública está exposta no código-fonte (má prática).

6. **Monitoramento**: Integrado com sistema de logging centralizado e health check.

7. **Padrão Corporativo**: Segue a arquitetura SPA definida pelo Banco Votorantim com uso de bibliotecas internas (@arqt/*).

8. **Estado Atual**: Projeto em estado inicial/template, versão 0.2.0, sem funcionalidades de negócio implementadas.

9. **Deployment**: Containerizado com Apache HTTP Server em imagem Red Hat e orquestrado via OpenShift com ConfigMaps para configuração por ambiente.

10. **Pipeline**: Integrado com Jenkins para CI/CD conforme arquivo jenkins.properties.