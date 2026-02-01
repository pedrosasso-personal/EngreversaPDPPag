# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema web de aprovações desenvolvido em Angular 7 para o Internet Banking do Banco Votorantim. Permite que usuários master visualizem, aprovem ou rejeitem solicitações pendentes de operações financeiras (Pix, Open Banking, Perfil de Investidor), além de consultar o histórico de aprovações. O sistema implementa fluxo de aprovação com múltiplas assinaturas, validação por token e controle de permissões por perfil de usuário.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **AprovacoesComponent** | Componente principal que gerencia as abas de pendências e histórico |
| **PendenciasComponent** | Exibe lista de aprovações pendentes, permite seleção em lote e processamento via token |
| **HistoricoComponent** | Exibe histórico de aprovações já processadas com filtros por período |
| **DetalheComponent** | Exibe detalhes de uma operação específica (assinaturas, aprovadores, documentos) |
| **ResultadoComponent** | Tela de feedback após processamento de aprovações |
| **AprovacoesService** | Serviço principal para comunicação com APIs de aprovações |
| **PendenciasService** | Serviço auxiliar para gerenciamento de estado de pendências |
| **AprovacoesBase** | Classe abstrata com lógica compartilhada (filtros, status, detalhes) |
| **CardComponent** | Componente de card reutilizável com padding configurável |
| **EmptyStateComponent** | Componente para exibição de estado vazio |
| **LoadComponent** | Componente de loading |
| **ModalApprovalLimitComponent** | Modal informativo sobre limite de 500 aprovações |
| **ModalInfoMyProfileComponent** | Modal tutorial sobre funcionalidade "Meu Perfil" |

## 3. Tecnologias Utilizadas
- **Framework Frontend**: Angular 7.1.4
- **Linguagem**: TypeScript 3.1.6
- **UI Components**: Angular Material 7.1.1, Angular Flex Layout
- **Bibliotecas Internas**: @intb/commons (0.104.0), @arqt/spa-framework (1.8.5), @arqt/ui (1.3.0)
- **Gerenciamento de Estado**: RxJS 6.3.3 (BehaviorSubject, Subject)
- **Datas**: Moment.js 2.29.4
- **Testes**: Jest 23.6.0
- **Build**: Angular CLI 7.1.4, ng-packagr 4.4.0
- **Containerização**: Docker (httpd-24-rhel7)
- **Servidor Mock**: json-server, Node.js/Express
- **Service Worker**: @angular/service-worker (PWA)
- **Análise Estática**: SonarQube, TSLint

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/aprovacoes/pendentes` | AprovacoesService | Lista aprovações pendentes com paginação e filtro por data |
| GET | `/v1/ib/aprovacoes/historico` | AprovacoesService | Lista histórico de aprovações com filtro por data |
| POST | `/v1/ib/aprovacoes/totalizar` | AprovacoesService | Calcula total de operações e valores selecionados |
| GET | `/v1/ib/aprovacoes/detalhe/operacao/{id}` | AprovacoesService | Obtém detalhes de uma operação específica |
| POST | `/v1/ib/aprovacoes/processar` | TokenModalModule | Processa aprovação/rejeição em lote (via token) |
| POST | `/v1/ib/aprovacoes/operacao/{id}/pdf` | AprovacoesService | Gera PDF com detalhes da operação |
| GET | `/v3/ib/aprovacoes/{id}` | AprovacoesService | Obtém PDF de operação (versão 3) |
| GET | `/v1/ib/portal/userdata` | PendenciasService | Obtém dados do usuário logado |
| GET | `/api-utils/status` | AppModule | Health check do backend |
| POST | `/api-utils/logger` | AppModule | Envio de logs do frontend |

## 5. Principais Regras de Negócio
- **Limite de Aprovação em Lote**: Máximo de 500 operações por vez para aprovar/rejeitar
- **Múltiplas Assinaturas**: Operações podem exigir número mínimo de aprovações e aprovadores obrigatórios
- **Restrição de Auto-Aprovação**: Usuários que já atuaram em uma operação não podem aprová-la novamente (checkbox desabilitado)
- **Validação por Token**: Aprovações/rejeições exigem validação via token (SMS/Email)
- **Tipos de Operação**: Suporta Pix (PAGPIX, AGENPIX, DEVPIX), Open Banking (CONS), Perfil de Investidor (SUITABILITY), Meu Perfil (MEU_PERFIL)
- **Filtro Temporal**: Consultas limitadas a períodos de 7, 30, 60 ou 90 dias
- **Paginação**: Lista de pendências carregada com scroll infinito (100 itens por página)
- **Status de Operação**: P (Pendente), A (Aprovado), R (Rejeitado), E (Expirado), T (Em processamento)
- **Perfil de Usuário**: Tipo 2 (operador) tem restrições diferentes de usuário master
- **Redirecionamento Open Banking**: Operações CONS redirecionam para página de detalhes de compartilhamento

## 6. Relação entre Entidades

**Entidades Principais:**

- **PendenciasModel / HistoricoModel**: Representam operações de aprovação
  - Atributos: id, dataSolicitacao, tipoTransacao, descricao, valor, nomeSolicitante/nomeSolicitador, statusTransacao
  
- **DetailModel**: Detalhes de uma operação
  - Atributos: id, codigoOriginalOperacao, aprovacoesMinimas, mensagemErro, error, type
  - Relacionamentos: 
    - 1:N com AssinaturaModel (aprovacoes - já assinadas)
    - 1:N com AssinaturaModel (aprovadores - podem assinar)

- **AssinaturaModel**: Representa uma assinatura/aprovador
  - Atributos: statusAprovacao (A/R), data, usuarioAprovador, obrigatorio

- **UserDataModel**: Dados do usuário logado
  - Relacionamentos:
    - 1:1 com ClientModel (current_client)
    - 1:1 com AccountModel (current_account)

- **AprovacoesSelecionadasModel**: Totalização de seleção
  - Atributos: quantidadeOperacoes, totalOperacoes

**Relacionamentos:**
- Uma operação (Pendencias/Historico) possui múltiplas assinaturas (aprovações já realizadas)
- Uma operação possui múltiplos aprovadores elegíveis
- Um usuário (UserData) está associado a um cliente e uma conta corrente

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema frontend não acessa banco diretamente, apenas via APIs REST |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema frontend não atualiza banco diretamente, apenas via APIs REST |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts / environment.prod.ts | Leitura | AppConfigurationService | Configurações de ambiente (URLs de API, chaves públicas) |
| data.json | Leitura | Mock Server (mocks/server.js) | Dados mockados para desenvolvimento local |
| routes.json | Leitura | Mock Server (mocks/server.js) | Mapeamento de rotas para mock |
| teste.pdf | Leitura | Mock Server | PDF de exemplo para testes |
| detalhes.pdf | Gravação | DetalheComponent.downloadFile() | PDF gerado com detalhes da operação (download no navegador) |
| tslint.report.json | Gravação | npm scripts | Relatório de análise estática |
| test-report.xml | Gravação | Jest | Relatório de testes unitários |
| coverage/lcov.info | Gravação | Jest | Relatório de cobertura de testes |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **API de Aprovações** | Backend principal (`/v1/ib/aprovacoes/*`) para gestão de aprovações |
| **API de Portal** | Serviço de dados do usuário (`/v1/ib/portal/userdata`) |
| **API de Token CA** | Validação de token para aprovações (`/v1/ib/token-ca/*`) via TokenModalModule |
| **API de Dados de Contato** | Obtenção de contatos (`/v1/ib/dados/contato`) |
| **API Utils** | Health check e logging (`/api-utils/status`, `/api-utils/logger`) |
| **Open Banking** | Redirecionamento para detalhes de compartilhamento (`/open-banking/transmissao/detalhes-compartilhamento`) |
| **SonarQube** | Análise estática de código (https://sonar.appdes.bvnet.bv) |
| **Nexus NPM** | Repositório de pacotes (https://nexus.bvnet.bv/repository/npm-group/) |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com componentes especializados
- Uso adequado de RxJS para gerenciamento de estado reativo
- Implementação de classe base (AprovacoesBase) para reutilização de lógica
- Componentização adequada (card, empty-state, load, modals)
- Uso de TypeScript com tipagem forte (interfaces/models bem definidos)
- Configuração de testes unitários com Jest
- Documentação de API via Compodoc
- Implementação de PWA com Service Worker

**Pontos de Melhoria:**
- Código comentado em vários locais (ex: handleCheckData no histórico, funcionalidade de impressão)
- Alguns métodos marcados com `/* istanbul ignore next */` indicando baixa cobertura de testes
- Lógica de negócio misturada com lógica de apresentação em alguns componentes
- Uso excessivo de `any` em alguns pontos (ex: `insertDetail`)
- Falta de tratamento de erro consistente (alguns lugares usam HttpErrorResponse, outros não)
- Código duplicado entre PendenciasComponent e HistoricoComponent
- Dependências desatualizadas (Angular 7, bibliotecas com vulnerabilidades conhecidas)
- Falta de lazy loading para módulos secundários
- Strings hardcoded que deveriam estar em arquivos de i18n
- Alguns componentes muito grandes (PendenciasComponent com múltiplas responsabilidades)

## 14. Observações Relevantes

1. **Arquitetura de Biblioteca**: O projeto está estruturado como uma biblioteca Angular (`projects/intb/aprovacoes`) que pode ser empacotada e reutilizada em outros projetos

2. **Mock Server Sofisticado**: Implementação de servidor mock com Node.js/Express que simula comportamento de APIs, incluindo delay de 2 segundos e gerenciamento de estado

3. **Containerização**: Aplicação preparada para deploy em container Docker com Apache httpd, incluindo configurações de compressão e cache

4. **Tutorial Interativo**: Modal de 6 etapas (`ModalInfoMyProfileComponent`) para onboarding de nova funcionalidade "Meu Perfil"

5. **Acessibilidade**: Uso de `aria-label` e preocupação com navegação por teclado

6. **Performance**: Implementação de scroll infinito para evitar carregamento de grandes volumes de dados

7. **Segurança**: Uso de chave pública RSA para criptografia, validação por token em operações críticas

8. **CI/CD**: Configuração para Jenkins (`jenkins.properties`) e integração com SonarQube para análise de qualidade

9. **Versionamento**: Sistema de versionamento semântico (0.24.0) com changelog implícito

10. **Ambiente de Desenvolvimento**: Suporte completo para desenvolvimento local com hot-reload e mock de APIs

11. **Limitação Técnica**: Aplicação desenvolvida em Angular 7 (EOL), recomenda-se migração para versões mais recentes

12. **Dependência de Bibliotecas Internas**: Forte acoplamento com bibliotecas `@intb/commons`, `@arqt/spa-framework` e `@arqt/ui` do Banco Votorantim