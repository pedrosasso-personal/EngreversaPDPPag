# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema atômico responsável por gerenciar informações de pagamento de tributos e boletos. O serviço oferece funcionalidades para gravar, consultar e validar dados de boletos, incluindo consultas de segunda via e validação de horários para evitar pagamentos duplicados. Atua como repositório centralizado de informações de pagamentos de boletos no contexto do CCBD (Centro de Controle de Banco de Dados) do Banco Votorantim.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `InfoPgtoTribBolController` | Controlador REST que expõe endpoints para gravação e consulta de boletos |
| `InfoPgtoTribBolServiceImpl` | Implementação da lógica de negócio para operações com boletos |
| `InfoPgtoTribBolRepository` | Interface de acesso a dados usando JDBI para operações no banco |
| `BoletoAdapter` | Adaptador para conversão entre entidades de domínio e representações REST |
| `TbDetalheBoleto` | Entidade de domínio representando detalhes completos de um boleto |
| `TbBoleto` | Entidade de domínio representando informações básicas de boleto |
| `TbDetalheBoletoPgmCartao` | Entidade estendida para boletos pagos com cartão |
| `DatabaseConfiguration` | Configuração de conexão com banco de dados SQL Server |
| `DetalheBoletoMapper` | Mapper JDBI para conversão de ResultSet em TbDetalheBoleto |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.x
- **Linguagem**: Java 11
- **Gerenciamento de Dependências**: Maven 3.5.3
- **Banco de Dados**: Microsoft SQL Server
- **Acesso a Dados**: JDBI 3.9.1
- **Documentação API**: Swagger/OpenAPI 3.0 (Springfox)
- **Segurança**: Spring Security OAuth2 com JWT
- **Logging**: Logback com formato JSON
- **Monitoramento**: Spring Actuator + Micrometer + Prometheus
- **Utilitários**: Lombok 1.18.10
- **Testes**: JUnit Jupiter 5+, Mockito
- **Containerização**: Docker
- **Orquestração**: OpenShift (Google Cloud Platform)

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | `/v1/corporativo/pagamentos/boleto-info` | InfoPgtoTribBolController | Grava informações de um novo boleto |
| GET | `/v1/corporativo/pagamentos/boleto-info` | InfoPgtoTribBolController | Consulta boleto por código/linha digitável ou ID |
| GET | `/v1/corporativo/pagamentos/segunda-via` | InfoPgtoTribBolController | Consulta segunda via por protocolo ou código de autorização |
| GET | `/v1/corporativo/pagamentos/segunda-via-agendamento` | InfoPgtoTribBolController | Consulta segunda via de agendamento por NSU |
| GET | `/v1/corporativo/pagamentos/boleto-info/validar-horario` | InfoPgtoTribBolController | Valida se houve pagamentos nas últimas 48 horas |

## 5. Principais Regras de Negócio

- **Gravação de Boleto**: Ao gravar um boleto, o sistema primeiro insere os detalhes na tabela `TbDetalheBoleto`, depois na `TbTransacaoBoleto`, e finalmente verifica se já existe registro na `TbBoleto` (insere novo ou atualiza existente)
- **Validação de Horário**: Impede pagamentos duplicados verificando se houve lançamentos nas últimas 48 horas para o mesmo código de barras ou linha digitável
- **Exclusão de Status**: Na validação de horário, exclui boletos com status 5 e 6 (provavelmente cancelados/rejeitados)
- **Exclusão de Espécie**: Na validação por linha digitável, exclui boletos com código de espécie 31
- **Consulta Flexível**: Permite consulta por múltiplos identificadores (código, ID, NSU, protocolo, código de autorização)
- **Tratamento de Código de Barras**: Se não houver código de barras, utiliza a linha digitável como identificador principal
- **Valores Padrão**: Campos monetários opcionais são preenchidos com zero quando não informados

## 6. Relação entre Entidades

**TbBoleto** (1) ← (N) **TbDetalheBoleto** (1) ← (1) **TbTransacaoBoleto**
- TbBoleto: Armazena referência ao código de barras e ao detalhe mais recente
- TbDetalheBoleto: Contém informações completas do boleto (beneficiário, pagador, valores)
- TbTransacaoBoleto: Registra informações transacionais (valores calculados, horários, protocolos)

**TbDetalheBoleto** (1) ← (N) **TbLancamentoBoleto**
- TbLancamentoBoleto: Registra cada lançamento/pagamento realizado

**TbDetalheBoletoPgmCartao**: Extensão de TbDetalheBoleto com informações adicionais do remetente/pagador final quando o pagamento é feito com cartão

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDPagamentoConta.TbBoleto | Tabela | SELECT | Consulta informações básicas de boletos por código de barras |
| CCBDPagamentoConta.TbDetalheBoleto | Tabela | SELECT | Consulta detalhes completos de boletos |
| CCBDPagamentoConta.TbTransacaoBoleto | Tabela | SELECT | Consulta informações transacionais de boletos |
| CCBDPagamentoConta.TbLancamentoBoleto | Tabela | SELECT | Consulta lançamentos/pagamentos de boletos |
| CCBDPagamentoConta.TbStatusBoleto | Tabela | SELECT | Join para obter status do boleto |
| CCBDPagamentoConta.TbFormaPagamento | Tabela | SELECT | Join para filtrar forma de pagamento (cartão = 2) |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| CCBDPagamentoConta.TbDetalheBoleto | Tabela | INSERT | Insere novos detalhes de boleto |
| CCBDPagamentoConta.TbTransacaoBoleto | Tabela | INSERT | Insere informações transacionais do boleto |
| CCBDPagamentoConta.TbBoleto | Tabela | INSERT | Insere novo registro de boleto |
| CCBDPagamentoConta.TbBoleto | Tabela | UPDATE | Atualiza referência ao detalhe mais recente |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | Leitura | Spring Boot | Configurações da aplicação por ambiente |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON |
| *.sql | Leitura | InfoPgtoTribBolRepository | Queries SQL para operações no banco |
| sboot-ccdb-base-atom-info-pgto-trib-bol.yaml | Leitura | Swagger Codegen | Especificação OpenAPI para geração de código |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| SQL Server (DBCCBD) | Banco de Dados | Banco de dados principal para persistência de informações de boletos |
| OAuth2/JWT Provider | Autenticação | Serviço de autenticação OAuth2 com tokens JWT (api-digital*.bancovotorantim.com.br) |
| Prometheus | Monitoramento | Exportação de métricas para monitoramento |

## 13. Avaliação da Qualidade do Código

**Nota:** 7/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (controller, service, repository, adapter)
- Uso adequado de padrões como Adapter e Repository
- Documentação OpenAPI bem estruturada
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Implementação de health checks e métricas

**Pontos de Melhoria:**
- Tratamento de exceções genérico (catch Exception) sem diferenciação de tipos específicos
- Falta de validações de entrada mais robustas nos controllers
- Conversões de tipos com possíveis NullPointerExceptions (ex: `Integer.parseInt` sem validação)
- Lógica de negócio com múltiplos ifs aninhados no BoletoAdapter
- Ausência de testes unitários nos arquivos fornecidos
- Comentários em português misturados com código em inglês
- Alguns métodos muito longos (ex: `transformToDetalheBoleto`)
- Uso de strings literais para flags ("S"/"N") ao invés de enums

## 14. Observações Relevantes

- O sistema utiliza JDBI ao invés de JPA/Hibernate, o que oferece mais controle sobre as queries SQL mas requer mais código manual
- Há suporte específico para pagamentos com cartão através da entidade `TbDetalheBoletoPgmCartao`
- A validação de horário de 48 horas é uma regra crítica para evitar pagamentos duplicados
- O sistema está preparado para deploy em múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas
- Utiliza autenticação OAuth2 com JWT, indicando integração com gateway de APIs corporativo
- O projeto segue padrões arquiteturais do Banco Votorantim (arqt-base-master-springboot)
- Logs estruturados em JSON facilitam análise e monitoramento
- A aplicação expõe métricas no formato Prometheus na porta 9090