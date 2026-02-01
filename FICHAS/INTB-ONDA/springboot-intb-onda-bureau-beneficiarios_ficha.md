# Ficha Técnica do Sistema

---

## 1. Descrição Geral

O sistema **springboot-intb-onda-bureau-beneficiarios** é uma API REST desenvolvida em Spring Boot que tem como objetivo consultar informações de sócios de empresas através de integração com o serviço de Bureau de Crédito (Serasa). O sistema realiza consultas recursivas para obter a estrutura societária completa de uma empresa a partir de seu CNPJ, navegando pela hierarquia de participações societárias e armazenando os dados consultados em um banco de dados Sybase. A aplicação também oferece um endpoint de exemplo (Hello World) para fins de referência.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server.java** | Classe principal que inicializa a aplicação Spring Boot |
| **ObterSociosService.java** | Serviço principal que orquestra a consulta recursiva de sócios, controlando o limite de consultas e a navegação pela hierarquia societária |
| **HelloService.java** | Serviço de exemplo que retorna uma mensagem de saudação |
| **BureauCreditoRepository.java** | Repositório responsável por realizar chamadas ao serviço SOAP de Bureau de Crédito (Serasa) |
| **SocioRepository.java** | Repositório que consulta dados de sócios no banco de dados Sybase (tabela TbSerasaPjCTSocietarioDetalhe) |
| **ObterSociosApi.java** | Controller REST que expõe o endpoint POST /obterSocios |
| **HelloApi.java** | Controller REST de exemplo que expõe o endpoint GET /hello |
| **DetalhesSocio.java** | Entidade de domínio que representa os dados de um sócio |
| **ConsultaSocios.java** | Objeto de domínio que controla o estado da consulta recursiva (quantidade de consultas e resultados) |
| **ValidaCNPJ.java** | Utilitário para validação de CNPJ |
| **Sanitizador.java** | Utilitário para sanitização de inputs (logs seguros) |
| **DetalhesSocioRowMapper.java** | Mapper JDBC para conversão de ResultSet em objetos DetalhesSocio |
| **DocketConfiguration.java** | Configuração do Swagger/OpenAPI |
| **WebServiceTemplateConfiguration.java** | Configuração do cliente SOAP (WebServiceTemplate) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework principal)
- **Spring Web** (REST APIs)
- **Spring Web Services** (cliente SOAP)
- **Spring Security** (autenticação básica e LDAP)
- **Spring JDBC** (acesso a banco de dados)
- **Sybase jConnect 4** (driver JDBC para Sybase)
- **Swagger/Springfox 3.0.0** (documentação de API)
- **Micrometer + Prometheus** (métricas)
- **Spring Actuator** (health checks e monitoramento)
- **Apache CXF** (geração de código a partir de WSDL)
- **JUnit 5 + Mockito** (testes unitários)
- **JMeter** (testes funcionais)
- **Docker** (containerização)
- **Maven** (gerenciamento de dependências)
- **Logback** (logging em formato JSON)
- **Bibliotecas BV**: springboot-arqt-base-trilha-auditoria-web, springboot-arqt-base-security-basic, sbootlib-arqt-base-tracing

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /hello | HelloApi | Endpoint de exemplo que retorna uma mensagem de saudação personalizada |
| POST | /obterSocios | ObterSociosApi | Endpoint principal que recebe um CNPJ e retorna a estrutura completa de sócios da empresa |

---

## 5. Principais Regras de Negócio

1. **Consulta Recursiva de Sócios**: O sistema realiza consultas recursivas para obter toda a cadeia societária de uma empresa, navegando pelos CNPJs dos sócios que são pessoas jurídicas.

2. **Limite de Consultas**: Existe um limite configurável (padrão: 500 consultas) para evitar loops infinitos ou consultas excessivas na estrutura societária.

3. **Complementação de CNPJ**: Como o bureau não armazena a parte matriz/filial do CNPJ (4 dígitos), o sistema tenta todas as combinações de 0001 a 9999 até encontrar um CNPJ válido.

4. **Carência de Consulta**: Existe um período de carência configurável (padrão: 30 dias) para reutilização de consultas anteriores no bureau.

5. **Validação de CNPJ**: O sistema valida CNPJs antes de processá-los, incluindo verificação de dígitos verificadores.

6. **Sanitização de Logs**: Todos os dados sensíveis são sanitizados antes de serem registrados em logs.

7. **Controle de Consultas Duplicadas**: O sistema verifica se um CNPJ já foi consultado na mesma execução para evitar consultas redundantes.

8. **Hierarquia de Empresas**: O sistema mantém o relacionamento entre empresa pai e empresa antecessora na estrutura societária.

---

## 6. Relação entre Entidades

**DetalhesSocio**: Entidade principal que representa um sócio de uma empresa
- Atributos: nuCnpj, dtConsulta, tpPessoaSocio, nuDocumentoSocio, dvDocumentoSocio, nmSocio, dsNacionalidadeSocio, pcCapitalSocio, dtEntradaSocio, flRestricaoSocio, pcCapitalVolanteSocio, stSocio, nuSeq, nuCnpjEmpresaPai

**ConsultaSocios**: Objeto de controle da consulta recursiva
- Atributos: qtdConsultas (contador), resultadoSocios (Set<DetalhesSocio>)
- Relacionamento: Contém múltiplos DetalhesSocio

**Representations (DTOs)**:
- ObterSociosRequestRepresentation: numeroDocumento
- ObterSociosResponseRepresentation: listaSocios (List<SocioRepresentation>)
- SocioRepresentation: numeroDocumentoSocio, numeroDocumentoEmpresa, nomeSocio, percentualParticipacao, tipoPessoa, isListadoBolsa, nuDocumentoEmpresaAntecessora

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| DBCONSULTACRED..TbSerasaPjCTSocietarioDetalhe | Tabela | SELECT | Tabela que armazena os detalhes dos sócios consultados no bureau Serasa |
| DBCONSULTACRED..TbConsulta | Tabela | SELECT | Tabela que armazena informações sobre as consultas realizadas ao bureau (usada para obter a data da última consulta) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | leitura | /usr/etc/log/ (runtime) | Arquivo de configuração de logs em formato JSON |
| application.yml | leitura | src/main/resources | Arquivo de configuração principal da aplicação |
| application-local.yml | leitura | src/main/resources | Arquivo de configuração para ambiente local |
| CreditoBureauBackendService_v2.wsdl | leitura | src/main/resources/wsdl | WSDL do serviço de Bureau de Crédito |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

1. **Serviço SOAP de Bureau de Crédito (Serasa)**: 
   - Endpoint: ${SERVICEBUS_HOST}/services/CreditoBureauBackendServiceV2
   - Operação: consultarRestricoesBureau
   - Descrição: Serviço externo que realiza consultas de crédito e informações societárias no bureau Serasa
   - Classe responsável: BureauCreditoRepository

2. **Banco de Dados Sybase (DBCONSULTACRED)**:
   - Host: Variável por ambiente (DES/QA/UAT/PRD)
   - Descrição: Banco de dados que armazena os resultados das consultas ao bureau
   - Classe responsável: SocioRepository

3. **LDAP (Autenticação)**:
   - Descrição: Serviço de autenticação corporativa via LDAP
   - Configuração: WebServiceTemplateConfiguration, application.yml

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (controller, service, repository)
- Uso adequado de injeção de dependências
- Implementação de testes unitários
- Configuração adequada de segurança e auditoria
- Uso de DTOs (Representations) para separar modelo de domínio da API
- Sanitização de logs para segurança
- Documentação via Swagger

**Pontos de Melhoria:**
- Lógica complexa de consulta recursiva no ObterSociosService poderia ser refatorada em métodos menores
- Método `complementarNuCpnj` realiza até 9999 iterações, o que pode impactar performance
- Falta de tratamento de exceções mais específico em alguns pontos
- Alguns métodos muito longos (ex: `consultarSocios` com múltiplas responsabilidades)
- Falta de validação mais robusta de entrada de dados
- Comentários em português misturados com código em inglês
- Uso de `@Autowired` em construtores poderia ser substituído por injeção via construtor sem anotação (Spring 4.3+)
- Falta de testes de integração implementados (diretório vazio)

---

## 14. Observações Relevantes

1. **Limite de Consultas**: O sistema possui um limite configurável de 500 consultas para evitar loops infinitos na estrutura societária. Este valor pode precisar de ajuste dependendo da complexidade das estruturas empresariais consultadas.

2. **Complementação de CNPJ**: A lógica de complementação de CNPJ (método `complementarNuCpnj`) pode ser custosa em termos de performance, pois tenta até 9999 combinações. Considerar otimizações ou cache.

3. **Ambientes**: O sistema está configurado para 4 ambientes (DES, QA, UAT, PRD) com configurações específicas de banco de dados e URLs de serviço.

4. **Segurança**: Implementa autenticação básica e LDAP, com endpoints públicos configuráveis.

5. **Monitoramento**: Integração completa com Prometheus/Grafana para métricas e monitoramento.

6. **Containerização**: Dockerfile configurado para deploy em ambiente Google Cloud Platform (GCP).

7. **Versionamento**: O projeto está na versão 0.17.0, indicando que ainda está em desenvolvimento ativo.

8. **Dependências Corporativas**: Utiliza extensivamente bibliotecas internas do Banco Votorantim (arqt-base-*).