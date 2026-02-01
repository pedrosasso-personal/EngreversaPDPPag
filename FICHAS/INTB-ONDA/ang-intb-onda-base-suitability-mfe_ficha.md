# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de Suitability (Perfil de Investidor) desenvolvido como Micro Frontend (MFE) em Angular 7. O sistema permite que clientes do Banco Votorantim realizem um questionário para identificar seu perfil de investidor (Conservador, Moderado ou Arrojado), visualizem seu perfil atual e refaçam o teste quando necessário. O MFE pode ser integrado em outras aplicações do Internet Banking.

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **SuitabilityMfeComponent** | Componente principal do MFE, orquestra a exibição do perfil e abertura dos modais |
| **PerfilSuitabilityComponent** | Exibe o perfil atual do investidor com opção de refazer o teste |
| **PerguntasSuitabilityComponent** | Gerencia o fluxo de perguntas do questionário de suitability |
| **PerfilSucessoComponent** | Exibe o resultado após conclusão do questionário |
| **ModalPerfilComponent** | Modal que contém o formulário completo de perguntas com navegação entre questões |
| **ModalResultadoComponent** | Modal que exibe o resultado calculado do perfil |
| **SuitabilityMfeService** | Serviço principal que gerencia dados do perfil, cálculo e persistência |
| **ApiSuitabilityService** | Serviço de comunicação com APIs REST do backend |
| **PerfilUsuarioService** | Gerencia dados temporários do usuário durante o preenchimento |
| **UserDataService** | Armazena dados do usuário (documento, tipo pessoa) |
| **ModalService** | Controla abertura e fechamento dos modais |
| **StepsService** | Gerencia progresso e navegação entre etapas do questionário |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal
- **TypeScript 3.1.6** - Linguagem de programação
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **Angular Flex Layout 7.0.0-beta.24** - Sistema de layout responsivo
- **RxJS 6.3.3** - Programação reativa
- **Jest 23.6.0** - Framework de testes unitários
- **@arqt/spa-framework 1.4.0** - Framework SPA customizado do banco
- **@intb/ui 0.29.0** - Biblioteca de componentes UI customizados
- **@intb/commons 0.80.0** - Biblioteca de utilitários comuns
- **JSON Server 0.14.0** - Mock server para desenvolvimento
- **OpenShift** - Plataforma de deployment (via configurações em openshift-as-code)
- **Apache HTTP Server** - Servidor web (configurado via rotas.conf)
- **Sonar** - Análise estática de código
- **Jenkins** - CI/CD

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/incluirSuitability` | ApiSuitabilityService | Salva/atualiza o perfil de suitability do cliente |
| GET | `/v1/ib/obterSuitability` | ApiSuitabilityService | Consulta o perfil de suitability atual do cliente |
| POST | `/v1/ib/calcularSuitability` | ApiSuitabilityService | Calcula o perfil do investidor baseado nas respostas |
| POST | `/api-utils/logger` | N/A | Envia logs da aplicação |
| GET | `/api-utils/status` | N/A | Health check do backend |

---

## 5. Principais Regras de Negócio

1. **Cálculo de Perfil**: O perfil do investidor é calculado com base em 10 perguntas (questionário 2) ou 16 perguntas (questionário 1), cada uma com peso específico
2. **Tipos de Perfil**: Três perfis possíveis - Conservador, Moderado e Arrojado (Agressivo)
3. **Validade do Perfil**: O perfil possui data de início e fim de vigência, com contagem de dias restantes
4. **Tipos de Resposta**: Suporta múltipla escolha, caixa de seleção e valores numéricos
5. **Validação de Soma**: Na questão 9, a soma dos percentuais deve totalizar exatamente 100%
6. **Navegação Sequencial**: O usuário deve responder as perguntas em ordem, não podendo avançar sem responder
7. **Identificação de Pessoa**: Diferencia pessoa física (CPF) e jurídica (CNPJ) pelo tamanho do documento
8. **Modo Private**: Suporta visualização diferenciada para clientes Private Banking
9. **Refazer Teste**: Permite que o cliente refaça o questionário a qualquer momento
10. **Persistência Temporária**: Dados são mantidos em serviços durante o preenchimento antes da persistência final

---

## 6. Relação entre Entidades

**Principais Modelos:**

- **PerfilInvestidorModel**: Entidade principal contendo numeroDocumento, tipoPessoa, questionario, listaRespostas, codigoPerfilInvestidor, nomePerfilInvestidor
- **QuestionarioModel**: Contém questionario (id), listaRespostas, codigoPerfilInvestidor, nomePerfilInvestidor
- **PerguntaModel**: Representa uma pergunta com descricao, respostas (array de OpcaoModel), peso, id, tipoResposta, respSelecionada
- **RespostaModel**: Contém pergunta (id), tipoResposta, listaItemResposta (array de ItemModel)
- **ItemModel**: Item de resposta com resposta (string) e valorResposta (opcional)
- **OpcaoModel**: Opção de resposta com descricao, valor, tipoPerfil, id
- **CardPerfilModel**: Modelo de apresentação com titulo, descricao, tipoBotao, icone

**Relacionamentos:**
- PerfilInvestidorModel 1:N RespostaModel
- RespostaModel 1:N ItemModel
- PerguntaModel 1:N OpcaoModel
- QuestionarioModel contém array de RespostaModel

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema consome dados via API REST, não acessa diretamente estruturas de banco |

**Observação**: Os dados são obtidos através do endpoint `/v1/ib/obterSuitability` que retorna o perfil do investidor já persistido.

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | O sistema persiste dados via API REST através do endpoint `/v1/ib/incluirSuitability` |

**Observação**: A persistência é realizada através de chamadas REST, não há acesso direto a estruturas de banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| questionario.ts | Leitura | SuitabilityMfeService | Contém as perguntas dos questionários (QUESTIONARIO e QUESTIONARIO_DOIS) |
| environment.ts / environment.prod.ts | Leitura | AppConfigurationService | Configurações de ambiente (URLs de API, chaves, etc) |
| data.json | Leitura | Mock Server | Dados mockados para desenvolvimento local |
| rotas.conf | Leitura | Apache/OpenShift | Configuração de proxy reverso para APIs |
| config-map.json | Leitura | OpenShift | Configurações de deployment |
| manifest.json | Leitura | Service Worker | Configuração PWA |

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
| API Suitability Backend | REST API | APIs para cálculo, consulta e persistência de perfil de investidor |
| API Utils | REST API | Serviços utilitários (logger, health check) |
| IB Antigo (Legacy) | HTTP | Sistema legado do Internet Banking (heartbeat) |
| Nexus NPM Registry | NPM | Repositório de pacotes NPM do banco |
| Sonar | HTTP | Análise estática de código |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (componentes, serviços, modelos)
- Uso adequado de TypeScript com tipagem forte através de interfaces e classes
- Implementação de padrões Angular (Observables, Reactive Forms, Services)
- Estrutura de testes configurada (Jest)
- Documentação JSDoc presente em alguns métodos
- Uso de bibliotecas corporativas padronizadas (@arqt, @intb)
- Configuração adequada para diferentes ambientes

**Pontos Negativos:**
- Lógica de negócio complexa concentrada em componentes (ModalPerfilComponent com 300+ linhas)
- Métodos muito longos e com múltiplas responsabilidades (ex: `habilitarBotao()`, `aplicarOpacidade()`)
- Uso excessivo de manipulação direta do DOM (getElementById, style.opacity)
- Falta de tratamento de erros em várias chamadas HTTP
- Código comentado e console.logs em produção
- Falta de testes unitários implementados (apenas estrutura)
- Nomenclatura inconsistente em alguns pontos (mix de português/inglês)
- Acoplamento forte entre componentes e serviços
- Falta de validações mais robustas em formulários

---

## 14. Observações Relevantes

1. **Arquitetura Micro Frontend**: O sistema foi desenvolvido como MFE para ser integrado em outras aplicações, com build específico para AngularJS (`build:lib:angularjs`)

2. **Dois Questionários**: Suporta dois tipos de questionários (1 com 16 perguntas, 2 com 10 perguntas), configurável via parâmetro

3. **Mock Server**: Possui estrutura completa de mock server (JSON Server) para desenvolvimento local independente do backend

4. **Deployment OpenShift**: Configuração completa para deployment em OpenShift com ConfigMaps e DeploymentConfigs

5. **Service Worker**: Configurado para funcionar como PWA com estratégias de cache

6. **Temas**: Suporta tema corporativo e modo Private Banking com ícones e estilos diferenciados

7. **Navegação Controlada**: Implementa navegação sequencial com controle de opacidade e habilitação/desabilitação de campos

8. **Integração com Framework Corporativo**: Utiliza extensivamente bibliotecas internas (@arqt/spa-framework, @intb/ui, @intb/commons)

9. **CI/CD**: Configurado para Jenkins com propriedades específicas (jenkins.properties)

10. **Análise de Qualidade**: Integrado com SonarQube para análise estática contínua

11. **Versionamento**: Versão atual 1.42.0 da aplicação e 0.0.7 da biblioteca MFE

12. **Compatibilidade**: Requer Node.js 8+ e NPM 5.5.1+