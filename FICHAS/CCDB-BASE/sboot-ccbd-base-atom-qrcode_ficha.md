# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-atom-qrcode** é um serviço atômico (microserviço) desenvolvido em Java com Spring Boot, responsável por gerar códigos QR (QRCode) a partir de um texto fornecido. O sistema recebe uma requisição contendo o texto a ser codificado, dimensões da imagem e tipo de formato (PNG ou JPG), e retorna a imagem do QRCode codificada em Base64. Trata-se de um componente reutilizável dentro da arquitetura do Banco Votorantim, seguindo padrões de microserviços atômicos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal que inicializa a aplicação Spring Boot com segurança OAuth2 habilitada |
| `QrcodeController` | Controlador REST que expõe o endpoint para geração de QRCode |
| `QrcodeService` / `QrCodeServiceImpl` | Interface e implementação da lógica de negócio para geração de QRCode utilizando a biblioteca ZXing |
| `QrcodeMapper` | Classe utilitária para conversão entre objetos de representação (API) e objetos de domínio |
| `QrcodeConfiguration` | Configuração Spring para instanciar o bean do serviço de QRCode |
| `OpenApiConfiguration` | Configuração do Swagger/OpenAPI para documentação da API |
| `ResourceExceptionHandler` | Tratador global de exceções para padronizar respostas de erro |
| `QrcodeRequest` | Objeto de domínio representando a requisição de geração de QRCode |
| `QrCodeResponse` | Objeto de domínio representando a resposta com a imagem gerada |
| `QrCodeDimensao` | Objeto de domínio representando as dimensões (altura e largura) do QRCode |
| `TipoImagemEnum` | Enumeração que define os tipos de imagem suportados (PNG, JPG) |
| `QrcodeException` | Exceção customizada para erros na geração de QRCode |

---

## 3. Tecnologias Utilizadas

- **Java 11** (OpenJDK)
- **Spring Boot 2.x** (framework principal)
- **Spring Web** (para criação de APIs REST)
- **Spring Security OAuth2** (autenticação e autorização via JWT)
- **Spring Actuator** (monitoramento e métricas)
- **Micrometer + Prometheus** (coleta de métricas)
- **Swagger/Springfox 2.9.2** (documentação de API)
- **ZXing (Google)** (biblioteca para geração de QRCode)
- **Lombok** (redução de código boilerplate)
- **Maven** (gerenciamento de dependências e build)
- **Docker** (containerização)
- **JUnit 5** (testes unitários)
- **Mockito** (mocks para testes)
- **Rest Assured** (testes funcionais)
- **Pact** (testes de contrato)
- **Grafana + Prometheus** (observabilidade)
- **Logback** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/banco-digital/qrcode` | `QrcodeController` | Gera um QRCode a partir de um texto, retornando a imagem em Base64 |

**Observação:** O endpoint requer autenticação via Bearer Token (OAuth2/JWT).

---

## 5. Principais Regras de Negócio

1. **Validação de Tipo de Imagem**: O sistema aceita apenas os formatos PNG e JPG. Caso um formato não suportado seja informado, uma exceção `IllegalArgumentException` é lançada.

2. **Geração de QRCode**: Utiliza a biblioteca ZXing para codificar o texto fornecido em uma matriz de bits (BitMatrix) e converte para imagem no formato especificado.

3. **Codificação Base64**: A imagem gerada é convertida para Base64 antes de ser retornada ao cliente, facilitando o transporte via JSON.

4. **Tratamento de Erros**: Erros durante a geração do QRCode (IOException, WriterException) são capturados e convertidos em `QrcodeException`, que é tratada globalmente retornando HTTP 422 (Unprocessable Entity).

5. **Dimensões Customizáveis**: O cliente pode especificar altura e largura da imagem QRCode gerada.

---

## 6. Relação entre Entidades

O sistema possui uma estrutura de domínio simples:

- **QrcodeRequest**: Contém `texto` (String), `dimensao` (QrCodeDimensao) e `tipoImagem` (TipoImagemEnum)
- **QrCodeDimensao**: Contém `altura` (Integer) e `largura` (Integer)
- **QrCodeResponse**: Contém `imagem` (String em Base64)
- **TipoImagemEnum**: Enumeração com valores PNG e JPG

**Relacionamento:**
- `QrcodeRequest` **possui** `QrCodeDimensao` (composição)
- `QrcodeRequest` **referencia** `TipoImagemEnum` (associação)

Não há entidades persistidas em banco de dados; o sistema é stateless.

---

## 7. Estruturas de Banco de Dados Lidas

Não se aplica.

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `application.yml` | Leitura | Spring Boot (startup) | Arquivo de configuração da aplicação (porta, profiles, segurança, etc.) |
| `logback-spring.xml` | Leitura | Logback (logging) | Configuração de logs (formato JSON, níveis, appenders) |
| `sboot-ccbd-base-atom-qrcode.yaml` | Leitura | Swagger Codegen (build time) | Especificação OpenAPI para geração de interfaces e representações |
| Logs (console/arquivo) | Gravação | Logback | Logs da aplicação em formato JSON |

---

## 10. Filas Lidas

Não se aplica.

---

## 11. Filas Geradas

Não se aplica.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| Servidor OAuth2/JWT | API Externa | Validação de tokens JWT através do endpoint `jwks.json` configurado (ex: `https://api-digitaluat.bancovotorantim.com.br/openid/connect/jwks.json`) |
| Prometheus | Exportação de Métricas | Exposição de métricas no endpoint `/actuator/prometheus` para coleta pelo Prometheus |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Código bem organizado seguindo arquitetura em camadas (application, domain, common)
- Uso adequado de padrões como Mapper, Service, Controller
- Separação clara de responsabilidades
- Uso de Lombok reduzindo boilerplate
- Tratamento centralizado de exceções
- Testes unitários, de integração e funcionais estruturados
- Documentação via Swagger/OpenAPI
- Configuração de observabilidade (Prometheus, Grafana)
- Uso de imutabilidade com builders e final nos objetos de domínio

**Pontos de Melhoria:**
- Falta de validação de entrada mais robusta (ex: Bean Validation com @Valid)
- Ausência de logs estruturados em alguns pontos críticos
- Testes de cobertura poderiam ser mais abrangentes (alguns testes estão vazios ou incompletos)
- Documentação inline (JavaDoc) poderia ser mais detalhada
- Configuração de segurança poderia ser mais explícita e documentada

O código demonstra boas práticas de desenvolvimento, mas há espaço para melhorias em validações, testes e documentação.

---

## 14. Observações Relevantes

1. **Arquitetura Atômica**: O projeto segue o padrão de microserviços atômicos do Banco Votorantim, sendo um componente reutilizável e independente.

2. **Segurança**: A aplicação utiliza OAuth2 Resource Server com validação de JWT, garantindo que apenas requisições autenticadas possam acessar os endpoints.

3. **Observabilidade**: Infraestrutura completa de métricas com Prometheus e Grafana, incluindo dashboards pré-configurados para monitoramento de JVM, HTTP, HikariCP, etc.

4. **Multi-ambiente**: Suporte a múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles do Spring.

5. **Containerização**: Dockerfile otimizado utilizando OpenJ9 (JVM com menor footprint de memória).

6. **Pipeline CI/CD**: Configuração para Jenkins com propriedades específicas (`jenkins.properties`) e infraestrutura como código (`infra.yml`).

7. **Testes**: Estrutura completa de testes (unitários, integração, funcionais, contrato via Pact), embora alguns estejam incompletos.

8. **Dependências Corporativas**: Utiliza bibliotecas internas do Banco Votorantim (arqt-base) para padronização de erros, segurança e auditoria.

9. **Versão**: Projeto na versão 0.1.0, indicando fase inicial/MVP.

10. **Tecnologia Base**: Gerado via scaffolding plugin do BV (`br.com.votorantim.arqt:scaffolding-plugin:0.51.7`), garantindo conformidade com padrões corporativos.