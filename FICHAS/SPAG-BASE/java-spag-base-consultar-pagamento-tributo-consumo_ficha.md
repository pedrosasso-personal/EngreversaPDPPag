# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **java-spag-base-consultar-pagamento-tributo-consumo** é um componente Java EE desenvolvido para consultar informações de pagamentos de tributos. Ele atua como um intermediário que recebe requisições REST, busca configurações no banco de dados SPAG, consome uma API externa (IS2B) para obter dados de pagamento e retorna as informações processadas ao solicitante. O sistema utiliza autenticação OAuth para integração com a API externa e implementa controles de segurança baseados em roles.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `ConsultarPagamentoTributoBean` | EJB Stateless que implementa a lógica de negócio principal para consulta de pagamentos de tributos |
| `ConsultarPagamentoTributo` (REST) | Endpoint REST que expõe o serviço de consulta de pagamento via HTTP |
| `ConsultarIntegrationServices` | Responsável pela integração com a API externa (IS2B) para consulta de pagamentos |
| `CriarTokenIntegration` | Gerencia a criação e renovação de tokens OAuth para autenticação na API externa |
| `HttpCaapiIntegration` | Classe abstrata que encapsula a lógica de chamadas HTTP para a CA-API |
| `PagamentoTributoSpagDaoImpl` | DAO que realiza consultas no banco de dados SPAG para buscar URLs de configuração |
| `ConsultaRowMapper` | Mapper Spring JDBC para conversão de ResultSet em objetos de domínio |
| `ConsultarRequest` / `ConsultarResponse` | DTOs para comunicação com a API externa |
| `Pagamento` | Entidade de domínio representando dados de um pagamento |
| `CaapiToken` | Bean de sessão que armazena o token JWT para reutilização |

---

## 3. Tecnologias Utilizadas

- **Java EE 6/7** (EJB 3.1, JAX-RS, CDI)
- **Maven** (gerenciamento de dependências e build multi-módulo)
- **WebSphere Application Server** (IBM WAS)
- **Spring JDBC** (acesso a dados)
- **Apache HttpClient** (chamadas HTTP)
- **Gson** (serialização/deserialização JSON)
- **Log4j2 / SLF4J** (logging)
- **Swagger** (documentação de APIs REST)
- **JUnit, Mockito, PowerMock** (testes unitários)
- **OAuth 2.0** (autenticação)
- **Apache Commons Lang3** (utilitários)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/atacado/pagamentos/consultarPagamento` | `ConsultarPagamentoTributo` | Consulta informações de pagamento de tributo com base em dados do dicionário de pagamento |

---

## 5. Principais Regras de Negócio

1. **Consulta de URL dinâmica**: O sistema busca a URL da API externa no banco de dados SPAG antes de realizar a consulta, permitindo configuração dinâmica.

2. **Mapeamento de banco remetente**: Se o código do banco remetente global for 413 ou 436, o sistema força o código do banco para 413 na requisição.

3. **Tratamento de documento**: Prioriza o uso de `cnpjCpfRemetenteFintech` sobre `cnpjCpfRemetente` quando disponível.

4. **Conversão de datas**: Converte datas do formato `dd/MM/yyyy` para `yyyy-MM-dd` no retorno.

5. **Retry automático**: Em caso de falha na chamada da API externa, o sistema tenta novamente uma vez antes de lançar exceção.

6. **Validação de sucesso**: Apenas quando o código de erro retornado é "000", os dados detalhados do pagamento são mapeados para o objeto de resposta.

7. **Gerenciamento de token OAuth**: O sistema mantém um token em sessão e o renova automaticamente quando recebe códigos HTTP 401 ou 403.

---

## 6. Relação entre Entidades

**Entidades principais:**

- **ConsultarRequest**: Contém `numeroDocumento`, `tipoServico`, `linhaDigitavel`, `codigoBanco`
- **ConsultarResponse**: Contém `codigoErro`, `mensagemErro` e um objeto `Pagamento`
- **Pagamento**: Contém dados detalhados do pagamento (statusTransacao, nomeCedente, dataVencimento, valores, etc.)
- **ConsultaUrl**: Entidade que representa a URL de consulta armazenada no banco
- **DicionarioPagamento**: DTO externo (biblioteca spag-lib) usado para entrada e saída do serviço REST

**Relacionamentos:**
- ConsultarResponse **contém** Pagamento (composição 1:1)
- ConsultarRequest e ConsultarResponse são usados na comunicação com a API externa
- DicionarioPagamento é convertido para ConsultarRequest e recebe dados de ConsultarResponse

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| `DBSPAG..TbParametroPagamentoTributo` | Tabela | SELECT | Armazena a URL de consulta da API externa (campo `DsUrlConsultaPagamento`) |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| `config-arqt-base.properties` | Leitura | `ConfigArqtrBaseProperties` | Contém configurações de URLs de APIs (gateway, OAuth, webservices) por ambiente |
| `config-spag.properties` | Leitura | Testes | Contém credenciais e URIs específicas da API SPAG |
| `errorMessages.properties` | Leitura | Commons | Repositório de mensagens de erro do sistema |
| `roles.properties` | Leitura | Commons | Lista de roles de segurança da aplicação |
| `PagamentoTributoSpagDaoImpl-sql.xml` | Leitura | `PagamentoTributoSpagDaoImpl` | Arquivo XML contendo queries SQL do DAO |

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
| **API IS2B (Parceiros)** | REST | API externa para consulta de dados de pagamento de tributos. Endpoint: `/v2/parceiros/is2b/pagamentos/dados-conta/consultar` |
| **API Gateway OAuth** | REST | Serviço de autenticação OAuth 2.0 para obtenção de tokens de acesso (client_credentials grant type) |
| **Banco de Dados SPAG** | JDBC | Banco de dados SQL Server (DBSPAG) para consulta de parâmetros de configuração via DataSource `jdbc/spagBaseDBSPAGDS` |

**Detalhes da integração com API IS2B:**
- Autenticação via OAuth 2.0 (Bearer token)
- Formato: JSON
- Trilha de auditoria incluída nos headers
- Retry automático em caso de falha
- Renovação automática de token em caso de expiração

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades em camadas (business, persistence, integration, domain, rs)
- Uso adequado de padrões Java EE (EJB, CDI, JAX-RS)
- Implementação de retry e tratamento de token expirado
- Logging adequado em pontos críticos
- Uso de injeção de dependências

**Pontos Negativos:**
- **Código comentado**: Diversos trechos de código comentado no projeto (módulos ws, jms, configurações)
- **Tratamento de exceções genérico**: Uso excessivo de `catch (Exception e)` sem tratamento específico
- **Lógica de retry rudimentar**: Implementada com try-catch aninhado em vez de mecanismo mais robusto
- **Hardcoding**: Valores como código de banco (655, 413, 436) e código de erro ("000") estão hardcoded
- **Falta de constantes**: Strings mágicas espalhadas pelo código
- **Inconsistência de nomenclatura**: Mistura de português e inglês em nomes de variáveis e métodos
- **Testes incompletos**: Alguns testes marcados como NAO_ENVIAR, cobertura aparentemente baixa
- **Documentação**: Falta de Javadoc em métodos públicos importantes
- **Acoplamento**: Dependência direta de biblioteca externa (spag-lib) sem abstração

---

## 14. Observações Relevantes

1. **Arquitetura Multi-módulo**: O projeto segue uma estrutura Maven multi-módulo bem organizada (business, commons, domain, ear, integration, jms, persistence, rs, ws).

2. **Módulos desabilitados**: Os módulos `jms` e `ws` estão comentados no build, indicando que o sistema atualmente expõe apenas interface REST.

3. **Segurança**: O sistema implementa autenticação baseada em roles (`spag-integracao`, `intr-middleware`) e utiliza BASIC authentication no WebSphere.

4. **Configuração por ambiente**: O sistema suporta múltiplos ambientes (DES, QA, UAT, PRD) através de arquivos de propriedades.

5. **Dependências de arquitetura**: O projeto depende fortemente de bibliotecas corporativas (`fjee-base`, `arqt-base`, `spag-base-pagamentos-commons`).

6. **Classloader customizado**: Configuração de classloader PARENT_LAST no WebSphere para evitar conflitos de bibliotecas.

7. **Trilha de auditoria**: Implementação de handlers JAX-RS/JAX-WS para captura de trilha de auditoria em todas as requisições.

8. **JNDI para credenciais**: Credenciais OAuth são obtidas via JNDI (`cell/persistent/client_id_spag`, `cell/persistent/client_secret_spag`), seguindo boas práticas de segurança.

9. **Versionamento**: O projeto utiliza Git para controle de versão e está na versão 0.7.0.

10. **Pipeline CI/CD**: Arquivo `jenkins.properties` indica integração com Jenkins para deploy automatizado.