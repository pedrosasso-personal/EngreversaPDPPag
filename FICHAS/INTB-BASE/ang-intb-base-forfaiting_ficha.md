# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema web front-end desenvolvido em Angular 7 para gestão de operações de **Forfaiting** (desconto de saque em operações de comércio exterior). O sistema permite realizar cotações indicativas de operações de Forfaiting e consultar operações desembolsadas (em aberto e liquidadas), com funcionalidades de download de documentos (avisos de vencimento e comprovantes).

---

## 2. Principais Classes e Responsabilidades

| Classe/Componente | Responsabilidade |
|-------------------|------------------|
| **CotacaoComponent** | Componente principal para realizar cotações de Forfaiting, validando datas, valores e calculando taxas de desconto |
| **CotacaoService** | Serviço responsável por comunicação com APIs de cotação, spreads, limites, feriados e gravação de cotações |
| **DesembolsadasComponent** | Componente container para exibição de operações desembolsadas |
| **DesembolsadasListaComponent** | Componente de listagem de operações com filtros por data e status (abertas/liquidadas) |
| **DesembolsadasService** | Serviço para consulta de operações desembolsadas e documentos PDF |
| **PdfsComponent** | Componente para download de PDFs (aviso de vencimento, comprovante de desembolso e liquidação) |
| **ModalComponent** | Componente genérico de modal para exibição de mensagens e confirmações |
| **CustomDateAdapter** | Adaptador customizado para formatação de datas no padrão brasileiro |
| **DateUtils** | Classe utilitária para manipulação e formatação de datas |
| **TipoMoeda** | Classe utilitária para conversão de códigos de moeda em símbolos |

---

## 3. Tecnologias Utilizadas

- **Angular 7.1.4** - Framework principal
- **Angular Material 7.1.1** - Biblioteca de componentes UI
- **RxJS 6.3.3** - Programação reativa
- **Moment.js 2.22.2** - Manipulação de datas
- **@arqt/spa-framework 1.8.5** - Framework corporativo do Banco Votorantim
- **@arqt/ui 1.3.0** - Biblioteca de componentes UI corporativos
- **@intb/commons 0.80.0** - Biblioteca de componentes compartilhados
- **ng2-currency-mask 9.0.2** - Máscara de moeda
- **ngx-daterangepicker-material 3.0.1** - Seletor de intervalo de datas
- **Jest 23.6.0** - Framework de testes
- **TypeScript 3.1.6** - Linguagem de programação
- **SCSS** - Pré-processador CSS
- **Docker** - Containerização (Apache HTTPD)
- **OpenShift** - Plataforma de deployment
- **JSON Server** - Mock de APIs para desenvolvimento

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/ib/portal/userdata` | CotacaoService, DesembolsadasService | Obtém dados do usuário logado |
| GET | `/atacado/plataformaCliente/consultarSpread` | CotacaoService | Consulta spreads do cliente por produto |
| GET | `/atacado/plataformaCliente/tempo/buscarHorario` | CotacaoService | Verifica horário de funcionamento e feriados |
| GET | `/atacado/plataformaCliente/tempo/listarFeriados` | CotacaoService | Lista feriados para validação de datas |
| GET | `/atacado/plataformaCliente/consultarLimite` | CotacaoService | Consulta limites operacionais do produto |
| GET | `/atacado/plataformaCliente/consultarTaxaTierCotacao` | CotacaoService | Calcula taxa TIR para cotação |
| POST | `/atacado/plataformaCliente/gravarCotacao` | CotacaoService | Grava cotação realizada no TradeFlex |
| GET | `/atacado/plataformaCliente/email/envioEmailForfating` | CotacaoService | Envia email quando cliente não possui spread |
| GET | `/atacado/plataformaCliente/obterParametro/1` | CotacaoService | Consulta se botão de pânico está ativo |
| GET | `/atacado/plataformaCliente/listarOperacoesDesembolsadas` | DesembolsadasService | Lista operações desembolsadas do cliente |
| GET | `/atacado/plataformaCliente/consultarAvisoVencimentos` | DesembolsadasService | Obtém PDF de aviso de vencimento |
| GET | `/atacado/plataformaCliente/consultarComprovanteDesembolso` | DesembolsadasService | Obtém PDF de comprovante (desembolso ou liquidação) |

---

## 5. Principais Regras de Negócio

1. **Validação de Horário de Funcionamento**: Sistema valida se a cotação está sendo realizada dentro do horário permitido (dias úteis)
2. **Validação de Feriados**: Datas de desembolso e vencimento não podem cair em feriados
3. **Validação de Limites Operacionais**: 
   - Valor da fatura não pode exceder limite máximo da operação
   - Data de desembolso não pode ser superior ao prazo máximo (qtDiasTermo)
   - Diferença entre desembolso e vencimento não pode exceder prazo máximo da operação (qtDiasOperacao)
4. **Cálculo de Taxa de Desconto**: Taxa = Spread do Cliente + Taxa TIR
5. **Cálculo de Valor de Desembolso**: Valor Desembolso = Valor Fatura / (1 + ((Taxa / 100) * (Dias / 360)))
6. **Validação de Spread Ativo**: Cliente deve possuir spread ativo para realizar cotações
7. **Botão de Pânico**: Sistema pode ser desabilitado remotamente via parâmetro
8. **Filtro de Operações**: Operações são separadas entre "Em Aberto" (statusLiquidacao = 'N') e "Liquidadas" (statusLiquidacao = 'S')
9. **Status de Operação**: 
   - "Contrato Fechado": sem PDF de desembolso
   - "Pago ao Exportador": com PDF de desembolso, sem liquidação
   - "Liquidado": com PDF de liquidação
10. **Período de Consulta Padrão**: 90 dias retroativos para listagem de operações

---

## 6. Relação entre Entidades

**UserDataModel**
- Contém dados do usuário logado
- Relaciona-se com ClientModel (current_client) e AccountModel (current_account)

**ClientModel**
- Representa o cliente atual
- Atributo principal: cdCliente (código do cliente)

**DesembolsadasModel**
- Representa uma operação de Forfaiting desembolsada
- Contém informações financeiras, datas e status
- Relaciona-se com TipoMoeda através de codigoMoeda

**Models de Request/Response**
- ConsultarParametroForfaiting: parâmetros do sistema
- SpreadRequestModel/SpreadResponseModel: spreads do cliente
- HorarioRequestModel/HorarioResponseModel: validação de horários
- TaxaTirRequestModel/TaxaTirResponseModel: cálculo de taxa
- GravarCotacaoRequestModel: dados para gravação de cotação
- LimiteResponseModel: limites operacionais
- ListarFeriadosModel: feriados para validação

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema é um front-end que consome APIs REST. Não há acesso direto a banco de dados.*

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema é um front-end que consome APIs REST. Não há acesso direto a banco de dados.*

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| aviso_vencimento_{codigo}.pdf | Gravação (download) | PdfsComponent | PDF com aviso de vencimento da operação |
| comprovante_desembolso_{codigo}.pdf | Gravação (download) | PdfsComponent | PDF com comprovante de desembolso |
| comprovante_liquidado_{codigo}.pdf | Gravação (download) | PdfsComponent | PDF com comprovante de liquidação |
| data.json | Leitura | JSON Server (mock) | Dados mockados para desenvolvimento local |
| routes.json | Leitura | JSON Server (mock) | Rotas mockadas para desenvolvimento local |
| rotas.conf | Leitura | Apache HTTPD | Configuração de proxy reverso para APIs |

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
| API Plataforma Cliente | REST API | Backend principal para operações de Forfaiting (cotações, consultas, limites) |
| API Portal Userdata | REST API | Serviço de dados do usuário logado |
| TradeFlex | Sistema Externo | Sistema onde as cotações são gravadas (via API) |
| Mesa Corporate | Telefone | Contato para operações que não podem ser realizadas pelo sistema |
| Apache HTTPD | Proxy Reverso | Servidor web que faz proxy das requisições para backends |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa organização modular com separação clara de responsabilidades (components, services, models)
- Uso adequado de TypeScript com tipagem de modelos
- Implementação de padrões Angular (Services, Components, Modules)
- Uso de RxJS para programação reativa
- Componentização adequada (modal, pdfs, timeline)
- Configuração de ambientes (dev/prod)
- Testes unitários configurados (Jest)
- Documentação inline com JSDoc
- Uso de bibliotecas corporativas padronizadas

**Pontos de Melhoria:**
- Lógica de negócio complexa dentro de componentes (CotacaoComponent com 400+ linhas)
- Comentários em código comentado (console.log, alerts) que deveriam ser removidos
- Mensagens de erro hardcoded em português (dificulta internacionalização)
- Falta de tratamento de erro mais robusto em alguns observables
- Código duplicado em validações de datas
- Classe TipoMoeda com JSON hardcoded (deveria vir de serviço/configuração)
- Alguns métodos muito longos que poderiam ser refatorados
- Falta de documentação de arquitetura e fluxos principais
- Uso de `any` em alguns tipos (deveria ser mais específico)

---

## 14. Observações Relevantes

1. **Ambiente de Desenvolvimento**: Sistema utiliza JSON Server para mock de APIs durante desenvolvimento local
2. **Deployment**: Aplicação containerizada com Docker (Apache HTTPD) e deployment via OpenShift
3. **Segurança**: Uso de chave pública RSA para criptografia (configurada em environment)
4. **Responsividade**: Sistema possui classes CSS específicas para modo "private" (provavelmente Private Banking)
5. **Service Worker**: Configurado para funcionamento offline (PWA)
6. **Compressão**: Apache configurado com compressão DEFLATE para otimização de performance
7. **Cache**: Configuração específica de cache para index.html (sem cache) e demais assets
8. **Moedas Suportadas**: Sistema suporta múltiplas moedas internacionais (USD, EUR, GBP, etc.)
9. **Formato de Data**: Sistema utiliza formato brasileiro (DD/MM/YYYY) com locale pt-BR
10. **Integração com Mesa**: Em casos de erro ou operações fora do horário, sistema direciona para contato telefônico
11. **Versionamento**: Projeto utiliza versionamento semântico (0.6.4)
12. **Monitoramento**: Integração com SonarQube para análise estática de código