# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-solicita-consulta-cip** é um microsserviço REST desenvolvido em Spring Boot que realiza a solicitação de consulta de boletos de pagamento na CIP (Câmara Interbancária de Pagamentos). 

O componente verifica se a consulta na CIP deve ser realizada com base em parâmetros configuráveis (contingência, valor do pagamento, configuração do cliente) e, quando aplicável, executa a consulta integrando-se com outro serviço REST (consulta-boleto). O resultado da consulta é incorporado ao dicionário de pagamento e retornado ao solicitante.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot |
| **SolicitaConsultaCipAPI.java** | Controller REST que expõe o endpoint `/v1/atacado/pagamentos/solicitaConsultaCip` |
| **SolicitaConsultaCipService.java** | Serviço de negócio que orquestra a lógica de verificação e execução da consulta CIP |
| **ConsultaCipRestRepository.java** | Repositório responsável por integrar com o serviço REST de consulta de boleto e converter a resposta |
| **DbSpagRepository.java** | Repositório de acesso ao banco de dados SPAG para buscar parâmetros de configuração |
| **AppConfiguration.java** | Configuração do RestTemplate para chamadas ao serviço de consulta boleto |
| **AppProperties.java** | Propriedades de configuração da API de consulta boleto (host, credenciais, timeout) |
| **DocketConfiguration.java** | Configuração do Swagger para documentação da API |
| **ParametroInterfaceCip.java** | Entidade que representa os parâmetros gerais da interface CIP |
| **ParametroValidacaoCipCliente.java** | Entidade que representa os parâmetros de validação CIP específicos por cliente |
| **SolicitaConsultaCipRequest/Response** | DTOs de requisição e resposta do serviço |
| **Utils.java** | Classe utilitária com métodos auxiliares (conversão de data, tratamento de ocorrências, etc) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.0.0.RELEASE** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring JDBC** - Para acesso a banco de dados
- **Springfox Swagger 2.8.0** - Documentação de API
- **Microsoft SQL Server JDBC Driver 7.0.0** - Driver de banco de dados
- **Lombok 1.16.20** - Redução de código boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Gradle** - Ferramenta de build
- **JUnit e Mockito** - Testes unitários
- **JaCoCo** - Cobertura de testes
- **SonarQube** - Análise de qualidade de código
- **Docker** - Containerização (AdoptOpenJDK 8 com OpenJ9)
- **Bibliotecas internas Votorantim:**
  - springboot-arqt-base-trilha-auditoria-web (1.1.4)
  - springboot-arqt-base-security-basic (1.2.0)
  - springboot-arqt-base-lib-database (0.2.2)
  - java-spag-base-pagamentos-commons (0.9.0)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/atacado/pagamentos/solicitaConsultaCip` | SolicitaConsultaCipAPI | Recebe um DicionarioPagamento, verifica se deve consultar a CIP e executa a consulta quando aplicável, retornando o dicionário enriquecido com os dados da CIP |

---

## 5. Principais Regras de Negócio

1. **Verificação de Elegibilidade para Consulta CIP:**
   - Apenas pagamentos de boleto (código de liquidação ITP = 22) são elegíveis
   - Pagamentos pré-confirmados não são consultados na CIP

2. **Contingência CIP:**
   - Se a CIP estiver em contingência (flag `FlRecebimentoContingenciaCIP = 'S'`), apenas pagamentos dentro do range de valores parametrizado (`VrMinimoAutorizacaoCIP` e `VrMaximoAutorizacaoCIP`) são aceitos
   - Pagamentos fora do range geram ocorrência de erro

3. **Parametrização por Cliente:**
   - Clientes podem ter configuração específica para não realizar consulta CIP (`FlValidacaoCip = 'N'`)
   - Neste caso, apenas pagamentos com valor menor que o mínimo definido (`VrMinimoValidacaoCip`) não são consultados

4. **Retry de Consulta:**
   - Em caso de falha na chamada do serviço de consulta CIP, o sistema tenta novamente até 3 vezes
   - Após 3 tentativas sem sucesso, gera ocorrência de erro

5. **Tratamento de Resposta:**
   - A resposta da CIP é convertida para o formato interno (BoletoPagamentoCompletoDTO)
   - Erros na conversão geram ocorrência específica

6. **Indicadores de Retorno:**
   - Campo `consultaCIP` indica o status: "S" (sim), "N" (não), "C" (contingência)
   - Campo `flRetornoConsultaCIP` indica se houve erro na consulta

---

## 6. Relação entre Entidades

**Entidades principais:**

- **DicionarioPagamento**: Entidade central que trafega por todo o fluxo, contendo todas as informações do pagamento
  - Contém: BoletoPagamentoCompletoDTO (dados da consulta CIP)
  - Contém: ListaOcorrencia (erros/avisos do processamento)

- **ParametroInterfaceCip**: Parâmetros gerais da interface CIP (contingência, valores mínimo/máximo)

- **ParametroValidacaoCipCliente**: Parâmetros específicos por cliente (CPF/CNPJ)

- **BoletoPagamentoCompletoDTO**: Dados completos do boleto retornados pela CIP
  - Contém: ListaBaixaEfetiva, ListaBaixaOperacional, ListaCalculoTitulo, ListaDescontoTitulo, ListaJurosTitulo, ListaMultaTitulo
  - Contém: PessoaBeneficiarioOriginalDTO

**Relacionamentos:**
- DicionarioPagamento (1) -> (0..1) BoletoPagamentoCompletoDTO
- DicionarioPagamento (1) -> (0..1) ListaOcorrencia
- ParametroValidacaoCipCliente (N) -> (1) Cliente (por CPF/CNPJ)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroInterfaceCIP | Tabela | SELECT | Busca os parâmetros gerais da interface CIP (contingência, valores mínimo/máximo de autorização) |
| TbParametroValidacaoCipCliente | Tabela | SELECT | Busca os parâmetros de validação CIP específicos de um cliente pelo CPF/CNPJ |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Arquivo de configuração de logs (montado via ConfigMap no Kubernetes) |
| dbspagrepository-sql.xml | Leitura | DbSpagRepository | Arquivo XML contendo as queries SQL para acesso ao banco SPAG |
| springboot-spag-base-consulta-boleto.yaml | Leitura | Swagger Client | Especificação OpenAPI do serviço de consulta boleto integrado |

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
| **springboot-spag-base-consulta-boleto** | REST API | Serviço REST que realiza a consulta efetiva do boleto na CIP. Autenticação via Basic Auth. Endpoint: `GET /{codigoBarra}` |
| **Banco de Dados SPAG (SQL Server)** | JDBC | Banco de dados corporativo contendo parâmetros de configuração da CIP e validações por cliente |
| **LDAP BVNet** | LDAP | Serviço de autenticação e autorização (integrado via biblioteca springboot-arqt-base-security) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades (controller, service, repository)
- Uso adequado de injeção de dependências
- Tratamento de exceções estruturado com retry e ocorrências
- Uso de Lombok para reduzir boilerplate
- Configuração externalizada (application.yml)
- Documentação Swagger configurada
- Testes unitários presentes
- Uso de bibliotecas corporativas padronizadas

**Pontos de Melhoria:**
- Classe `ConsultaCipRestRepository` muito extensa (mais de 400 linhas) com múltiplas responsabilidades (chamada REST + conversão complexa)
- Métodos de conversão muito longos e repetitivos, poderiam ser refatorados
- Falta de tratamento específico para alguns cenários de erro
- Comentários em português misturados com código em inglês
- Alguns nomes de variáveis poderiam ser mais descritivos
- Falta de validação de entrada em alguns pontos
- Uso de `new Integer()` ao invés de `Integer.valueOf()` (deprecated)
- Alguns blocos catch vazios (ex: `catch (EmptyResultDataAccessException em) { ; }`)
- Falta de logs estruturados em alguns pontos críticos

---

## 14. Observações Relevantes

1. **Ambientes:** O sistema está preparado para rodar em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas via profiles Spring

2. **Segurança:** Utiliza autenticação Basic Auth e integração com LDAP corporativo. Em ambiente local, possui usuários in-memory para testes

3. **Infraestrutura:** Preparado para deploy em OpenShift/Kubernetes com ConfigMaps, Secrets e probes de liveness/readiness configurados

4. **Monitoramento:** Integrado com trilha de auditoria corporativa (springboot-arqt-base-trilha-auditoria-web)

5. **Timeout:** Configurado timeout de 30 segundos para chamadas ao serviço de consulta boleto

6. **Versionamento:** API versionada (v1) no path do endpoint

7. **Biblioteca Comum:** Utiliza biblioteca compartilhada `java-spag-base-pagamentos-commons` que define estruturas de dados comuns (DicionarioPagamento, DTOs, Enums)

8. **Pipeline CI/CD:** Configurado para build automatizado via Jenkins (jenkins.properties) com deploy em plataforma Google Cloud

9. **Qualidade:** Integrado com SonarQube e JaCoCo para análise de qualidade e cobertura de código

10. **Contingência:** Sistema preparado para operar em modo de contingência da CIP com regras específicas de validação de valores