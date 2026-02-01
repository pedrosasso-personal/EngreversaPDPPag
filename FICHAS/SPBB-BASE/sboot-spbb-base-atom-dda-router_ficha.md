# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-spbb-base-atom-dda-router** é um serviço atômico desenvolvido em Java com Spring Boot, responsável por centralizar o envio de solicitações de baixa de boleto e cancelamento de baixa de boleto para a Nuclea (CIP - Câmara Interbancária de Pagamentos) através das mensagens DDA0108 e DDA0115. O sistema atua como um roteador que recebe requisições REST, gera mensagens XML no padrão DDA, criptografa essas mensagens utilizando o serviço SPBSecJava (EVALCryptoSPB) e as envia para filas IBM MQ específicas de acordo com o ISPB (Identificador do Sistema de Pagamentos Brasileiro) do banco destinatário (Banco Votorantim - BV ou Banco Votorantim S.A. - BVSA).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application.java` | Classe principal de inicialização da aplicação Spring Boot |
| `DdaRouterApiDelegateImpl` | Implementa os endpoints REST para solicitação e cancelamento de baixa de boleto |
| `DdaRouterService` | Contém a lógica de negócio principal para processamento das solicitações de baixa |
| `EncryptService` | Responsável pela criptografia das mensagens utilizando SPBSecJava |
| `DdaRouterJMSRepositoryImpl` | Implementa o envio de mensagens para as filas IBM MQ |
| `DDAMapper` | Realiza o mapeamento entre objetos de representação (API) e objetos de domínio |
| `DDAUtil` | Classe utilitária com funções auxiliares para processamento DDA |
| `MensagemUtil` | Responsável pela geração das mensagens XML DDA0108 e DDA0115 |
| `FeatureToggleService` | Gerencia feature flags da aplicação |
| `JmsConfig` | Configuração das conexões JMS com IBM MQ |
| `DdaRouterConfiguration` | Configuração geral dos beans da aplicação |
| `DecryptConfiguration` | Configuração do serviço de criptografia SPBSecJava |
| `APIKeyAuthFilter` | Filtro de autenticação por API Key |

---

## 3. Tecnologias Utilizadas

- **Java 11+**
- **Spring Boot 2.x** (framework principal)
- **Spring Security** (autenticação e autorização)
- **Spring JMS** (integração com filas)
- **IBM MQ** (middleware de mensageria)
- **SPBSecJava 1.0.6** (biblioteca de criptografia para SPB)
- **Maven 3.8+** (gerenciamento de dependências)
- **Lombok** (redução de código boilerplate)
- **Gson** (serialização/deserialização JSON)
- **OpenAPI 3.0** (documentação de API)
- **Swagger UI** (interface de documentação)
- **Logback** (framework de logging)
- **Spring Retry** (mecanismo de retry)
- **Feature Toggle** (gerenciamento de features)
- **OAuth2/JWT** (autenticação)
- **Apache Commons Text** (manipulação de strings)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/solicitarBaixaBoleto` | `DdaRouterApiDelegateImpl` | Solicita a baixa de um boleto através da mensagem DDA0108 |
| POST | `/v1/cancelarBaixaBoleto` | `DdaRouterApiDelegateImpl` | Cancela uma baixa de boleto previamente solicitada através da mensagem DDA0115 |

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Baixa**: Para determinados tipos de baixa (TpBaixa), campos específicos são obrigatórios ou opcionais. Por exemplo, para TpBaixa 5, 6, 7 e 8, campos opcionais como ISPBPartRecbdrBaixa, VlrBaixaTit e CanPgto são removidos.

2. **Geração de Número de Operação (NuOp)**: O sistema gera um número único de operação composto por um prefixo (89 para cobrança ou 99 para SPAG) concatenado com um sequencial de 7 dígitos.

3. **Roteamento por ISPB**: As mensagens são roteadas para filas específicas (BV ou BVSA) com base no ISPB do participante recebedor principal.

4. **Criptografia Obrigatória**: Todas as mensagens enviadas para a CIP devem ser criptografadas utilizando o serviço SPBSecJava antes do envio.

5. **Formatação de CPF/CNPJ**: O sistema completa CPF/CNPJ com zeros à esquerda conforme o tipo de pessoa (F para física, J para jurídica).

6. **Validação de Agência Recebedora**: Para certos tipos de baixa, o campo AgRecbdr é obrigatório.

7. **Remoção de Caracteres Especiais**: As mensagens XML têm caracteres especiais removidos para garantir conformidade com o padrão.

8. **Ajuste de Data/Hora**: O sistema ajusta automaticamente datas e horas de processamento, subtraindo 5 segundos para evitar erros de sincronização com a CIP.

9. **Retry de Criptografia**: O serviço de criptografia possui mecanismo de retry (2 tentativas com delay de 500ms) em caso de falha.

10. **Gerenciamento de Pool de Servidores**: O sistema mantém um pool de conexões com servidores de criptografia (EVAL) e verifica o status das conexões.

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **DDA0108**: Representa uma solicitação de baixa de boleto
  - Atributos: ispbPartRecbdrPrincipal, ispbPartRecbdrAdmtd, numIdentcTit, tpBaixa, ispbPartRecbdrBaixa, codPartRecbdrBaixa, tpPessoaPort, cnpjCpfPort, nomRzSocPort, tpPessoaAgrgdr, cnpjCpfAgrgdr, nomRzSocAgrgdr, agRecbdr, dtHrRecbtTit, vlrBaixaTit, numCodBarrasBaixa, canPgto, meioPgto, indrOpContg, ispbInidrPgto, dtMovto, numCtrlPart, complNumOprc

- **DDA0115**: Representa um cancelamento de baixa de boleto
  - Atributos: ispbPartRecbdrPrincipal, ispbPartRecbdrAdmtd, numIdentcBaixa, dtHrCanceltBaixa, dtMovto, numCtrlPart

- **DDA0106**: Entidade de domínio (não utilizada diretamente nos endpoints)
  - Atributos: numCtrlPart, ispbPartRecbdrPrincipal, ispbPartRecbdrAdmtd, numCodBarras, tpRet, sitTit, dtMovto

- **DDA0110**: Entidade de domínio (não utilizada diretamente nos endpoints)
  - Atributos: numCtrlPart, ispbPartRecbdrPrincipal, ispbPartRecbdrAdmtd, numCodBarras, dtMovto

**Relacionamentos:**
- DDA0108Representation → DDA0108 (mapeamento via DDAMapper)
- DDA0115Representation → DDA0115 (mapeamento via DDAMapper)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação (leitura/gravação) | Local/Classe Responsável | Breve Descrição |
|-----------------|----------------------------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot Configuration | Arquivo de configuração principal da aplicação |
| `application-local.yml` | Leitura | Spring Boot Configuration | Arquivo de configuração para ambiente local |
| `logback-spring.xml` | Leitura | Logback Framework | Configuração de logs da aplicação |
| `openapi.yaml` | Leitura | OpenAPI Generator | Especificação da API REST |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

**Filas IBM MQ:**

1. **Fila BV (Banco Votorantim)**
   - Nome da fila: `QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT` (ambiente local/des)
   - Queue Manager: `QM.ATA.01`
   - Canal: `SPAG.SRVCONN`
   - Classe responsável: `DdaRouterJMSRepositoryImpl` (via `jmsTemplateBV`)
   - Descrição: Fila para envio de mensagens DDA criptografadas para o Banco Votorantim (ISPB: 59588111)

2. **Fila BVSA (Banco Votorantim S.A.)**
   - Nome da fila: `QL.SPAG.BANCO_LIQUIDANTE_RECEBIMENTO_REQ.INT` (ambiente local/des)
   - Queue Manager: `QM.ATA.01`
   - Canal: `SPAG.SRVCONN`
   - Classe responsável: `DdaRouterJMSRepositoryImpl` (via `jmsTemplateBVSA`)
   - Descrição: Fila para envio de mensagens DDA criptografadas para o Banco Votorantim S.A. (ISPB: 01858774)

---

## 12. Integrações Externas

1. **SPBSecJava (EVALCryptoSPB)**
   - Tipo: Serviço de criptografia
   - Endereços: srv-evaluat01.bvnet.bv, srv-evaluat02.bvnet.bv (ambiente local)
   - Porta: 10000
   - Descrição: Serviço responsável pela criptografia das mensagens DDA antes do envio para a CIP
   - Classe responsável: `EncryptService`

2. **Nuclea (CIP - Câmara Interbancária de Pagamentos)**
   - Tipo: Sistema externo
   - ISPB: 17423302
   - Descrição: Destinatário final das mensagens DDA0108 e DDA0115 para processamento de baixas de boleto
   - Integração via: Filas IBM MQ

3. **Feature Toggle Service**
   - Tipo: Serviço de gerenciamento de features
   - Descrição: Controla habilitação/desabilitação de funcionalidades via feature flags
   - Classe responsável: `FeatureToggleService`

4. **OAuth2/JWT Provider**
   - Tipo: Serviço de autenticação
   - Issuer URI: https://api-des.bancovotorantim.com.br:443 (ambiente des)
   - JWK Set URI: https://apigatewaydes.bvnet.bv/openid/connect/jwks.json
   - Descrição: Provedor de autenticação e autorização via tokens JWT

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem estruturado seguindo padrões de arquitetura limpa (separação clara entre camadas: rest, service, repository, domain)
- Uso adequado de injeção de dependências e inversão de controle
- Implementação de tratamento de erros e logging estruturado
- Utilização de Lombok para redução de boilerplate
- Documentação OpenAPI bem definida
- Implementação de retry e reconexão para serviços críticos
- Uso de feature toggles para controle de funcionalidades
- Separação de configurações por ambiente
- Testes unitários presentes (embora não analisados em detalhe)

**Pontos de Melhoria:**
- Algumas classes utilitárias (MensagemUtil, DDAUtil) possuem métodos muito extensos que poderiam ser refatorados
- Uso de `StringBuilder` manual para construção de XML poderia ser substituído por bibliotecas especializadas (JAXB, Jackson XML)
- Alguns métodos possuem múltiplas responsabilidades (ex: `getMsgEncrypt` faz inicialização e criptografia)
- Falta de constantes para alguns valores "mágicos" espalhados pelo código
- Tratamento de exceções genérico em alguns pontos (`catch (Exception e)`)
- Comentários em português misturados com código em inglês
- Alguns logs poderiam ser mais informativos (níveis de log adequados)

---

## 14. Observações Relevantes

1. **Segurança**: O sistema utiliza múltiplas camadas de segurança incluindo OAuth2/JWT, API Key authentication e criptografia de mensagens via SPBSecJava.

2. **Ambientes**: A aplicação está preparada para múltiplos ambientes (local, des, uat, prd) com configurações específicas para cada um.

3. **Monitoramento**: Exposição de endpoints Actuator (health, metrics, prometheus) na porta 9090 para monitoramento da aplicação.

4. **Padrão de Mensagens**: As mensagens DDA seguem o padrão XML definido pelo Banco Central do Brasil para o Sistema de Pagamentos Brasileiro (SPB).

5. **Sincronização Temporal**: O sistema implementa ajustes de tempo (subtração de 5 segundos) para evitar problemas de sincronização com a CIP.

6. **Pool de Conexões**: Implementação de pool de conexões JMS com cache de sessões (tamanho 10) e reconexão automática.

7. **Normalização de Dados**: Remoção automática de caracteres especiais e acentuação nas mensagens XML para garantir conformidade.

8. **Versionamento de API**: API versionada (v1) permitindo evolução futura sem quebra de compatibilidade.

9. **Docker Ready**: Projeto preparado para containerização com Dockerfile e scripts de bootstrap.

10. **Infraestrutura como Código**: Arquivo `infra.yml` para gerenciamento de configurações de infraestrutura por ambiente.