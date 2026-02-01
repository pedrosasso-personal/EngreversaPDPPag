# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema Angular de Open Banking/Open Finance desenvolvido para o Banco BV. A aplicação gerencia o compartilhamento de dados financeiros entre instituições, permitindo consentimentos de transmissão e recepção de dados, além de operações de pagamento via Pix através do Open Finance. O sistema implementa fluxos de autorização, gestão de consentimentos, visualização de compartilhamentos ativos/encerrados e processamento de pagamentos instantâneos.

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **ConsentComponent** | Gerencia o fluxo de consentimento para compartilhamento de dados, incluindo seleção de modalidades e contas |
| **PaymentComponent** | Controla operações de pagamento e agendamento via Pix Open Finance |
| **DataSharingComponent** | Gerencia o processo de compartilhamento de dados entre instituições |
| **TransmittedComponent** | Lista e gerencia consentimentos transmitidos (enviados) |
| **DetailExpansiveComponent** | Exibe detalhes expandidos de compartilhamentos com ações de renovação/encerramento |
| **ConsentService** | Serviço para operações de consentimento (aceitar, rejeitar, revogar) |
| **PaymentService** | Serviço para operações de pagamento e validação |
| **DataSharingService** | Serviço para gerenciar compartilhamento de dados e objetivos |
| **GoogleTagManagerService** | Gerencia tagueamento e analytics via Google Tag Manager |
| **FeatureToggleService** | Gerencia feature flags via ConfigCat |
| **PcmService** | Gerencia redirecionamentos no fluxo híbrido PCM (Payment Consent Management) |

## 3. Tecnologias Utilizadas

- **Framework Frontend**: Angular 7.1.4
- **UI Components**: Angular Material 7.1.1, @intb/commons, @intb/ui
- **Gerenciamento de Estado**: RxJS 6.3.3, BehaviorSubject
- **Roteamento**: Angular Router
- **Estilização**: SCSS, Angular Flex Layout
- **HTTP Client**: Angular HttpClient
- **Feature Flags**: ConfigCat 5.5.2
- **Analytics**: Google Tag Manager (via @intb/commons)
- **Testes**: Jest 23.6.0
- **Build**: Angular CLI 7.1.4, Webpack
- **Criptografia**: JSEncrypt 3.0.0-rc.1, crypto-js 4.2.0
- **Detecção de Dispositivo**: ngx-device-detector
- **Moment.js**: 2.22.2 (manipulação de datas)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/ib/open-banking/consents/{consentId}/interaction/{interactionId}/accept` | ConsentService | Aceita um consentimento de compartilhamento |
| POST | `/v1/ib/open-banking/consents/{consentId}/interaction/{interactionId}/reject` | ConsentService | Rejeita um consentimento |
| POST | `/v1/ib/open-banking/managed-consents/{consentId}/revoke` | ConsentService | Revoga um consentimento transmitido |
| DELETE | `/v1/ib/reception/removeConsent` | ConsentService | Remove um consentimento recebido |
| GET | `/v1/ib/open-banking/managed-consents` | ConsentService | Lista consentimentos transmitidos |
| GET | `/v1/ib/open-banking/consents` | ConsentService | Lista consentimentos recebidos |
| GET | `/v1/ib/open-banking/consents/interaction/{interactionId}/resume` | ConsentService | Obtém resumo do consentimento |
| GET | `/v1/ib/open-detentora/consents/interaction/{interactionId}` | PaymentService | Obtém dados de pagamento |
| POST | `/v1/ib/open-detentora/consents/{consentId}/interaction/{interactionId}/selectedAccount/{account}/accept` | PaymentService | Aceita pagamento |
| POST | `/v1/ib/open-detentora/consents/{consentId}/interaction/{interactionId}/selectedAccount/{account}/cancel` | PaymentService | Cancela pagamento |
| POST | `/v1/ib/open-detentora/consents/interaction/{interactionId}/validate` | PaymentService | Valida dados de pagamento |
| GET | `/v1/ib/reception/objectives` | DataSharingService | Lista objetivos de compartilhamento |
| GET | `/v1/ib/reception/institutions` | DataSharingService | Lista instituições participantes |
| GET | `/v1/ib/reception/data-groups/{objectiveId}` | DataSharingService | Obtém grupos de dados por objetivo |
| POST | `/v1/ib/reception/createConsent` | DataSharingService | Cria novo consentimento de recepção |
| POST | `/v1/ib/open-banking/hybrid-flow/server/redirect-to-client` | PcmService | Redireciona para cliente no fluxo híbrido |
| POST | `/v1/ib/open-banking/hybrid-flow/client/redirect-to-server` | PcmService | Redireciona para servidor no fluxo híbrido |
| GET | `/v1/ib/portal/userdata` | AppService | Obtém dados do usuário logado |

## 5. Principais Regras de Negócio

1. **Validação de CPF/CNPJ**: O documento do usuário logado deve corresponder ao documento informado na instituição iniciadora
2. **Timeout de Consentimento**: Consentimentos pendentes expiram após 60 minutos
3. **Timeout de Pagamento**: Operações de pagamento devem ser concluídas antes da meia-noite do dia do agendamento
4. **Aprovadores Múltiplos**: Transações podem requerer aprovação de múltiplos aprovadores
5. **Validação de Conta**: A conta selecionada deve permitir operações de pagamento e ter saldo suficiente
6. **Prazo de Compartilhamento**: Compartilhamentos podem ter prazo determinado (1-12 meses) ou indeterminado
7. **Status de Consentimento**: Ativo, Pendente, Encerrado, Vencido, Temporariamente Indisponível
8. **Renovação de Compartilhamento**: Encerra o compartilhamento atual e cria um novo com os mesmos dados
9. **Modalidades de Dados**: Dados Cadastrais, Conta, Cartão de Crédito, Operações de Crédito, Investimentos, Câmbio
10. **Segmentação de Cliente**: Clientes Private têm acesso a modalidades adicionais de investimento
11. **Redirecionamento Seguro**: Após autorização, redireciona para instituição iniciadora via Open Finance
12. **Feature Flags**: Funcionalidades controladas por feature toggles (ConfigCat)

## 6. Relação entre Entidades

**ConsentModel**
- consentId: string
- interactionId: string
- status: string
- brandName/brandId: identificação da marca
- modalityList: Array<ModalityModel>

**ModalityModel**
- id: number
- name: string
- accounts: Array (contas associadas)
- subModalityList: Array<SubModality>

**PaymentData**
- consentId: string
- paymentType: string
- accountNumberList/accountNumberSelected: string[]
- creditorName/creditorDocument: dados do beneficiário
- paymentValue: number
- paymentDate/expirationDate: datas
- validation: PaymentDataValidation

**DataSharingConsent**
- brandId: string
- institutionId: string
- objectiveId: number
- durationInMonths: number
- permissions: Array<string>

**Resume**
- approversList: Array<Aprover>
- receptorBank: string
- userDocument: string
- timePeriod: string

## 7. Estruturas de Banco de Dados Lidas

não se aplica (aplicação frontend Angular)

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica (aplicação frontend Angular)

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Descrição |
|-----------------|----------|-------------------------|-----------|
| environment.ts / environment.prod.ts | leitura | AppConfigurationService | Configurações de ambiente (URLs de API, chaves públicas) |
| assets/images/svg/*.svg | leitura | Diversos componentes | Ícones e imagens SVG da aplicação |
| manifest.json | leitura | Service Worker | Manifesto PWA |
| ngsw-config.json | leitura | Service Worker | Configuração do Service Worker |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Descrição |
|-----------------|-----------|
| **API Backend BV** | API REST principal para operações de Open Banking (consentimentos, pagamentos, dados) |
| **ConfigCat** | Serviço de feature flags para controle de funcionalidades |
| **Google Tag Manager** | Plataforma de analytics e tagueamento de eventos |
| **Instituições Financeiras Externas** | Redirecionamento via Open Finance para instituições participantes |
| **Nexus (NPM Registry)** | Repositório de pacotes NPM do Banco BV |

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (services, components, models)
- Uso adequado de RxJS e programação reativa
- Implementação de feature toggles para controle de funcionalidades
- Cobertura de testes unitários com Jest
- Uso de TypeScript com tipagem adequada
- Implementação de analytics e tagueamento estruturado
- Sanitização de inputs em serviços críticos (PaymentService)

**Pontos de Melhoria:**
- Presença excessiva de comentários `/* istanbul ignore next */` indicando código não testado
- Alguns componentes com lógica de negócio complexa que poderia ser extraída para services
- Uso de `console.log` em código de produção
- Alguns métodos muito extensos que poderiam ser refatorados
- Falta de tratamento de erro consistente em algumas chamadas HTTP
- Código comentado em alguns arquivos
- Algumas strings hardcoded que poderiam estar em arquivos de configuração/i18n

## 14. Observações Relevantes

1. **Arquitetura SPA**: Aplicação Single Page Application com lazy loading de módulos
2. **Biblioteca Compartilhada**: Projeto estruturado como biblioteca Angular (`@intb/open-banking`) para reutilização
3. **Segurança**: Implementa criptografia RSA (JSEncrypt) e sanitização de inputs
4. **Responsividade**: Uso de Angular Flex Layout e detecção de dispositivos
5. **PWA**: Configurado como Progressive Web App com Service Worker
6. **Acessibilidade**: Uso de Material Design com suporte a acessibilidade
7. **Versionamento**: Versão 0.74.0 indica projeto em evolução ativa
8. **Compatibilidade**: Suporte a IE11 através de polyfills
9. **Fluxo Híbrido PCM**: Implementação de fluxo híbrido para redirecionamento seguro entre instituições
10. **Segmentação**: Diferenciação de funcionalidades entre clientes Corporate e Private
11. **Monitoramento**: Integração com Sonar para análise estática de código
12. **Build**: Configuração para build otimizado em produção com AOT compilation