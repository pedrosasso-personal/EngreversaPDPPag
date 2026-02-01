# Ficha Técnica do Sistema

## 1. Descrição Geral
Sistema de gerenciamento de mensagens SPB (Sistema de Pagamentos Brasileiro) desenvolvido em Spring Boot. O sistema é responsável por processar, cadastrar, validar e controlar fluxos de mensagens financeiras, incluindo operações de batimento, consultas automáticas, geração de extratos CIP, controle de grades horárias e integração com câmaras de compensação. Trata-se de um serviço atômico (Atomic) seguindo a arquitetura Atlante do Banco Votorantim.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal de inicialização da aplicação Spring Boot com configuração de segurança JWT |
| `AppConfiguration` | Configuração central de beans da aplicação, incluindo serviços, mappers e conversores HTTP |
| `JdbiConfiguration` | Configuração do framework JDBI para acesso a banco de dados, incluindo plugins e repositórios |
| `Slf4jSqlLogger` | Logger customizado para registrar execuções SQL via JDBI |
| `GlobalExceptionHandler` | Tratamento centralizado de exceções da aplicação |
| `BusinessException` | Exceção genérica de negócio |
| `RegraNegocioException` | Exceção específica para violações de regras de negócio |
| `IspbGenericUtils` | Utilitários genéricos incluindo configuração de ModelMapper e tratamento de ações de usuário |
| `PopulaDto` | Utilitário para popular DTOs de requisição |
| `Sanitizador` | Utilitário para sanitização de strings contra injeção de código |

## 3. Tecnologias Utilizadas
- **Framework Principal**: Spring Boot 2.7.x
- **Linguagem**: Java 11+
- **Gerenciamento de Dependências**: Maven 3.8+
- **Banco de Dados**: Sybase ASE (via driver jConnect 16.3-SP03-PL07)
- **Framework de Acesso a Dados**: JDBI 3.9.1 (SQL Object, StringTemplate4)
- **Mapeamento de Objetos**: MapStruct, ModelMapper 3.1.0
- **Segurança**: Spring Security OAuth2 Resource Server com JWT
- **Serialização JSON**: Jackson com suporte a Java Time Module
- **Documentação API**: OpenAPI 3 / Swagger UI
- **Logging**: Logback com formato JSON
- **Servidor de Aplicação**: Tomcat Embed 9.0.111
- **Monitoramento**: Spring Boot Actuator com Prometheus
- **Utilitários**: Apache Commons Lang3, Lombok

## 4. Principais Endpoints REST
Não identificados neste pacote de fontes. A documentação menciona que os endpoints podem ser visualizados em `http://localhost:8080/swagger-ui/index.html`, mas as implementações não foram fornecidas nesta iteração.

## 5. Principais Regras de Negócio
- **Validação de Mensagens**: Sistema valida layouts de mensagens através do `LayoutMensagemCheckService`
- **Batimento de Mensagens**: Processo de conciliação de mensagens financeiras via `BatimentoMensagemService`
- **Controle de Duplicidade**: Verificação e tratamento de mensagens duplicadas através do `CadastroMensagemDuplicadaService`
- **Agendamento vs Digitação**: Diferenciação entre operações agendadas e digitadas imediatamente (flag "S" indica agendamento)
- **Operações Permitidas**: Controle de operações que permitem confirmação pelo mesmo usuário que digitou (ex: OPLTR003)
- **Níveis de Acesso**: Sistema de controle de acesso com níveis: COMPLETO, CONSULTAR, INCLUIR, ALTERAR, EXCLUIR, CONFIRMAR
- **Instituições**: Suporte a múltiplas instituições (BV - ISPB 59588111, BVSA - ISPB 01858774)
- **Sanitização de Dados**: Escape de caracteres especiais para prevenção de injeção de código

## 6. Relação entre Entidades
Não foi possível identificar completamente neste pacote. As seguintes entidades/serviços foram identificados:
- **GradeHorario**: Controle de grades horárias
- **GeracaoExtratoCip**: Geração de extratos CIP
- **ErroMensagem**: Registro de erros em mensagens
- **FluxoMensagem**: Controle de fluxo de mensagens
- **FluxoMovimento**: Movimentações de fluxo
- **BatimentoMensagem**: Batimento/conciliação de mensagens
- **CadastroMensagem**: Cadastro principal de mensagens
- **CadastroMensagemDuplicada**: Controle de mensagens duplicadas
- **ModuloCamara**: Módulo de câmara de compensação
- **ModuloCamaraDtvm**: Módulo específico para DTVM
- **ModuloOperacional**: Módulo operacional
- **ModuloLiquidacao**: Módulo de liquidação
- **PopupServicos**: Serviços de popup
- **ConsultaOperacaoAutomatica**: Consultas automáticas de operações
- **InformeOperProcessadas**: Informes de operações processadas

## 7. Estruturas de Banco de Dados Lidas
Não se aplica - as queries específicas não foram fornecidas neste pacote de fontes. Os repositórios foram identificados mas suas implementações SQL não estão presentes.

## 8. Estruturas de Banco de Dados Atualizadas
Não se aplica - as queries específicas não foram fornecidas neste pacote de fontes. Há evidências de operações de UPDATE através do `UpdateDebCredRequest`, mas os detalhes das tabelas não foram fornecidos.

## 9. Arquivos Lidos e Gravados
Não se aplica - não foram identificados processamentos de arquivos neste pacote de fontes.

## 10. Filas Lidas
Não se aplica - não foram identificadas integrações com sistemas de mensageria neste pacote de fontes.

## 11. Filas Geradas
Não se aplica - não foram identificadas integrações com sistemas de mensageria neste pacote de fontes.

## 12. Integrações Externas
- **Servidor de Autenticação OAuth2/JWT**: 
  - Ambiente DEV: `https://api-des.bancovotorantim.com.br:443`
  - JWKS URL: `https://apigatewaydes.bvnet.bv/openid/connect/jwks.json`
- **Banco de Dados Sybase**: `sybuatbco.bvnet.bv:3400/DBISPB`

## 13. Avaliação da Qualidade do Código

**Nota:** 8/10

**Justificativa:**
- **Pontos Positivos**:
  - Excelente organização em camadas (config, service, repository, mapper)
  - Uso adequado de injeção de dependências via Spring
  - Implementação de tratamento centralizado de exceções
  - Configuração de logging estruturado em JSON
  - Uso de MapStruct para mapeamento de objetos
  - Sanitização de inputs para segurança
  - Configuração adequada de segurança OAuth2/JWT
  - Documentação via OpenAPI/Swagger
  - Separação de perfis de configuração (local, uat, des, prd)
  
- **Pontos de Melhoria**:
  - Uso de `@Lazy` e `allow-circular-references: true` indica possível dependência circular entre beans
  - Classe `IspbGenericUtils` mistura responsabilidades (ModelMapper e lógica de negócio)
  - Falta de documentação JavaDoc nas classes
  - Configuração de segurança desabilitada no perfil local pode ser arriscada

## 14. Observações Relevantes
- Sistema segue arquitetura Atlante do Banco Votorantim
- Aplicação expõe métricas Prometheus na porta 9090
- Suporte a múltiplos ambientes via profiles Spring
- Configuração de retry e timeout via bootstrap.sh
- Sistema utiliza charset ISO-1 para conexão Sybase
- Cookies de sessão configurados com flags de segurança (http-only, secure)
- Logging de todas as queries SQL executadas
- Sistema não renderiza campos null nas respostas JSON

## 15. Histórico da Iteração

### Iteração 1
- Análise inicial do pacote de configuração e classes base
- Identificação de 15+ serviços e repositórios relacionados a mensagens SPB
- Mapeamento de tecnologias utilizadas (Spring Boot, JDBI, Sybase, OAuth2)
- Identificação de enums de negócio (AcaoUsuario, InstituicaoEnum, NivelAcessoEnum, OperacoesPermitidasEnum)
- Documentação de classes utilitárias e tratamento de exceções
- Análise de configurações de ambiente e segurança