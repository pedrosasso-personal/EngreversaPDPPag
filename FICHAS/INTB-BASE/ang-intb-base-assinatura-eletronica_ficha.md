# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web de assinatura eletrônica de contratos em lote para Internet Banking. Permite que usuários visualizem contratos pendentes de assinatura, assinem múltiplos contratos simultaneamente através de token eletrônico, e acompanhem o status do processamento. A aplicação apresenta um dashboard com cards informativos sobre contratos pendentes, assinados, concluídos e em desacordo, com foco na assinatura em lote de contratos pendentes.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AssinaturaComponent** | Componente raiz que encapsula o dashboard de assinatura |
| **DashboardComponent** | Orquestra a exibição do dashboard, cards, modal de assinatura e tela de resultado |
| **DashboardService** | Gerencia estado dos contratos, processamento e comunicação com API backend |
| **DashboardHeaderComponent** | Exibe título e valor total pendente de assinatura |
| **DashboardCardsComponent** | Renderiza cards com totalizadores de contratos por status |
| **SignatureCardComponent** | Card individual que exibe informações de um tipo de contrato e permite iniciar assinatura |
| **SignatureComponent** | Modal de assinatura que integra componente de token eletrônico |
| **SignatureService** | Controla visibilidade do modal de assinatura |
| **SignatureResultComponent** | Tela de feedback (sucesso/erro) após processamento da assinatura |
| **SignatureResultService** | Gerencia tipo de resultado a ser exibido |
| **DashboardDisclaimerComponent** | Exibe aviso informativo sobre funcionalidades adicionais no desktop |
| **AppConfigurationService** | Fornece configurações de ambiente para a aplicação |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **Angular Flex Layout 7.0.0** - Sistema de layout responsivo
- **RxJS 6.3.3** - Programação reativa
- **TypeScript 3.1.6** - Linguagem de programação
- **@arqt/spa-framework 1.8.5** - Framework corporativo BV
- **@intb/commons** - Biblioteca de componentes compartilhados (Token, Alert)
- **Angular Service Worker** - PWA capabilities
- **Moment.js 2.22.2** - Manipulação de datas
- **JSEncrypt 3.0.0** - Criptografia RSA
- **Jest 23.6.0** - Framework de testes
- **Docker** - Containerização
- **OpenShift** - Plataforma de deployment
- **JSON Server** - Mock de API para desenvolvimento

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/portal/contracts/signatureStatus` | DashboardService | Obtém status de processamento dos contratos pendentes |
| GET | `/v1/ib/portal/totalContracts` | DashboardService | Retorna quantidade de contratos por tipo e valor total pendente |
| POST | `/v1/ib/portal/saveEletronicSign` | SignatureComponent (via TokenModule) | Processa assinatura eletrônica em lote dos contratos |
| GET | `/api-utils/status` | ConfigurationModel | Health check do backend |
| POST | `/api-utils/logger` | ConfigurationModel | Envio de logs |

---

## 5. Principais Regras de Negócio

1. **Assinatura em Lote**: Apenas contratos com status "pendentes" podem ser assinados em lote através da aplicação mobile/web
2. **Polling de Processamento**: Sistema verifica status de processamento a cada 5 segundos quando há assinatura em andamento
3. **Validação de Token**: Assinatura requer validação através de token eletrônico (aplicação 2)
4. **Atualização Automática**: Dashboard é atualizado automaticamente após conclusão do processamento
5. **Controle de Estado**: Cards são habilitados/desabilitados conforme disponibilidade de contratos e status de processamento
6. **Feedback Visual**: Sistema exibe tela de sucesso ou erro após tentativa de assinatura
7. **Limitação Mobile**: Assinatura individual e visualização de detalhes só disponível via desktop
8. **Totalização**: Valor total pendente é calculado e exibido no header do dashboard
9. **Criptografia**: Chave pública RSA configurada para criptografia de dados sensíveis

---

## 6. Relação entre Entidades

**SignatureCardModel**
- Representa um card de contrato no dashboard
- Atributos: title, total, icon, text, active

**DashboardCards (Configuração)**
- Define 4 tipos de contratos: pendentes, assinados, concluídos, desacordo
- Cada tipo possui ícone, label de botão e status de ativação

**SignatureResults (Configuração)**
- Define 2 tipos de resultado: success, error
- Cada tipo possui ícone, título e descrição

**Fluxo de Dados:**
```
DashboardService.getContratos() 
  → totalContract[] (pendentes, assinados, concluídos, desacordo)
  → DashboardCardsComponent 
  → SignatureCardComponent[]
  → SignatureComponent (modal)
  → TokenModule (validação)
  → SignatureResultComponent (feedback)
```

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica - A aplicação consome APIs REST mas não acessa diretamente estruturas de banco de dados. O backend é responsável pela persistência.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica - A aplicação não atualiza diretamente estruturas de banco de dados. Todas as operações de escrita são realizadas através de chamadas à API REST do backend.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Configurações de ambiente (URLs de API, chaves públicas, log level) |
| angular.json | leitura | Angular CLI | Configurações de build e deployment |
| package.json | leitura | NPM | Dependências e scripts do projeto |
| manifest.json | leitura | Service Worker | Configuração PWA |
| mocks/data.json | leitura | JSON Server (dev) | Dados mockados para desenvolvimento |
| mocks/routes.json | leitura | JSON Server (dev) | Rotas mockadas para desenvolvimento |
| tslint.report.json | gravação | Scripts NPM | Relatório de análise estática de código |
| test-report.xml | gravação | Jest | Relatório de testes unitários |
| coverage/* | gravação | Jest | Relatórios de cobertura de testes |

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
| **API BV Backend** | REST API | API principal para operações de contratos e assinatura eletrônica |
| **@arqt/spa-framework** | Biblioteca | Framework corporativo BV com componentes core e configurações |
| **@intb/commons** | Biblioteca | Biblioteca compartilhada com componentes Token e Alert |
| **API Utils** | REST API | Serviços utilitários (health check, logger) |
| **Token Eletrônico** | Componente | Sistema de validação por token (aplicação 2) integrado via TokenModule |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular seguindo padrões Angular
- Separação clara de responsabilidades entre componentes, serviços e módulos
- Uso adequado de RxJS e BehaviorSubject para gerenciamento de estado
- Documentação JSDoc presente em métodos principais
- Implementação de animações e feedback visual
- Configuração adequada para diferentes ambientes
- Uso de TypeScript com tipagem
- Estrutura de testes configurada (Jest)

**Pontos de Melhoria:**
- Falta de tratamento de erros mais robusto em alguns serviços
- Polling com intervalo fixo (5s) poderia ser configurável
- Alguns componentes poderiam ter interfaces mais explícitas
- Falta de testes unitários implementados (apenas estrutura)
- Comentários em português misturados com código em inglês
- Método `showError()` com dados hardcoded poderia ser mais flexível
- Ausência de interceptors HTTP para tratamento centralizado de erros
- Alguns magic numbers e strings poderiam ser constantes
- Falta de validações de entrada em alguns métodos

O código demonstra boas práticas de desenvolvimento Angular, mas há espaço para melhorias em robustez, testabilidade e manutenibilidade.

---

## 14. Observações Relevantes

1. **Arquitetura de Biblioteca**: O projeto está estruturado como uma biblioteca Angular (`@intb/assinatura-eletronica`) que pode ser consumida por outras aplicações

2. **Suporte PWA**: Aplicação configurada como Progressive Web App com Service Worker e manifest

3. **Deployment Multi-Ambiente**: Configurações específicas para DES, QA, UAT e PRD via OpenShift

4. **Containerização**: Dockerfile e configurações Apache (httpd.conf) para deployment em containers

5. **Desenvolvimento Local**: Mock server configurado para desenvolvimento sem dependência do backend

6. **Build Otimizado**: Configurações de build com AOT, tree-shaking e lazy loading de fontes

7. **Análise de Código**: Integração com SonarQube para análise de qualidade e cobertura

8. **Documentação**: Compodoc configurado para geração de documentação técnica

9. **Segurança**: Chave pública RSA configurada para criptografia de dados sensíveis

10. **Responsividade**: Uso extensivo de Flex Layout para interface responsiva

11. **Tema Corporativo**: Integração com tema corporativo BV através de SCSS

12. **Internacionalização**: Locale pt-BR configurado para formatação de moeda e datas