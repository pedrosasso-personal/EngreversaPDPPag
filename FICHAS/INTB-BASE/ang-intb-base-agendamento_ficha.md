# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema web de consulta e cancelamento de agendamentos de pagamentos (PIX e transferências) desenvolvido em Angular 7. Permite ao usuário visualizar seus agendamentos futuros, consultar detalhes de cada agendamento e realizar o cancelamento mediante validação por token. O sistema é estruturado como uma biblioteca Angular reutilizável (`@intb/agendamento`) e uma aplicação host que a consome.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AgendamentoComponent** | Componente principal que lista agendamentos, gerencia filtros de data e exibe feedbacks de sucesso/erro |
| **DetalheComponent** | Exibe detalhes completos de um agendamento específico (origem, destino) e permite cancelamento |
| **ModalCancelComponent** | Modal de confirmação de cancelamento com integração de token de segurança |
| **FeedbackComponent** | Componente genérico para exibição de mensagens de sucesso ou erro |
| **EmptyStateComponent** | Exibe estado vazio quando não há agendamentos |
| **LoadComponent** | Componente de loading durante requisições |
| **AgendamentoService** | Serviço responsável por comunicação com API (listagem e detalhes de agendamentos) |
| **ModalCancelService** | Gerencia estado de resposta do cancelamento via Subject/Observable |
| **AppService** | Serviço para obtenção de dados compartilhados da sessão do usuário |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **Angular Flex Layout** - Sistema de layout responsivo
- **RxJS 6.3.3** - Programação reativa
- **Moment.js 2.29.4** - Manipulação de datas
- **@arqt/spa-framework 1.8.5** - Framework corporativo BV
- **@intb/commons** - Biblioteca de componentes compartilhados (Button, Modal, Table, Token, etc)
- **TypeScript 3.1.6** - Linguagem de desenvolvimento
- **Jest 23.6.0** - Framework de testes unitários
- **Node.js 8+** - Ambiente de execução
- **JSON Server** - Mock de API para desenvolvimento
- **Docker** - Containerização (Apache HTTPD)
- **Service Worker** - PWA capabilities

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/scheduled-payments?initialDate={date}&finalDate={date}` | AgendamentoService | Lista agendamentos em um período |
| GET | `/v1/ib/scheduled-payments/{nsu}?isNovoAgendamento={boolean}` | AgendamentoService | Obtém detalhes de um agendamento específico |
| POST | `/v1/ib/scheduled-payments/{nsu}/cancel?isNovoAgendamento={boolean}&type={type}` | ModalCancelComponent (via TokenModule) | Cancela um agendamento com validação de token |
| GET | `/v1/ib/portal/userdata` | AppService | Obtém dados compartilhados da sessão do usuário |
| GET | `/v1/ib/dados/contato` | N/A (mock) | Obtém dados de contato do usuário |
| POST | `/v1/ib/token-ca/notification-type/{type}/application/{application}` | TokenModule (@intb/commons) | Gera token de autenticação |

---

## 5. Principais Regras de Negócio

1. **Período de Consulta**: Agendamentos são consultados em janelas de 30, 60 ou 90 dias a partir da data atual + 1 dia
2. **Tipos de Agendamento**: Sistema diferencia entre PIX automático (recorrente) e PIX/transferência única
3. **Identificação de Agendamento**: Usa `identificadorRecorrencia` para agendamentos recorrentes e `nuUnicoAgendamento` para agendamentos únicos
4. **Máscara de CPF/CNPJ**: CPF exibe formato `***.XXX.XXX-**` (parcialmente mascarado), CNPJ exibe formato completo `XX.XXX.XXX/XXXX-XX`
5. **Cancelamento com Token**: Requer validação por token de segurança antes de confirmar cancelamento
6. **Tipos de Pagamento para Token**: `PIX_AUTOMATICO` para recorrentes, `PIX_TRANSFERENCIA` para únicos
7. **Feedback Visual**: Sistema exibe estados de sucesso, erro, loading e empty state conforme contexto
8. **Navegação Rastreada**: Todas as navegações são registradas via `LogNavigationService`

---

## 6. Relação entre Entidades

**Scheduled** (Agendamento)
- `dataAgendada`: Data do agendamento
- `favorecido`: Nome do beneficiário
- `tipoAgendamento`: Tipo (PIX, transferência)
- `valor`: Valor monetário
- `nuUnicoAgendamento`: Identificador único
- `identificadorRecorrencia`: ID de recorrência (se aplicável)
- `isNovoAgendamento`: Flag indicando novo modelo de agendamento

**ScheduledDetail** (Detalhe do Agendamento)
- `remetente`: Dados da origem (Detail)
- `favorecido`: Dados do destino (Detail)

**Detail** (Dados de Conta)
- `cdChavePix`: Chave PIX (opcional)
- `nome`: Nome do titular
- `nuCpfCnpj`: CPF/CNPJ
- `nuBanco`: Código/nome do banco
- `nuAgencia`: Número da agência
- `nuContaCorrente`: Número da conta
- `objeto`: Objetivo do pagamento (para recorrentes)
- `contract`: ID da cobrança (para recorrentes)
- `descricao`: Descrição adicional (para recorrentes)

**Relacionamentos**:
- Um `Scheduled` possui um `ScheduledDetail` (1:1)
- Um `ScheduledDetail` possui dois `Detail` (remetente e favorecido) (1:2)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `data.json` | Leitura | Mock Server (desenvolvimento) | Dados mockados para testes locais |
| `routes.json` | Leitura | Mock Server (desenvolvimento) | Mapeamento de rotas para mock |
| `manifest.json` | Leitura | Service Worker | Configuração PWA |
| `ngsw-config.json` | Leitura | Service Worker | Configuração de cache do Service Worker |
| `environment.ts` / `environment.prod.ts` | Leitura | AppConfigurationService | Configurações de ambiente |
| Logs (console/API) | Gravação | LogNavigationService | Registro de navegação e erros |

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
| **API BV Backend** | API REST principal para operações de agendamento (listagem, detalhes, cancelamento) |
| **API de Token** | Serviço de geração e validação de tokens de segurança (`/v1/ib/token-ca`) |
| **API de Dados do Usuário** | Serviço de dados compartilhados da sessão (`/v1/ib/portal/userdata`) |
| **API de Contato** | Serviço de dados de contato do usuário (`/v1/ib/dados/contato`) |
| **API Utils** | Serviços utilitários (health check, logger) |
| **@intb/commons** | Biblioteca de componentes compartilhados do Internet Banking |
| **@arqt/spa-framework** | Framework corporativo BV para SPAs |
| **Nexus NPM Registry** | Repositório corporativo de pacotes NPM |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7.5/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com componentes modulares
- Uso adequado de TypeScript com tipagem de interfaces
- Estrutura de biblioteca reutilizável bem organizada
- Implementação de testes unitários (Jest)
- Uso de padrões Angular (Services, Modules, Components)
- Configuração adequada de ambientes (dev/prod)
- Implementação de PWA com Service Worker
- Rastreamento de navegação implementado
- Uso de RxJS para programação reativa

**Pontos de Melhoria:**
- Código comentado no template HTML (filtros de data desabilitados)
- Falta de tratamento de erros mais robusto em alguns pontos
- Uso de `console.error` ao invés de serviço de logging estruturado
- Alguns componentes poderiam ter responsabilidades mais granulares
- Falta de documentação inline (JSDoc) em várias classes
- Hardcoded strings que poderiam estar em arquivos de i18n
- Dependências com versões desatualizadas (Angular 7, Node 8)
- Uso de `any` em alguns tipos (ex: `Observable<any>`)
- Falta de validações de entrada em alguns métodos

---

## 14. Observações Relevantes

1. **Arquitetura de Biblioteca**: O projeto é estruturado como uma biblioteca Angular (`@intb/agendamento`) que pode ser consumida por outras aplicações, promovendo reusabilidade

2. **Mock Server**: Implementação de servidor mock com Node.js e JSON Server para desenvolvimento local independente de backend

3. **Docker**: Configuração Docker usando Apache HTTPD (Red Hat) com otimizações de compressão e cache

4. **Segurança**: Implementação de criptografia RSA via `jsencrypt` com chave pública configurada

5. **Build Otimizado**: Configuração de build de produção com AOT, tree-shaking, minificação e lazy loading de fontes

6. **Análise de Código**: Integração com SonarQube para análise estática e cobertura de testes

7. **CI/CD**: Configuração Jenkins com propriedades específicas para pipeline

8. **Versionamento**: Projeto na versão 0.11.0, indicando fase de desenvolvimento ativo

9. **Tema Corporativo**: Uso de tema "corporativo" do BV com componentes padronizados

10. **Acessibilidade**: Uso de Angular Material que fornece componentes acessíveis por padrão

11. **Responsividade**: Implementação com Angular Flex Layout para layouts responsivos

12. **Monitoramento**: Sistema de logging integrado para rastreamento de erros e navegação