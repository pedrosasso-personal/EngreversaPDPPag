# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-saca-scco-atom-informacoes-contratos** é uma API REST desenvolvida em Spring Boot que fornece informações sobre contratos financeiros, especificamente consultando a situação atual de contratos. O serviço consulta dados de um banco de dados Sybase (SCC_FIN) e retorna informações sobre o status/situação de contratos identificados por número de contrato de gestão. O sistema segue a arquitetura de microserviços atômicos do padrão Atlante do Banco Votorantim.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal de inicialização da aplicação Spring Boot |
| **InformacoesContratosApiDelegateImpl** | Implementação do delegate da API REST, recebe requisições HTTP e delega ao serviço |
| **InformacoesContratosService** | Camada de serviço contendo lógica de negócio para consulta de situação de contratos |
| **InformacoesContratosRepository** | Interface JPA para acesso aos dados de situação de contratos no banco Sybase |
| **InformacoesContratosMapper** | Interface MapStruct para conversão entre entidades de domínio e representações REST |
| **SituacaoContrato** | Entidade JPA representando a situação de um contrato |
| **Situacao** | Entidade JPA representando os tipos de situação possíveis |
| **InformacoesContratosConfiguration** | Classe de configuração Spring para criação de beans |
| **BusinessActionConfiguration** | Configuração para trilha de auditoria |
| **ExceptionHandler** | Tratamento centralizado de exceções da aplicação |
| **InputVariableException** | Exceção customizada para validação de entrada |
| **ValidationClass** | Classe utilitária para validações de entrada |
| **DefinidorBusinessActionCustom** | Implementação customizada para definição de ações de negócio na auditoria |

---

## 3. Tecnologias Utilizadas

- **Java 21** (JDK 21)
- **Spring Boot 3.x** (baseado no parent pom-atle-base-sboot-atom-parent 3.1.2)
- **Spring Data JPA** (para acesso a dados)
- **Spring Security OAuth2** (autenticação JWT)
- **Hibernate** (ORM)
- **Sybase jConnect 4** (driver JDBC versão 7.07-ESD-5)
- **MapStruct** (mapeamento de objetos)
- **Lombok** (redução de boilerplate)
- **Maven 3.9** (gerenciamento de dependências)
- **OpenAPI 3.0** (documentação de API)
- **Swagger UI** (interface de documentação)
- **Docker** (containerização)
- **Google Cloud Platform** (plataforma de deploy)
- **Actuator** (monitoramento e health checks)
- **Logback** (logging)
- **Atlante Base** (framework interno Banco Votorantim)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /informacoes-contratos/{contrato} | InformacoesContratosApiDelegateImpl | Consulta a situação de um contrato específico pelo número do contrato de gestão |

---

## 5. Principais Regras de Negócio

1. **Validação de Número de Contrato**: O número do contrato não pode ser maior ou igual a 100.000.000.000.000 (100 trilhões). Caso contrário, retorna erro 400 com mensagem "Número do contrato maior que o permitido".

2. **Consulta de Situação**: O sistema busca a situação mais recente do contrato ordenando por data de última alteração (DT_ULT_ALT) em ordem decrescente.

3. **Mapeamento de Situações**: O sistema retorna códigos de situação que representam diferentes estados do contrato:
   - 0: RETIRAR SITUAÇÃO
   - 1: DESLOCALIZADO
   - 2: FALECIDO
   - 3: SUSPEITA DE FRAUDE
   - 4: FRAUDE COMPROVADA
   - 5: TERCEIRO
   - 6: LOJISTA
   - 7: CÁLCULO
   - 8: DESEMPREGADO
   - 9: VEÍCULO FURTADO SEM SEGURO
   - 10: GRAVAME BLOQUEADO PARA BAIXA
   - 11: FRAUDE/GRAVAME BLOQUEADO
   - 12: PORTABILIDADE
   - 13: DECLARAÇÃO ANUAL DE DÉBITOS
   - 14: PROCURADOR
   - 15: ALERTA

4. **Autenticação e Autorização**: Todas as requisições devem conter token JWT válido (Bearer Token) para autenticação.

5. **Auditoria**: O sistema registra ações de negócio através da trilha de auditoria Atlante, identificando operações GET como "BA: GET situacao contrato".

---

## 6. Relação entre Entidades

**SituacaoContrato** (Entidade Principal)
- Atributos: cdContrato, cdUsuario, dtUltAlt, nuContratoGestao (PK), sqContratoFinanceiro
- Relacionamento: ManyToOne com **Situacao** (através de cdSituacao)

**Situacao** (Entidade de Referência)
- Atributos: cdSituacao (PK), dsSituacao, cdUsuario, dtUltAlt
- Relacionamento: OneToMany com **SituacaoContrato**

**Relacionamento**: Um contrato possui uma situação, e uma situação pode estar associada a múltiplos contratos. A relação é estabelecida através do campo CD_SITUACAO.

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_SITUACAO_CONTRATO | Tabela | SELECT | Tabela principal contendo as situações dos contratos com informações de contrato, usuário e data de alteração |
| TB_SITUACAO | Tabela | SELECT | Tabela de referência contendo os tipos de situação possíveis com código e descrição |

**Banco de Dados**: Sybase ASE (SCC_FIN)

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| openapi.yaml | Leitura | src/main/resources/swagger/ | Contract-first da API REST, define endpoints e schemas |
| application.yml | Leitura | src/main/resources/ | Configurações da aplicação para todos os ambientes |
| application-local.yml | Leitura | src/main/resources/ | Configurações específicas para ambiente local |
| logback-spring.xml | Leitura | /usr/etc/log (runtime) | Configuração de logs para ambientes des/uat/prd |
| infra.yml | Leitura | infra-as-code/ | Configurações de infraestrutura como código para deploy |

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
| **Sybase ASE (SCC_FIN)** | Banco de Dados | Banco de dados principal contendo informações de contratos financeiros. Conexões diferentes por ambiente (des: ptasybdes15.bvnet.bv:6010, uat: ptasybuatfin.bvnet.bv:5050, prd: sybfin_4999_5000.bvnet.bv:5000) |
| **API Gateway BV** | Autenticação | Serviço de autenticação OAuth2/JWT para validação de tokens. URLs variam por ambiente (des: apigatewaydes.bvnet.bv, uat: apigatewayuat.bvnet.bv, prd: apigateway.bvnet.bv) |
| **JWKS Endpoint** | Autenticação | Endpoint para obtenção de chaves públicas JWT (/openid/connect/jwks.json) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada seguindo padrão de camadas (REST → Service → Repository)
- Uso adequado de padrões como MapStruct para mapeamento e Lombok para redução de boilerplate
- Separação clara de responsabilidades entre classes
- Configuração adequada de profiles para diferentes ambientes
- Documentação OpenAPI bem estruturada
- Uso de boas práticas Spring Boot (configuração via beans, injeção de dependências)
- Tratamento de exceções centralizado
- Validações de entrada implementadas

**Pontos de Melhoria:**
- A query nativa no repositório poderia ser substituída por JPQL ou Criteria API para maior portabilidade
- Falta de testes unitários incluídos na análise (embora existam na estrutura)
- A classe ValidationClass possui apenas um método estático e poderia ser melhor estruturada
- Constante MAX_VALUE poderia estar em arquivo de configuração
- Falta de paginação na consulta (embora retorne apenas um registro)
- Documentação inline (JavaDoc) limitada em algumas classes
- O ExceptionHandler trata apenas InputVariableException, poderia ter tratamento mais abrangente

O código demonstra maturidade e segue boas práticas de desenvolvimento, com estrutura clara e manutenível.

---

## 14. Observações Relevantes

1. **Padrão Atlante**: O projeto segue o padrão de microserviços atômicos do framework Atlante do Banco Votorantim, incluindo trilha de auditoria e configurações específicas.

2. **Charset Específico**: A conexão com o banco Sybase utiliza charset cp1252, importante para manutenção da integridade dos dados.

3. **Portas Segregadas**: A aplicação utiliza porta 8080 para API e porta 9090 para endpoints de gerenciamento (Actuator), seguindo boas práticas de segregação.

4. **Segurança**: Endpoints públicos são limitados apenas a documentação Swagger e console H2 (apenas em local). Todos os endpoints de negócio requerem autenticação JWT.

5. **Multi-layer Docker**: O Dockerfile utiliza estratégia de múltiplas camadas para otimização de build e cache de dependências.

6. **Ambientes**: O sistema está preparado para 3 ambientes: desenvolvimento (des), homologação (uat) e produção (prd), com configurações específicas para cada um.

7. **Health Checks**: Configurados probes de liveness e readiness com timeouts e delays apropriados para ambiente Kubernetes/OpenShift.

8. **Versionamento**: API versionada (v1) com possibilidade de evolução sem quebra de contratos.

9. **Observabilidade**: Integração com Prometheus para métricas e endpoints de health detalhados.

10. **Deploy**: Preparado para deploy em Google Cloud Platform (GCP) conforme configuração do jenkins.properties.