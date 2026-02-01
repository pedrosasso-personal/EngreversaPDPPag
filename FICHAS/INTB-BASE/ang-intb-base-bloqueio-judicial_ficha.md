# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web desenvolvido em Angular 7 para consulta e gerenciamento de **Bloqueios Judiciais** de contas correntes e ativos financeiros. A aplicação permite visualizar bloqueios judiciais por tipo (conta corrente, renda fixa, fundos de investimento, ações), consultar detalhes de processos judiciais específicos, filtrar por período e exportar relatórios em PDF. O sistema é voltado para o Internet Banking (INTB) do Banco BV.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **BloqueioService** | Serviço principal para comunicação com API backend, consulta de bloqueios por tipo e por processo, exportação de PDF |
| **ContaCorrenteComponent** | Componente de visualização e filtro de bloqueios judiciais de conta corrente, com tabela paginada e busca |
| **ProcessoComponent** | Exibe detalhes completos de um processo judicial específico com todos os bloqueios relacionados |
| **BloqueioTabsComponent** | Componente de navegação por abas entre diferentes tipos de bloqueio |
| **EmptyProcessComponent** | Componente de estado vazio quando não há processos a exibir |
| **LoadingComponent** | Componente de indicador de carregamento |
| **AppComponent** | Componente raiz da aplicação |
| **AppConfigurationService** | Serviço de configuração do ambiente (URLs, chaves públicas, etc) |
| **AppService** | Serviço para obtenção de dados de sessão do usuário |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework frontend principal
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **RxJS 6.3.3** - Programação reativa
- **Moment.js 2.23.0** - Manipulação de datas
- **@arqt/spa-framework 1.8.5** - Framework corporativo BV
- **@intb/commons** - Biblioteca de componentes compartilhados do Internet Banking
- **TypeScript 3.1.6** - Linguagem de programação
- **Jest 23.6.0** - Framework de testes unitários
- **JSON Server 0.14.0** - Mock de API para desenvolvimento
- **HttpClient (Angular)** - Cliente HTTP para comunicação com backend
- **Service Worker** - Para funcionalidades PWA
- **Sonar Scanner** - Análise estática de código

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/bloqueio/judicial` | BloqueioService | Consulta bloqueios judiciais por tipo e período |
| POST | `/v1/ib/bloqueio/judicial/processo` | BloqueioService | Consulta todos os bloqueios de um processo específico |
| POST | `/v1/ib/bloqueio/judicial/pdf` | BloqueioService | Exporta relatório de bloqueios em PDF |
| GET | `/v1/ib/portal/userdata` | AppService | Obtém dados de sessão do usuário |
| GET | `/api-utils/status` | N/A (configuração) | Health check do backend |
| POST | `/api-utils/logger` | N/A (configuração) | Envio de logs |

---

## 5. Principais Regras de Negócio

1. **Filtro por Período**: Permite consultar bloqueios judiciais em intervalos pré-definidos (7, 30, 60 ou 90 dias) ou período customizado
2. **Busca Textual**: Filtro de busca em tempo real (debounce de 300ms) aplicado sobre os dados da tabela
3. **Navegação por Processo**: Ao clicar em um processo na listagem, navega para tela de detalhes com todos os bloqueios relacionados
4. **Exportação de PDF**: Gera comprovante em PDF dos bloqueios filtrados/visualizados
5. **Impressão**: Funcionalidade de impressão da tela atual via window.print()
6. **Tipos de Bloqueio**: Sistema suporta 4 tipos - Conta Corrente, Renda Fixa, Fundos de Investimento e Ações
7. **Formatação de Valores**: Valores monetários formatados como moeda (currency), datas formatadas no padrão brasileiro
8. **Estado Vazio**: Exibe componente específico quando não há dados a exibir
9. **Loading**: Indicador de carregamento durante requisições assíncronas
10. **Modo Privado**: Sistema detecta se está em modo privado (PrivateService) para ajustar comportamento

---

## 6. Relação entre Entidades

**BloqueioJudicialModel** (Entidade principal):
- tipoBloqueio: string
- protocolo: string
- processo: string
- ativo: string
- valorPedido: number | string
- valorBloqueado: number | string
- vara: string
- autorJuiz: string
- cidade: string
- dtEmissao: Date | string
- dtBloqueio: Date | string
- dtDesbloqueio: Date | string
- status: string

**BloqueioJudicialProcessoModel** (Agregação por tipo):
- rendaFixa: BloqueioJudicialModel[]
- contaCorrente: BloqueioJudicialModel[]
- fundosInvestimentos: BloqueioJudicialModel[]
- acoes: BloqueioJudicialModel[]

**BloqueioRequestModel** (Payload de requisição):
- dataFim: string
- dataInicio: string
- tipoBloqueio: string

**Relacionamento**: Um processo judicial pode ter múltiplos bloqueios de diferentes tipos (1:N).

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: A aplicação Angular consome APIs REST, não acessa banco de dados diretamente.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: A aplicação Angular é frontend, não realiza operações diretas de escrita em banco de dados.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| comprovante.pdf | gravação | ContaCorrenteComponent.downloadFile() | Arquivo PDF gerado com relatório de bloqueios judiciais |
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Arquivos de configuração de ambiente (URLs, chaves, etc) |
| data.json | leitura | JSON Server (mock) | Dados mockados para desenvolvimento local |

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
| API Backend BV (`/api` ou `http://localhost:3200`) | REST API | API principal para consulta de bloqueios judiciais, processos e geração de PDFs |
| @arqt/spa-framework | Biblioteca | Framework corporativo do BV para padronização de SPAs |
| @intb/commons | Biblioteca | Componentes compartilhados do Internet Banking (TabsModule, TableModule, InputTextModule, RangeDatePickerModule, PrivateService) |
| JSON Server | Mock API | Servidor mock para desenvolvimento local (porta 3200) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara entre componentes, serviços e modelos
- Uso adequado de TypeScript com tipagem forte
- Implementação de testes unitários com Jest
- Uso de RxJS e programação reativa
- Debounce implementado corretamente para otimizar buscas
- Separação entre biblioteca (`projects/intb/bloqueio-judicial`) e aplicação (`src/app`)
- Configuração de ambientes (dev/prod) bem estruturada
- Uso de lazy loading para módulos

**Pontos de Melhoria:**
- Presença de `console.log` em código de produção (ProcessoComponent, ContaCorrenteComponent)
- Comentários `/* istanbul ignore next */` indicam código não testado
- Lógica de negócio misturada com lógica de apresentação em alguns componentes
- Falta de tratamento de erros mais robusto (apenas log no console em alguns casos)
- Código duplicado entre módulos da lib e da aplicação
- Falta de documentação inline (JSDoc) em alguns métodos
- Variável `v` não utilizada no ProcessoComponent (linha de debug)
- Uso de `any` em alguns lugares poderia ser mais específico

---

## 14. Observações Relevantes

1. **Arquitetura Micro Frontend**: O projeto está estruturado como biblioteca Angular (`projects/intb/bloqueio-judicial`) que pode ser empacotada e reutilizada em outras aplicações

2. **Modo de Desenvolvimento**: Sistema possui mock server (JSON Server) para desenvolvimento local independente do backend

3. **PWA**: Aplicação configurada como Progressive Web App com Service Worker

4. **Análise Estática**: Integração com SonarQube para análise de qualidade de código

5. **Compatibilidade**: Suporte a IE11 através de polyfills extensivos

6. **Impressão**: Funcionalidade de impressão implementada via CSS print media queries

7. **Exportação**: Sistema permite download de PDF gerado pelo backend

8. **Roteamento**: Uso de lazy loading para otimização de performance

9. **Tema**: Aplicação usa tema "corporativo" do BV

10. **Criptografia**: Chave pública RSA configurada para possível criptografia de dados sensíveis

11. **Localização**: Sistema configurado para pt-BR (português brasileiro)

12. **Build**: Configuração de build otimizada para produção com AOT, tree-shaking e minificação