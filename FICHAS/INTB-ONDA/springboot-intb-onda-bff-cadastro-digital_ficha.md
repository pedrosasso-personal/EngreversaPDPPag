# Ficha Técnica do Sistema

## 1. Descrição Geral

O **springboot-intb-onda-bff-cadastro-digital** é um BFF (Backend for Frontend) desenvolvido em Spring Boot para orquestrar o processo de cadastro digital de prospects (clientes em potencial) pessoa física e jurídica. O sistema atua como camada intermediária entre o frontend de onboarding e os serviços backend corporativos (ServiceBus), centralizando chamadas a múltiplos endpoints de dados mestres, validações, compliance e persistência de cadastros. Principais funcionalidades incluem: consulta de dados mestres (bancos, cidades, profissões, etc), validação de CEP, geração de hash de acesso, validação de prospects, inclusão de cadastros completos, geração de PDF de contrato via JasperReports, envio de emails, e controle de fluxo de navegação entre telas de cadastro.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Server** | Classe main do Spring Boot, inicializa aplicação e habilita Swagger |
| **BrokerConnector** | Classe base para integração REST com ServiceBus, trata erros HTTP (401, 404, timeout), implementa autenticação básica |
| **BrokerConfiguration** | Configuração de propriedades do broker (URL, usuário, senha) |
| **DocumentoService** | Gera PDF de contrato de cadastro PF/PJ usando JasperReports, classifica tipo investidor (qualificado/profissional) |
| **ProspectService** | Consulta dados de prospect e relacionamento via broker, enriquece com descrições de estado civil e países NIF |
| **IncluirCadastroDigitalService** | Inclui cadastro completo de prospect no backend via broker |
| **ValidarHashService** | Valida hash de acesso para controle de autenticação/autorização |
| **GerarHashAcessoService** | Gera hash de acesso para onboarding |
| **ObterEnderecoCepService** | Consulta endereço por CEP, valida formato e cruza cidade retornada com lista global |
| **EmailService** | Envia email com link de cadastro via broker |
| **AtividadeEconomicaService, BancoService, CargoService, CidadeService, etc** | Serviços para listar dados mestres (combos) via broker |
| **IncluirCadastroDigitalProspectApi** | Controller REST principal para inclusão de cadastro |
| **ConsultarRelacionamentoApi** | Controller REST para consulta de relacionamento de prospect |
| **DocumentoApi** | Controller REST para geração de PDF de contrato |
| **IncluirCadastroProspectRequestRepresentation** | DTO complexo (55kb) com todos os dados de cadastro PF/PJ |
| **ObterDadosProspectResponseRepresentation** | DTO complexo com resposta completa de dados de prospect |

---

## 3. Tecnologias Utilizadas

- **Java 8** (OpenJDK 8)
- **Spring Boot 2.0**
- **Gradle** (build)
- **RestTemplate** (cliente HTTP para integração com ServiceBus)
- **JasperReports** (geração de PDF de contratos)
- **Swagger 2** (documentação de API)
- **Jackson** (serialização JSON)
- **Lombok** (redução de boilerplate)
- **Bean Validation (javax.validation)** (validações de entrada)
- **Logback** (logging)
- **LDAP** (autenticação em ambientes des+)
- **Spring Security** (autenticação básica)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /incluirCadastroProspect | IncluirCadastroDigitalProspectApi | Inclui cadastro completo de prospect PF/PJ |
| POST | /V1/consultarRelacionamento | ConsultarRelacionamentoApi | Consulta relacionamento de prospect |
| GET | /documento/contrato/{nrDocumento} | DocumentoApi | Gera e retorna PDF de contrato de cadastro |
| POST | /gerarHashAcesso | GerarHashAcessoApi | Gera hash de acesso para onboarding |
| POST | /validarHashAcesso | ValidarHashApi | Valida hash de acesso |
| POST | /enviarLink | EmailApi | Envia email com link de cadastro |
| GET | /listarAtividadeEconomica | ListarAtividadeEconomicaApi | Lista atividades econômicas |
| GET | /listarBanco | ListarBancoApi | Lista bancos |
| GET | /listarCargo | ListarCargoApi | Lista cargos |
| POST | /listarCidade | ListarCidadeApi | Lista cidades por estado/país |
| GET | /listarEstadoCivil | ListarEstadoCivilApi | Lista estados civis |
| GET | /listarNaturezaJuridica | ListarNaturezaJuridicaApi | Lista naturezas jurídicas |
| GET | /listarOcupacaoProfissional | ListarOcupacaoProfissionalApi | Lista ocupações profissionais |
| GET | /listarPais | ListarPaisApi | Lista países |
| POST | /listarTipoPatrimonio/{codigo} | ListarPatrimonioApi | Lista tipos de patrimônio por grupo |
| GET | /listarProfissao | ListarProfissaoApi | Lista profissões |
| POST | /listarTipoDocumento/{codigo} | ListarTipoDocumentoApi | Lista tipos de documento por grupo |
| POST | /obterEnderecoCep | ObterEnderecoCEPApi | Obtém endereço por CEP |
| POST | /obterPessoa | ObterPessoaApi | Obtém dados de pessoa |
| POST | /obterTermos | ObterTermoApi | Obtém termos contratuais |
| POST | /validarProspect | ValidarProspectApi | Valida prospect (mock) |
| GET | /hello | HelloApi | Endpoint de exemplo/teste |

---

## 5. Principais Regras de Negócio

1. **Classificação de Investidor**: Classifica investidor como "qualificado" (patrimônio >= R$ 1.000.000) ou "profissional" (patrimônio >= R$ 10.000.000) para fins regulatórios.

2. **Validação de Hash de Acesso**: Todos os endpoints (exceto geração de hash) exigem validação de hash de autorização no header, retornando 403 se inválido.

3. **Validação de CEP**: Valida formato de CEP (8 dígitos), remove hífen, consulta endereço via broker e cruza cidade retornada com lista global de cidades.

4. **Marcação PEP (Pessoa Exposta Politicamente)**: Controle de compliance para identificação de pessoas politicamente expostas, com lista mínima de 3 PEPs no PDF.

5. **KYC (Know Your Customer)**: Coleta dados de due diligence incluindo países de operação, atividades internacionais, propósito de câmbio, etc.

6. **Controle de Fluxo de Navegação**: Gerencia navegação entre telas de cadastro baseado em tipoUsuario (OFFICER/INTERNET_BANKING), tipoEdicao (PREENCHIDO/NAO_PREENCHIDO/TELAS_CONFIRMACAO) e faseAtualizacao.

7. **Cidadania Americana**: Validação específica para cidadãos americanos com coleta de número NIF (Tax ID).

8. **Usuários Master PJ**: Cadastro de no mínimo 4 usuários administradores para pessoa jurídica.

9. **Pessoas Autorizadas Investimentos**: Cadastro de no mínimo 3 pessoas autorizadas para investimentos em PJ.

10. **Empresas Controladas/Coligadas**: Registro de estrutura societária para pessoa jurídica.

11. **Geração de PDF Contrato**: Processa templates Jasper (PF/PJ) com dados do prospect, monta XML intermediário e gera PDF final.

12. **Timeout de Integração**: Timeout de conexão de 5s e leitura de 20s para chamadas ao ServiceBus.

13. **Tratamento de Erros HTTP**: Converte erros do broker (401, 404, timeout) em exceptions customizadas (ApiUnavailable, ApiTimeout, BusinessException).

---

## 6. Relação entre Entidades

**Entidade Principal: Prospect**
- Possui dados básicos (CPF/CNPJ, nome, data nascimento/constituição, email, telefone)
- Relaciona-se com:
  - **Endereços** (1:N): EnderecoResidencial, EnderecoComercial, OutrosDomicilios, ResidenciaPermanente
  - **Documentos** (1:N): RG, CNH, Comprovante Residência, Estatuto Social, etc
  - **DadosProfissionais** (1:1): Profissão, OcupacaoProfissional, Cargo, Empresa
  - **Patrimonio** (1:1): RendaAnual, BensImoveis, InvestidoMercadoFinanceiro, PatrimonioEstimado
  - **OrigemPatrimonio** (1:1): Flags de origem (atividade profissional, investimentos, herança, etc)
  - **Exterior** (1:1): DomicilioFiscal, Pais, NumeroNIF
  - **PEP** (1:N): Lista de Pessoas Expostas Politicamente relacionadas
  - **Contas** (1:N): ContasDestino para transferências
  - **KYC** (1:1): Dados de due diligence (países, atividades, propósitos)

**Para Pessoa Jurídica, adicionalmente:**
- **NaturezaJuridica** (N:1)
- **AtividadeEconomica** (N:1)
- **EmpresasControladas** (1:N)
- **EmpresasColigadas** (1:N)
- **UsuariosAdministradores** (1:N): Mínimo 4 usuários master
- **PessoasAutorizadasInvestimentos** (1:N): Mínimo 3 pessoas autorizadas
- **GestaoPatrimonial** (1:1): Flags de carteira discricionária, conselho consultivo, etc

**Relacionamentos de Referência:**
- Cidade (N:1) -> UF (N:1) -> Pais (N:1)
- Banco (N:1)
- EstadoCivil (N:1)
- TipoDocumento (N:1)
- TipoPatrimonio (N:1)
- Officer (N:1): Responsável pelo cadastro

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

**Observação**: O sistema não acessa banco de dados diretamente. Todas as operações de leitura são realizadas via chamadas REST ao ServiceBus (broker centralizado), que por sua vez acessa os bancos de dados corporativos.

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

**Observação**: O sistema não atualiza banco de dados diretamente. Todas as operações de escrita (insert/update) são realizadas via chamadas REST ao ServiceBus (broker centralizado), que por sua vez persiste nos bancos de dados corporativos.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Template Jasper PF | leitura | /jasper (classpath) / DocumentoService | Template JasperReports para geração de contrato pessoa física |
| Template Jasper PJ | leitura | /jasper (classpath) / DocumentoService | Template JasperReports para geração de contrato pessoa jurídica |
| PDF Contrato | gravação (memória) | DocumentoService | PDF gerado em memória e retornado via HTTP (byte[]) |
| application.yml | leitura | Spring Boot | Configurações da aplicação por profile (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configurações de logging por ambiente |

---

## 10. Filas Lidas

não se aplica

**Observação**: O sistema não consome mensagens de filas. Toda comunicação é síncrona via REST.

---

## 11. Filas Geradas

não se aplica

**Observação**: O sistema não publica mensagens em filas. Toda comunicação é síncrona via REST.

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **ServiceBus BV (dadosCorporativos)** | REST API | Broker centralizado que expõe 20+ endpoints para: listar dados mestres (bancos, cidades, profissões, etc), CRUD de prospects, validações, obtenção de termos contratuais, envio de emails, geração/validação de hash de acesso |
| **GED (Gerenciamento Eletrônico de Documentos)** | REST API (via ServiceBus) | Sistema de armazenamento de documentos digitalizados, integrado via endpoints incluirDocumentoGED |
| **LDAP** | Autenticação | Servidor LDAP para autenticação de usuários em ambientes des, qa, uat e prd |

**Endpoints ServiceBus Consumidos:**
- listarAtividadeEconomica
- listarBanco
- listarCargo
- listarCidade
- listarEstadoCivil
- listarNaturezaJuridica
- listarOcupacaoProfissional
- listarPais
- listarProfissao
- listarTipoDocumento/{codigo}
- listarTipoPatrimonio
- obterEnderecoCep
- obterPessoa
- obterTermos
- consultarProspect
- consultarRelacionamento
- incluirCadastroProspect
- gerarHashAcesso
- validarHashAcesso
- enviarLink (email)
- incluirDocumentoGED
- listarOfficer/{login}

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com camadas bem definidas (API, Service, Repository, Domain)
- Uso adequado de DTOs (Representations) para contratos de API
- Documentação via Swagger bem estruturada
- Tratamento de erros customizado com exceptions específicas
- Uso de Bean Validation para validações de entrada
- Configuração por profiles para diferentes ambientes
- Uso de Lombok para redução de boilerplate
- Classe base BrokerConnector centraliza lógica de integração REST

**Pontos de Melhoria:**
- DTOs extremamente grandes (IncluirCadastroProspectRequestRepresentation com 55kb) indicam possível falta de decomposição
- Muitas classes de lista customizadas (ListaXXXRepresentation) que apenas estendem ArrayList sem adicionar funcionalidade
- Falta de testes unitários evidentes na análise
- Lógica de negócio complexa em DocumentoService (geração PDF) poderia ser melhor modularizada
- Uso de flags booleanas em excesso (master1-4, countJasper) sugere possível code smell
- Comentários e documentação JavaDoc ausentes ou escassos
- Validação de hash repetida em múltiplos controllers (poderia ser centralizada em interceptor/filter)
- Acoplamento forte com estrutura do ServiceBus (mudanças no broker impactam diretamente o BFF)
- Falta de circuit breaker ou retry para chamadas externas (resiliência)
- Timeouts hardcoded (5s/20s) poderiam ser configuráveis

---

## 14. Observações Relevantes

1. **Arquitetura BFF**: O sistema segue o padrão Backend for Frontend, atuando como orquestrador de múltiplos serviços backend. Isso simplifica o frontend mas centraliza complexidade no BFF.

2. **Dependência Crítica do ServiceBus**: Toda funcionalidade depende da disponibilidade do ServiceBus. Não há cache ou fallback para indisponibilidade.

3. **Geração de PDF em Memória**: PDFs de contrato são gerados em memória e retornados diretamente via HTTP. Para contratos grandes ou alto volume, pode haver impacto de performance/memória.

4. **Segurança por Hash**: Mecanismo de segurança customizado baseado em hash de acesso (não JWT padrão). Hash deve ser validado em cada requisição.

5. **Profiles de Ambiente**: Sistema preparado para 5 ambientes (local, des, qa, uat, prd) com configurações específicas de LDAP e URLs de integração.

6. **Compliance Regulatório**: Sistema trata requisitos regulatórios importantes (PEP, KYC, classificação de investidor) essenciais para instituições financeiras.

7. **Onboarding Digital Completo**: Cobre todo fluxo de cadastro digital desde captura de dados básicos até geração de contrato e envio de email.

8. **Diferenciação PF/PJ**: Lógica complexa para tratar diferenças entre cadastro de pessoa física e jurídica, com campos e validações específicas.

9. **Integração com GED**: Documentos digitalizados são armazenados em sistema GED externo, com referência mantida no cadastro.

10. **Navegação Controlada**: Sistema controla fluxo de navegação entre telas de cadastro baseado em estado (fase, tipo usuário, tipo edição), garantindo sequência correta de preenchimento.

11. **Deploy Docker**: Aplicação containerizada com Dockerfile configurado (OpenJDK 8, porta 8080, memória 64m-128m).

12. **Ausência de Persistência Local**: Sistema é stateless, não mantém estado ou cache local. Toda informação é obtida/persistida via ServiceBus.