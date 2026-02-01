# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **springboot-spag-base-valida-retorno-cip** é um componente de validação de retorno de consultas à CIP (Câmara Interbancária de Pagamentos) para pagamentos de boletos. Ele atua como um serviço intermediário que:

- Verifica se é necessário consultar a CIP com base em parâmetros configuráveis
- Realiza consultas à CIP para obter informações atualizadas de boletos
- Valida situação do boleto, beneficiário, valores e datas
- Implementa lógica de contingência quando a CIP está indisponível
- Retorna ocorrências/erros quando as validações falham

O sistema é construído em Spring Boot e expõe APIs REST (v1 e v2) para validação de pagamentos de boletos.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ValidaRetornoCipApi** | Controller REST v1 - recebe DicionarioPagamento e orquestra validações |
| **ValidaRetornoCipV2Api** | Controller REST v2 - recebe request simplificado e retorna response estruturado |
| **ParametrosCipService** | Verifica parâmetros para decidir se consulta CIP ou entra em contingência |
| **ConsultaCipService** | Realiza consulta à CIP com retentativas e preenche dicionário de pagamento |
| **ValidaRetornoCipService** | Valida situação do boleto e beneficiário conforme regras CIP |
| **ValidaValoresCipService** | Valida valores, datas e condições de pagamento (parcial, divergente, vencido) |
| **CalendarioBancoService** | Calcula dias úteis, feriados e próximo dia útil |
| **ConsultaCipRepository** | Integração HTTP com serviço de consulta de boleto calculado |
| **FeriadoRepository** | Integração HTTP com serviço de calendário/dias úteis |
| **ParametrosCipRepository** | Acessa tabelas de parâmetros de interface CIP e validação por cliente |
| **LancamentoRepository** | Consulta informações de lançamento no banco de dados |
| **DicionarioPagamentoWrapper** | Wrapper que encapsula DicionarioPagamento e facilita manipulação de ocorrências |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.7.18** - Framework principal
- **Spring Web** - APIs REST
- **Spring JDBC** - Acesso a banco de dados
- **SQL Server JDBC Driver** - Conexão com banco SQL Server
- **RestTemplate** - Cliente HTTP para integrações
- **Swagger/SpringFox 3.0.0** - Documentação de APIs
- **Logback** - Logging em formato JSON
- **Jackson** - Serialização/deserialização JSON
- **Lombok** - Redução de boilerplate
- **JUnit 4 e Mockito** - Testes unitários
- **Gradle 7.5.1** - Build e gerenciamento de dependências
- **Docker** - Containerização
- **Bibliotecas internas Votorantim**: springboot-arqt-base-trilha-auditoria-web, springboot-arqt-base-security, springboot-arqt-base-lib-database, java-spag-base-pagamentos-commons

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/atacado/pagamentos/validaRetornoCip | ValidaRetornoCipApi | Valida retorno CIP recebendo DicionarioPagamento completo |
| POST | /v2/atacado/pagamentos/validaRetornoCip | ValidaRetornoCipV2Api | Valida retorno CIP com request/response simplificados |

---

## 5. Principais Regras de Negócio

1. **Decisão de Consulta CIP**: Consulta CIP apenas se for pagamento de boleto (liquidação 22), não pré-confirmado, e conforme parametrização do cliente e contingência
2. **Contingência CIP**: Se CIP em contingência e valor abaixo do mínimo parametrizado, aceita sem consultar; se acima, rejeita boleto vencido
3. **Validação de Situação**: Boleto deve estar em análise (05, 11) ou cliente/beneficiário apto (12), exceto baixa operacional (07) com flags específicas
4. **Validação de Beneficiário**: Para valores >= R$ 250.000, valida se beneficiário do pagamento corresponde ao cadastrado na CIP
5. **Validação de Data Limite**: Data de referência não pode ultrapassar data limite de pagamento
6. **Validação de Valores**: 
   - Boletos não parciais devem ser pagos integralmente (tolerância ±0,05)
   - Boletos parciais vencidos, última parcela ou com valor residual devem ser pagos integralmente
   - Boletos divergentes só aceitos se parametrizado (tipos 1-4 com regras específicas)
7. **Retentativas**: Até 5 tentativas de consulta à CIP em caso de falha de comunicação
8. **Espécies Especiais**: Cartão de crédito (31) e boleto proposta (32) não passam por validação de valores

---

## 6. Relação entre Entidades

**Entidades de Domínio:**
- **DicionarioPagamento**: Entidade central contendo todos os dados do pagamento (biblioteca externa)
- **BoletoPagamentoCompletoDTO**: Informações completas do boleto retornadas pela CIP
- **Lancamento**: Informações de lançamento contábil
- **ParametroInterfaceCip**: Parâmetros globais de contingência e validação CIP
- **ParametroValidacaoCipCliente**: Parâmetros específicos por cliente (CPF/CNPJ)

**Relacionamentos:**
- DicionarioPagamento 1--1 BoletoPagamentoCompletoDTO
- BoletoPagamentoCompletoDTO 1--1 PessoaBeneficiarioOriginalDTO
- PessoaBeneficiarioOriginalDTO 1--1 (PessoaFisicaDTO ou PessoaJuridicaDTO)
- DicionarioPagamento N--1 Lancamento (via codLancamento)
- Cliente (CPF/CNPJ) N--1 ParametroValidacaoCipCliente

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbParametroInterfaceCIP | Tabela | SELECT | Parâmetros globais de contingência e validação CIP |
| TbParametroValidacaoCipCliente | Tabela | SELECT | Parâmetros de validação específicos por cliente |
| TbLancamento | Tabela | SELECT | Informações de lançamento contábil (flags de baixa e conta corrente) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| logback-spring.xml | Leitura | Configuração Spring Boot | Configuração de logging em JSON |
| application.yml | Leitura | Configuração Spring Boot | Configurações da aplicação por ambiente |
| lancamentorepository-sql.xml | Leitura | LancamentoRepository | Queries SQL para consulta de lançamentos |
| parametrosciprepository-sql.xml | Leitura | ParametrosCipRepository | Queries SQL para consulta de parâmetros CIP |

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
| **springboot-spag-base-boleto-calculado** | REST API | Consulta informações calculadas de boleto na CIP (host configurável por ambiente) |
| **sboot-dcor-base-atom-dias-uteis** | REST API | Consulta próximo dia útil e lista de dias não úteis (feriados) |
| **LDAP BVNet** | LDAP | Autenticação de usuários (ambientes des/qa/uat/prd) |
| **Banco SQL Server (DBSPAG)** | JDBC | Consulta parâmetros e lançamentos |

---

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (controller, service, repository)
- Uso adequado de padrões Spring Boot
- Testes unitários presentes com boa cobertura
- Uso de Lombok reduz boilerplate
- Configuração externalizada por ambiente
- Logging estruturado em JSON
- Tratamento de erros com ocorrências tipadas

**Pontos de Melhoria:**
- Lógica de negócio complexa em alguns métodos (ex: validações em ValidaValoresCipService)
- Métodos privados extensos que poderiam ser extraídos
- Alguns "magic numbers" e strings hardcoded (ex: "05", "07", "12" para situações)
- Comentários em português misturados com código em inglês
- Falta de constantes para valores repetidos (ex: tolerância 0.05)
- Alguns métodos com muitos parâmetros ou lógica condicional aninhada
- Tratamento de exceções genérico em alguns pontos
- Código de conversão entre representações poderia ser mais limpo (mappers)

---

## 14. Observações Relevantes

1. **Versionamento de API**: Sistema possui duas versões de API (v1 e v2) com contratos diferentes - v2 é mais simplificada
2. **Contingência**: Sistema implementa modo de contingência quando CIP está indisponível, com validações reduzidas
3. **Retentativas**: Implementa até 5 retentativas automáticas em caso de falha na comunicação com CIP
4. **Feriados Customizados**: Adiciona feriados extras hardcoded (25/01, 09/07, 20/11/2024) além dos retornados pela API
5. **Tolerância de Valores**: Aceita diferença de ±R$ 0,05 nas validações de valores integrais
6. **Autenticação**: Usa Basic Auth para integrações e LDAP/InMemory para autenticação de usuários
7. **Ambientes**: Configurado para 4 ambientes (des, qa, uat, prd) com parametrizações específicas
8. **Docker**: Preparado para containerização com Dockerfile e scripts Gradle
9. **Sanitização de Logs**: Implementa sanitização de mensagens de log para segurança (LogUtil)
10. **Biblioteca Externa**: Depende fortemente de biblioteca interna "java-spag-base-pagamentos-commons" para DTOs