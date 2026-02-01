# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web desenvolvido em Angular 7 para gerenciamento de investimentos em renda fixa (CDB e Compromissada) do Banco Votorantim. O sistema permite aos clientes realizar aplicações, resgates e acompanhar suas solicitações de investimentos em produtos de renda fixa, incluindo cálculo de impostos (IOF e IR), validações de horário e saldo, e gestão de operações com diferentes tipos de liquidez.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **InvestimentosComponent** | Componente principal que gerencia a navegação entre as abas de Aplicações, Resgate e Minhas Solicitações |
| **AplicacoesComponent** | Lista e filtra produtos de renda fixa disponíveis para aplicação |
| **AplicacaoComponent** | Gerencia o fluxo de aplicação em um produto específico, incluindo validações e envio de boleta |
| **ResgateComponent** | Componente container para os tipos de resgate (CDB e Compromissada) |
| **CdbComponent** | Gerencia resgates de CDB (liquidez, carência e prazo final) |
| **CompromissadaComponent** | Gerencia resgates de operações compromissadas |
| **FormularioResgateComponent** | Formulário de resgate com cálculo de taxas e valores líquidos |
| **MinhasSolicitacoesComponent** | Exibe histórico de solicitações de aplicações e resgates |
| **RendafixaService** | Serviço central para gerenciamento de estado e comunicação entre componentes |
| **AplicacoesService** | Serviço para operações relacionadas a aplicações |
| **ResgateService** | Serviço para operações relacionadas a resgates |
| **ModalTokenComponent** | Modal para validação de token em operações sensíveis |

## 3. Tecnologias Utilizadas

- **Framework Frontend**: Angular 7.1.4
- **Linguagem**: TypeScript 3.1.6
- **UI Components**: Angular Material 7.1.1
- **Gerenciamento de Estado**: RxJS 6.3.3 (BehaviorSubject/Observable)
- **Máscaras de Input**: ng2-currency-mask 5.3.1, ngx-mask 10.0.1
- **Date Picker**: saturn-datepicker 7.2.0, ngx-daterangepicker-material 2.1.9
- **Testes**: Jest 23.6.0
- **Build**: Angular CLI 7.1.4, ng-packagr 4.4.0
- **Bibliotecas Internas**: @intb/commons, @arqt/spa-framework, @arqt/ui
- **Utilitários**: Moment.js 2.22.2, Hammerjs 2.0.8
- **Criptografia**: jsencrypt 3.0.0-rc.1

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/rendafixa/aplicacao/produto` | AplicacoesService | Lista produtos disponíveis para aplicação com filtros |
| GET | `/v1/ib/rendafixa/aplicacao/produto/{id}` | AplicacaoService | Obtém detalhes de um produto específico |
| POST | `/v1/ib/boleta/enviar` | AplicacaoService | Envia boleta de aplicação |
| POST | `/ib/validacao-boleta/v1/produto/valor` | AplicacaoService | Valida valor da aplicação |
| GET | `/ib/validacao-boleta/v1/produto/{id}/horario` | AplicacaoService | Valida horário de operação |
| GET | `/ib/validacao-boleta/v1/situacao/cliente` | AplicacoesService | Valida situação do cliente |
| POST | `/ib/validacao-boleta/v1/command` | AplicacoesService | Valida comando de operação |
| GET | `/v1/ib/boleta/resgate/produto/CDB` | ResgateService | Lista operações CDB disponíveis para resgate |
| GET | `/v1/ib/boleta/resgate/produto/compromissada` | ResgateService | Lista operações compromissadas para resgate |
| POST | `/v1/ib/renda-fixa-calculos/calcular-valores` | ResgateService | Calcula IOF, IR e valores líquidos do resgate |
| POST | `/v1/ib/boleta/resgate/solicitacao` | ResgateService | Envia solicitação de resgate |
| POST | `/ib/validacao-boleta/v1/command-resgate` | ResgateService | Valida comando de resgate |
| GET | `/v1/ib/rendafixa/aplicacao/solicitacao` | MinhasSolicitacoesService | Lista solicitações do cliente com filtros |

## 5. Principais Regras de Negócio

- **Validação de Horário**: Produtos possuem horário limite para operação (HhInicioOperacao e HhFimOperacao)
- **Aplicação Mínima**: Cada produto possui valor mínimo de aplicação (VrMinimoAplicacaoOperacao)
- **Cálculo de IOF**: Isento após 30 dias da aplicação, alíquota regressiva de 96% a 0%
- **Cálculo de IR**: Alíquota regressiva baseada no prazo: 22,5% (até 180 dias), 20% (181-360 dias), 17,5% (361-720 dias), 15% (acima de 720 dias)
- **Tipos de Liquidez**: CDB Liquidez (resgate imediato), CDB Carência (resgate após período), CDB Prazo Final (resgate no vencimento)
- **Bloqueios Parciais**: Operações podem ter valores bloqueados que não podem ser resgatados
- **Resgate Total vs Parcial**: Cliente pode optar por resgatar valor total ou parcial da operação
- **Validação de Saldo**: Sistema valida se valor solicitado não excede saldo disponível
- **Token de Segurança**: Operações de aplicação e resgate requerem validação por token
- **Filtros de Produtos**: Indexador (pré/pós-fixado), liquidez, carência, vencimento, aplicação mínima

## 6. Relação entre Entidades

**ItemDadoProdutosAplicacao** (Produto de Aplicação)
- CdParametrizacaoProdutoIB: Identificador único
- Produto, Rentabilidade, QtDiaVencimento, QtDiaLiquidez
- VrMinimoAplicacaoOperacao, HhInicioOperacao, HhFimOperacao
- Relacionamento: Um produto pode ter múltiplas aplicações

**AplicacaoBoleta** (Boleta de Aplicação)
- codigoParametrizacaoProduto: FK para ItemDadoProdutosAplicacao
- valorOperacao: Valor da aplicação

**ItemDadoResgate** (Operação Disponível para Resgate)
- cdOperacao: Identificador único da operação
- tipoCdb: Tipo de liquidez (1=Carência, 2=Liquidez, 3=PrazoFinal)
- valorBruto, valorLiquido, valorAplicado
- dtAplicacao, dtLiquidez, dtVencimento
- bloqueios, valorBloqueio: Controle de bloqueios parciais

**PostResgateItem** (Item de Resgate)
- codigoOperacao: FK para ItemDadoResgate
- valorBruto, valorLiquido, valorIOF, valorIR
- flagResgateTotal: Indica se é resgate total

**MinhasSolicitacoes** (Histórico de Solicitações)
- cdOperacao: Identificador da operação
- codStatus: Status da solicitação (1=Em processamento, 13=Processada, etc)
- codEvento: Tipo de evento (0=Aplicação, 1=Resgate)
- valor, solicitadoEm, processadoEm

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| não se aplica | não se aplica | não se aplica | Sistema consome apenas APIs REST, não acessa banco diretamente |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|------------------------------|------|----------|-----------------|
| não se aplica | não se aplica | não se aplica | Sistema consome apenas APIs REST, não acessa banco diretamente |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| environment.ts | leitura | src/environments/ | Configurações de ambiente (desenvolvimento) |
| environment.prod.ts | leitura | src/environments/ | Configurações de ambiente (produção) |
| manifest.json | leitura | src/ | Configuração PWA (Progressive Web App) |
| ngsw-config.json | leitura | raiz do projeto | Configuração do Service Worker |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/API | Descrição |
|-------------|-----------|
| **API BV Renda Fixa** | API REST principal para operações de renda fixa (aplicações, resgates, consultas) |
| **API Validação Boleta** | API para validações de horário, valor, situação do cliente e comandos |
| **API Cálculos Renda Fixa** | API para cálculo de IOF, IR e valores líquidos |
| **@intb/commons** | Biblioteca interna de componentes compartilhados do Banco |
| **@arqt/spa-framework** | Framework interno para aplicações SPA |
| **@arqt/ui** | Biblioteca de componentes UI do Banco |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (componentes, serviços, modelos)
- Uso adequado de TypeScript com tipagem forte
- Implementação de testes unitários com Jest
- Uso de padrões Angular (Services, Observables, Dependency Injection)
- Componentização adequada com reutilização de código
- Uso de bibliotecas internas padronizadas do banco

**Pontos de Melhoria:**
- Alguns componentes com responsabilidades múltiplas (ex: CdbComponent gerencia 3 tipos de liquidez)
- Lógica de negócio misturada com lógica de apresentação em alguns componentes
- Comentários em português e inglês misturados
- Alguns métodos longos que poderiam ser refatorados (ex: transformRelatorioData)
- Tratamento de erros genérico em alguns pontos
- Código comentado presente em alguns arquivos
- Falta de documentação JSDoc em alguns métodos públicos
- Alguns componentes com alta complexidade ciclomática

## 14. Observações Relevantes

- **Arquitetura**: Sistema segue padrão de micro-frontend, podendo ser empacotado como Web Component
- **Segurança**: Implementa validação por token em operações sensíveis (aplicação e resgate)
- **Responsividade**: Interface adaptada para mobile e desktop
- **Acessibilidade**: Uso de Angular Material que fornece componentes acessíveis
- **Performance**: Implementa lazy loading de fontes e Service Worker para PWA
- **Temas**: Suporta múltiplos temas (corporativo e private)
- **Internacionalização**: Usa moment.js com locale pt-BR para formatação de datas
- **Build**: Configurado para build otimizado com AOT, tree-shaking e code splitting
- **Testes**: Cobertura de testes unitários implementada com Jest
- **CI/CD**: Integração com SonarQube para análise de qualidade
- **Documentação**: Usa Compodoc para geração de documentação técnica
- **Versionamento**: Segue versionamento semântico (0.25.2)