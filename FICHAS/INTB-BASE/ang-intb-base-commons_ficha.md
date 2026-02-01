---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Este é um projeto de biblioteca de componentes compartilhados (commons) para aplicações Angular, desenvolvido em TypeScript. A biblioteca fornece componentes de interface de usuário (UI) reutilizáveis como botões, alertas, modais, tabelas, inputs, cards e outros elementos visuais padronizados. O projeto é containerizado com Docker e utiliza Apache HTTP Server para servir a aplicação compilada. A biblioteca suporta temas públicos e privados (white-label), com componentes adaptáveis através do serviço `PrivateService`.

### 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| `ActionBarComponent` | Barra de ação flutuante com animações de entrada/saída |
| `AlertComponent` | Sistema de alertas/notificações com suporte a ícones SVG customizados |
| `AlertService` | Gerenciamento centralizado de alertas (exibição, tipo, mensagem) |
| `BannerComponent` | Componente de banner com imagem, título e descrição |
| `ButtonComponent` | Botão customizável com múltiplos estilos e temas |
| `CardComponent` | Container de card com padding configurável |
| `CardContainerComponent` | Card com imagem, título, conteúdo e botões de ação |
| `CardValueIconComponent` | Card para exibir valor com ícone e label |
| `CheckTableComponent` | Tabela com checkboxes, ordenação, paginação e filtros |
| `CheckboxComponent` | Checkbox com suporte a temas |
| `DetailBarComponent` | Barra de detalhes com ações e labels |
| `DropdownComponent` | Dropdown/select customizável |
| `ExpansionPanelComponent` | Painel expansível do Material Design |
| `InputSearchComponent` | Campo de busca/pesquisa |
| `InputTextComponent` | Input de texto com validações, máscaras e formatações |
| `LoadingComponent` | Indicador de carregamento |
| `LoadingService` | Gerenciamento de estado de loading |
| `ModalComponent` | Sistema de modais responsivo (desktop/mobile) |
| `ModalService` | Gerenciamento de propriedades de modais |
| `ModalUploadComponent` | Modal especializado para upload de arquivos |
| `PilulasEstadoComponent` | Componente de pills/badges de estado |
| `RadioButtonComponent` | Botão de rádio customizável |
| `RadioGroupComponent` | Grupo de botões de rádio |
| `RangeDatePickerComponent` | Seletor de intervalo de datas |
| `SeeMoreTableComponent` | Controle de scroll horizontal para tabelas |
| `PrivateService` | Serviço para determinar tema público/privado |
| `CpfCnpjDirective` | Diretiva para máscara e validação de CPF/CNPJ |
| `RemoveTagsHtmlDirective` | Diretiva para remover tags HTML de inputs |

### 3. Tecnologias Utilizadas
- **Angular** (Framework principal)
- **TypeScript** (Linguagem de programação)
- **Angular Material** (Biblioteca de componentes UI)
- **SCSS** (Pré-processador CSS)
- **RxJS** (Programação reativa)
- **Moment.js** (Manipulação de datas)
- **ngx-daterangepicker-material** (Seletor de intervalo de datas)
- **ngx-mask** (Máscaras para inputs)
- **ng2-currency-mask** (Máscara de moeda)
- **ngx-device-detector** (Detecção de dispositivo)
- **Docker** (Containerização)
- **Apache HTTP Server** (Servidor web - Red Hat SCL httpd-24-rhel7)
- **Jest** (Framework de testes - mencionado na estrutura)
- **Jenkins** (Integração contínua - mencionado na estrutura)
- **SonarQube** (Análise de qualidade de código - mencionado na estrutura)

### 4. Principais Endpoints REST
não se aplica

### 5. Principais Regras de Negócio
- **Validação de CPF**: Implementa algoritmo completo de validação de CPF brasileiro, incluindo verificação de dígitos verificadores e rejeição de sequências repetidas
- **Validação de CNPJ**: Implementa algoritmo completo de validação de CNPJ brasileiro com verificação de dígitos verificadores
- **Máscara Dinâmica CPF/CNPJ**: Aplica máscara automaticamente conforme o usuário digita, alternando entre formato CPF (11 dígitos) e CNPJ (14 dígitos)
- **Validação de Telefone**: Valida formato de telefone brasileiro
- **Validação de Email**: Utiliza validador padrão do Angular para emails
- **Limite de Tamanho de Arquivo**: No upload, valida tamanho máximo configurável (padrão 5MB)
- **Formatos de Arquivo Aceitos**: Valida extensões de arquivo permitidas no upload (padrão PDF)
- **Detecção de Arquivos Duplicados**: Opcionalmente impede upload de arquivos com mesmo nome
- **Seleção de Intervalo de Datas**: Limita seleção a máximo de 89 dias, com data mínima de 2 anos atrás e máxima hoje
- **Intervalos Pré-definidos**: Oferece opções rápidas de 5, 30, 60 e 90 dias
- **Tema Público/Privado**: Aplica estilos diferentes baseado em configuração de tema (white-label)
- **Remoção de Tags HTML**: Remove automaticamente tags HTML de inputs de texto por segurança
- **Compressão de Assets**: Configuração Apache para compressão GZIP/DEFLATE de recursos estáticos
- **Cache de index.html**: Desabilita cache do arquivo index.html para garantir atualizações

### 6. Relação entre Entidades
não se aplica (biblioteca de componentes UI, sem modelo de dados de domínio)

### 7. Estruturas de Banco de Dados Lidas
não se aplica

### 8. Estruturas de Banco de Dados Atualizadas
não se aplica

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| token.json | leitura | assets/static/ | Arquivo de configuração com dados de token (SMS/email) |
| angular-httpd.conf | leitura | Docker | Configuração do Apache HTTP Server |
| Dockerfile | leitura | Docker | Definição da imagem Docker baseada em Red Hat httpd-24-rhel7 |
| index.html | gravação/leitura | Apache (runtime) | Arquivo principal da SPA, servido com cache desabilitado |
| dist/ | leitura | Docker COPY | Arquivos compilados da aplicação Angular |

### 10. Filas Lidas
não se aplica

### 11. Filas Geradas
não se aplica

### 12. Integrações Externas
não se aplica (biblioteca de componentes, sem integrações diretas)

### 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de componentes
- Uso adequado de TypeScript com interfaces e tipos definidos
- Implementação de padrões Angular (módulos, serviços, diretivas)
- Uso de RxJS para programação reativa (BehaviorSubject, Observables)
- Componentização adequada com responsabilidades bem definidas
- Suporte a temas (público/privado) através de serviço centralizado
- Uso de Angular Material para componentes base
- Validações robustas (CPF, CNPJ, email, telefone)
- Configuração Docker adequada com proxy settings e compressão

**Pontos de Melhoria:**
- Código comentado em vários locais (ex: LoadingService, CheckTableComponent) deveria ser removido
- Alguns componentes com lógica complexa no template que poderia ser extraída
- Falta de documentação JSDoc em muitos métodos
- Alguns componentes muito grandes (CheckTableComponent, ModalUploadContentComponent) poderiam ser refatorados
- Uso inconsistente de aspas simples e duplas
- Alguns magic numbers sem constantes nomeadas (ex: tamanhos, delays)
- Falta de tratamento de erros em alguns observables
- Alguns nomes de variáveis em português misturados com inglês
- Código de validação de CPF/CNPJ poderia ser extraído para funções auxiliares
- Falta de testes unitários nos arquivos fornecidos (apenas estrutura mencionada)

### 14. Observações Relevantes

1. **Arquitetura de Biblioteca**: Este é um projeto de biblioteca compartilhada (commons), não uma aplicação standalone, destinado a ser consumido por outras aplicações Angular

2. **Suporte Multi-tema**: Sistema robusto de temas com detecção automática via `PrivateService`, permitindo white-label

3. **Responsividade**: Componentes com suporte a desktop e mobile, com detecção via `ngx-device-detector`

4. **Internacionalização**: Uso de Moment.js com localização pt-BR para datas

5. **Segurança**: 
   - Remoção automática de tags HTML em inputs
   - Sanitização de SVG inline
   - Headers de segurança no Apache (Cache-Control, Pragma, Expires)

6. **Performance**:
   - ChangeDetectionStrategy.OnPush em alguns componentes
   - Compressão GZIP/DEFLATE configurada no Apache
   - Cache desabilitado apenas para index.html

7. **Containerização**: Imagem Docker baseada em Red Hat Enterprise Linux 7 com Apache 2.4

8. **Validações Brasileiras**: Implementações específicas para CPF, CNPJ e telefone brasileiro

9. **Acessibilidade**: Uso de aria-label em componentes como RadioGroup

10. **Animações**: Uso de Angular Animations para transições suaves (alerts, action-bar)

11. **Formulários Reativos**: Integração com Angular Reactive Forms para validação e controle de estado

12. **Máscaras Avançadas**: Suporte a máscaras de CPF/CNPJ dinâmicas, moeda, telefone e customizadas

13. **Upload de Arquivos**: Sistema completo com validação de formato, tamanho, duplicatas e preview

14. **Tabelas Avançadas**: Componente de tabela com ordenação, paginação, filtros e checkboxes

15. **Sistema de Modais**: Implementação dual para desktop (MatDialog) e mobile (MatBottomSheet)