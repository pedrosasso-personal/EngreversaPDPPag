# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema frontend Angular para gerenciamento de funcionalidades PIX do Banco Votorantim. Permite cadastro e gerenciamento de chaves PIX, transferências via chave ou dados bancários (agência/conta), consulta de limites, portabilidade e reivindicação de chaves. O sistema integra-se com APIs backend para operações PIX e oferece interface responsiva para usuários PF e PJ.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **CadastroComponent** | Gerencia cadastro de novas chaves PIX (CPF, CNPJ, email, telefone, EVP) |
| **MinhasChavesComponent** | Lista e exibe chaves PIX cadastradas pelo usuário |
| **PagamentosComponent** | Realiza transferências PIX usando agência e conta |
| **PagamentosChavesComponent** | Realiza transferências PIX usando chave PIX |
| **TransferenciaComponent** | Componente pai que gerencia abas de transferência |
| **DictService** | Serviço para operações de chaves PIX (cadastro, listagem, exclusão) |
| **PagamentosService** | Serviço para operações de pagamento e transferência |
| **FavoredService** | Gerencia favorecidos do usuário |
| **PortabilidadeComponent** | Gerencia solicitações de portabilidade de chaves |
| **ReinvidicacaoComponent** | Gerencia reivindicações de posse de chaves |
| **LimitesComponent** | Configuração de limites de transação PIX |
| **AdobeTagging** | Serviço de tagueamento para analytics Adobe |

## 3. Tecnologias Utilizadas
- **Framework Frontend**: Angular 7.1.4
- **Linguagem**: TypeScript 3.1.6
- **UI Components**: Angular Material 7.1.1, @intb/commons, @intb/ui, @arqt/ui
- **Gerenciamento de Estado**: RxJS 6.3.3, BehaviorSubject
- **Estilização**: SCSS, Angular Flex Layout 7.0.0
- **Testes**: Jest 23.6.0
- **Build**: Angular CLI 7.1.4, ng-packagr 4.4.0
- **HTTP Client**: Angular HttpClient
- **Validações**: @arqt/spa-framework (BvValidators)
- **Máscaras**: ngx-mask 7.9.10
- **Analytics**: Adobe Analytics, Google Analytics 4
- **Moment.js**: 2.29.4 (manipulação de datas)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/pix/chave-dict/no-token` | DictService | Cadastra chave PIX sem token |
| GET | `/v1/ib/pix/chave-dict` | DictService | Lista chaves PIX do usuário |
| POST | `/v1/ib/pix/chave-dict/remover` | DictService | Remove chave PIX |
| POST | `/v1/ib/pix/chave-dict/consultar` | PagamentosChavesService | Consulta informações de chave PIX |
| POST | `/v1/ib/pix/reivindicacao-portabilidade` | DictService | Solicita portabilidade/reivindicação |
| POST | `/v1/ib/pix/reivindicacao-portabilidade/listar` | DictService | Lista portabilidades/reivindicações |
| POST | `/v1/ib/pix/reivindicacao-portabilidade/confirmar` | DictService | Confirma portabilidade/reivindicação |
| POST | `/v1/ib/pix/reivindicacao-portabilidade/cancelar/no-token` | DictService | Cancela portabilidade/reivindicação |
| GET | `/v1/ib/pix/pagamento/consulta-status/{endToEnd}` | PagamentosService | Consulta status de pagamento |
| GET | `/v1/ib/pix/pagamento/consulta/conta` | PagamentosService | Consulta informações de conta |
| GET | `/v1/ib/pix/participante` | ParticipantesService | Lista instituições participantes do PIX |
| POST | `/v1/ib/comprovante/pdf` | PagamentosService | Gera comprovante PDF |
| POST | `/v1/ib/comprovante/pix-agendado/pdf` | PagamentosService | Gera comprovante de agendamento |
| GET | `/v1/ib/favorecidos` | FavoredService | Lista favorecidos |
| POST | `/v1/ib/favorecidos/remover` | FavoredService | Remove favorecido |
| POST | `/v1/ib/limites/cliente/inserir` | LimitesService | Define limites de transação |
| GET | `/v1/ib/limites/cliente/buscar` | LimitesService | Consulta limites configurados |

## 5. Principais Regras de Negócio
- **Limite de Chaves por Segmento**: PF pode cadastrar até 5 chaves, PJ até 20 chaves
- **Tipos de Chave Suportados**: CPF, CNPJ, Email, Telefone (celular), EVP (chave aleatória)
- **Validação de Chaves**: CPF/CNPJ validados com algoritmo específico, email com formato válido, telefone com máscara brasileira
- **Portabilidade**: Permite transferir chave de outra instituição para o BV (prazo de 7 dias para confirmação)
- **Reivindicação de Posse**: Permite reivindicar chave cadastrada por outro usuário (prazo de 7 dias para comprovação)
- **Agendamento**: Transferências podem ser agendadas até 12 meses no futuro
- **Mesma Titularidade**: Para contas BV, valida automaticamente se é mesma titularidade
- **Limites de Transação**: Limite configurável por transação e limite diário geral
- **Horário Noturno**: Limite especial de R$ 1.000,00 entre 20h e 6h
- **Favorecidos**: Permite salvar destinatários frequentes (chave ou agência/conta)
- **Validação de Saldo**: Verifica saldo antes de processar transferência
- **Comprovantes**: Geração de PDF para transações concluídas e agendadas
- **Token de Segurança**: Operações sensíveis requerem validação por token (SMS/email)

## 6. Relação entre Entidades

**DictModel** (Chaves PIX)
- `keysQuantity`: número de chaves cadastradas
- `possibleKeysQuantity`: número de chaves disponíveis
- `openClaimQuantity`: número de reivindicações abertas
- `keys[]`: lista de KeyModel

**KeyModel**
- `chave`: valor da chave
- `tipoChave`: tipo (CPF, CNPJ, PHONE, EMAIL, EVP)

**PortabilityAndOwnershipModel** (Portabilidade/Reivindicação)
- `id`: identificador
- `chave`: chave envolvida
- `tipoChave`: tipo da chave
- `status`: OPEN, WAITING_RESOLUTION, CANCELLED, CONFIRMED, COMPLETED
- `tipo`: PORTABILITY ou OWNERSHIP
- `doador`: instituição doadora
- `owner`: proprietário

**FavoredContactModel** (Favorecidos)
- `name`: nome do favorecido
- `document`: CPF/CNPJ
- `data[]`: lista de FavoredInfoModel (chaves ou contas)

**FavoredInfoModel**
- `type`: 'agencia' ou 'chave'
- `keyType`: tipo de chave (se aplicável)
- `key`: valor da chave
- `agency`, `account`, `accountType`: dados bancários (se aplicável)

**UserAccountModel** (Conta do Usuário)
- `type`: tipo de conta (CACC, SVGS, TRAN)
- `account`: número da conta
- `agency`: agência

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema frontend não acessa banco diretamente |

**Observação**: O sistema é uma aplicação frontend Angular que consome APIs REST. Não há acesso direto a banco de dados.

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| N/A | N/A | N/A | Sistema frontend não atualiza banco diretamente |

**Observação**: Todas as operações de escrita são realizadas via APIs REST do backend.

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `comprovante.pdf` | gravação | PagamentosComponent, PagamentosChavesComponent | Comprovante de transferência PIX gerado |
| `sessionStorage` | leitura/gravação | PagamentosService | Armazena dados temporários de pagamento (ete, comprovante) |
| `sessionStorage.tokenPayload` | leitura/gravação | ModalTokenComponent, CadastroComponent | Armazena payload do token de validação |
| `environment.ts` / `environment.prod.ts` | leitura | AppConfigurationService | Configurações de ambiente (URLs, chaves) |

## 10. Filas Lidas
não se aplica

## 11. Filas Geradas
não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **API Backend BV** | REST API | APIs para operações PIX (cadastro, transferência, consultas) - base URL configurável por ambiente |
| **Adobe Analytics** | Analytics | Tagueamento de eventos e page views para análise de comportamento |
| **Google Analytics 4** | Analytics | Rastreamento de interações e conversões do usuário |
| **Token Service** | REST API | Validação de tokens de segurança (SMS/email) via @intb/commons |
| **Banco Central - DICT** | Indireta | Consultas ao diretório de chaves PIX (via backend) |
| **Instituições Participantes PIX** | Indireta | Consulta de informações de bancos participantes (via backend) |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (components, services, models, pipes)
- Uso adequado de RxJS e Observables para gerenciamento de estado assíncrono
- Implementação de testes unitários com Jest
- Uso de TypeScript com tipagem adequada
- Componentização reutilizável (cards, modais, inputs)
- Implementação de analytics bem estruturada
- Uso de resolvers para carregamento de dados
- Pipes customizados para formatação (máscaras de CPF/CNPJ, telefone)

**Pontos de Melhoria:**
- Muitos comentários `/* istanbul ignore next */` indicando código não testado
- Componentes muito grandes com múltiplas responsabilidades (ex: PagamentosComponent, PagamentosChavesComponent com 500+ linhas)
- Lógica de negócio misturada com lógica de apresentação nos componentes
- Falta de tratamento consistente de erros em alguns fluxos
- Código duplicado entre PagamentosComponent e PagamentosChavesComponent
- Uso excessivo de `any` em alguns pontos
- Falta de documentação JSDoc em métodos complexos
- SessionStorage usado diretamente sem abstração adequada
- Alguns métodos muito longos que poderiam ser refatorados

## 14. Observações Relevantes

1. **Arquitetura**: Sistema construído como biblioteca Angular (`@intb/pix`) que pode ser consumida por outras aplicações do banco

2. **Segurança**: 
   - Uso de token de validação para operações sensíveis
   - Criptografia com chave pública RSA configurada
   - Validação de CPF/CNPJ no frontend e backend

3. **Responsividade**: Uso de Angular Flex Layout para layout responsivo

4. **Acessibilidade**: Implementação de modo "Private" para ocultar informações sensíveis

5. **Analytics**: Dupla implementação de tagueamento (Adobe e GA4) para análise detalhada de comportamento

6. **Agendamento**: Suporte a agendamento de transferências com validação de data (até 12 meses)

7. **Favorecidos**: Sistema de favorecidos permite salvar tanto chaves PIX quanto dados de agência/conta

8. **Status de Pagamento**: Polling a cada 3 segundos para verificar status de pagamentos em processamento

9. **Comprovantes**: Geração de PDF tanto para pagamentos imediatos quanto agendados

10. **Limites**: Sistema de limites configurável por transação e período (diário), com limite especial noturno

11. **Portabilidade/Reivindicação**: Fluxos complexos com prazos de 7 dias e múltiplos status

12. **Validações**: Validações robustas de formulários com feedback visual e mensagens de erro contextualizadas

13. **Mock Server**: Estrutura de mocks com json-server para desenvolvimento local

14. **Build**: Suporte a build de biblioteca e aplicação standalone, com possibilidade de uso como micro-frontend