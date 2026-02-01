# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-grade-horaria** é um microsserviço orquestrador desenvolvido em Spring Boot que fornece consultas de grade horária para transações bancárias do Banco Digital. O sistema determina se uma transação pode ser realizada em determinado horário, considerando dias úteis e horários de funcionamento específicos para cada tipo de transação (TED, Boletos CIP, Tributo e Consumo). Atua como orquestrador consultando serviços atômicos de dias úteis e domínio de conta corrente, aplicando regras de negócio para determinar se a grade horária está aberta ou encerrada e qual será a próxima grade disponível.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal Spring Boot que inicializa a aplicação |
| **GradeHorariaController** | Controller REST que expõe o endpoint de consulta de grade horária |
| **GradeHorariaBusiness** | Camada de negócio que coordena a consulta de grade horária |
| **GradeHorariaService** | Serviço que utiliza Apache Camel para orquestrar chamadas aos repositórios |
| **GradeHorariaTedStrategy** | Implementação da estratégia de consulta específica para transações TED |
| **GradeHorariaRepositoryImpl** | Implementação do repositório que consulta o serviço de domínio de conta corrente |
| **DiaUtilRepositoryImpl** | Implementação do repositório que consulta o serviço de dias úteis |
| **GradeHorariaRouter** | Roteador Apache Camel para consultas de grade horária |
| **DiaUtilRouter** | Roteador Apache Camel para validação de dias úteis |
| **CamelContextWrapper** | Wrapper do contexto Apache Camel para gerenciamento de rotas |
| **DateUtil** | Utilitário para manipulação e validação de datas |
| **GradeHorariaMapper** | Mapeador entre objetos de domínio e representações REST |
| **ExceptionControllerHandler** | Tratador centralizado de exceções da aplicação |

---

## 3. Tecnologias Utilizadas

- **Java 11** - Linguagem de programação
- **Spring Boot 2.x** - Framework principal
- **Spring Web** - Para criação de APIs REST
- **Spring Security OAuth2** - Autenticação e autorização via JWT
- **Apache Camel 3.0.1** - Framework de integração e orquestração
- **Maven** - Gerenciamento de dependências e build
- **Swagger/OpenAPI 3.0** - Documentação de APIs
- **Springfox 3.0.0** - Geração de documentação Swagger
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Logging com formato JSON
- **Lombok** - Redução de boilerplate
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **RestAssured** - Testes funcionais de APIs
- **Pact** - Testes de contrato
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração de containers
- **Grafana** - Visualização de métricas

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/v1/banco-digital/grade` | GradeHorariaController | Consulta a grade horária de uma transação específica, retornando se está aberta/encerrada e a próxima grade disponível |

**Parâmetros do endpoint:**
- `tipoTransacao` (obrigatório): TED, BOLETO_CIP, BOLETO_TRIBUTO, BOLETO_CONSUMO
- `data` (opcional): Data para consulta no formato yyyy-MM-dd
- `codigoPraca` (opcional): Código da praça/região

---

## 5. Principais Regras de Negócio

1. **Validação de Dia Útil**: Antes de consultar a grade horária, o sistema valida se a data informada é um dia útil bancário
2. **Estratégia por Tipo de Transação**: Atualmente implementada apenas para TED, com estrutura preparada para outros tipos (Strategy Pattern)
3. **Determinação de Grade Encerrada**: Para consultas do dia atual, verifica se o horário atual está dentro do intervalo da grade (início e fim)
4. **Próxima Grade Disponível**: Quando a grade está encerrada, busca automaticamente a próxima grade disponível no próximo dia útil
5. **Consulta de Data Futura**: Para datas futuras, sempre retorna a grade como não encerrada
6. **Validação de Data Retroativa**: Não permite consultas para datas anteriores à data atual
7. **Conversão de Timezone**: Trabalha com datas em formato ISO 8601 com timezone
8. **Fallback para Data Atual**: Se nenhuma data for informada, utiliza a data atual como padrão

---

## 6. Relação entre Entidades

**Entidades de Domínio:**

- **ConsultaGradeHoraria**: Entidade principal que encapsula uma consulta de grade horária
  - Contém: tipo de transação, data de consulta, data atual, flag se é hoje, grade atual e próxima grade
  
- **GradeHoraria**: Representa um período de grade horária
  - Contém: data/hora de início, data/hora de fim, flag indicando se está encerrada
  
- **DataValidada**: Resultado da validação de dia útil
  - Contém: data útil validada, flag indicando se é dia útil

**Enumerações:**

- **TipoTransacaoEnum**: TED, BOLETO_CIP, BOLETO_TRIBUTO, BOLETO_CONSUMO
- **PracaEnum**: BRASIL, SAO_PAULO, RIO_JANEIRO, NOVA_YORK
- **CodigoErroEnum**: Códigos de erro de negócio

**Relacionamentos:**
- ConsultaGradeHoraria (1) -> (1) TipoTransacaoEnum
- ConsultaGradeHoraria (1) -> (0..1) GradeHoraria (grade atual)
- ConsultaGradeHoraria (1) -> (0..1) GradeHoraria (próxima grade)

---

## 7. Estruturas de Banco de Dados Lidas

não se aplica

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot (resources) | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback (resources e /usr/etc/log) | Configuração de logs em formato JSON para diferentes ambientes |
| swagger-server/*.yaml | leitura | Swagger Codegen Maven Plugin | Especificações OpenAPI para geração de interfaces REST |
| swagger-client/*.yaml | leitura | Swagger Codegen Maven Plugin | Especificações OpenAPI dos serviços consumidos (dias úteis e conta corrente) |

---

## 10. Filas Lidas

não se aplica

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente-dominio** | API REST | Serviço atômico que fornece informações de grade horária por tipo de transação. Endpoint: `/v1/banco-digital/grade` |
| **sboot-dcor-base-atom-dias-uteis** | API REST | Serviço atômico que valida se uma data é dia útil e retorna o próximo dia útil. Endpoint: `/v1/corporativo/calendario/validar-dia-util/{data}` |
| **OAuth2/JWT Provider** | Autenticação | Servidor de autenticação para validação de tokens JWT (URLs variam por ambiente) |

**Observações:**
- Todas as integrações utilizam RestTemplate com segurança OAuth2
- URLs são configuráveis por ambiente via variáveis de ambiente
- Comunicação interna no cluster Kubernetes via service discovery

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada seguindo Clean Architecture (separação em camadas: domain, application)
- Uso adequado de padrões de projeto (Strategy, Repository, Wrapper)
- Boa cobertura de testes unitários com casos de teste bem definidos
- Uso de Lombok reduzindo boilerplate
- Configuração adequada de profiles para diferentes ambientes
- Documentação OpenAPI bem estruturada
- Tratamento centralizado de exceções
- Uso de Apache Camel para orquestração de forma elegante
- Código limpo e legível com nomenclatura adequada
- Separação clara de responsabilidades

**Pontos de Melhoria:**
- Apenas a estratégia TED está implementada, outras transações lançam UnsupportedOperationException
- Falta de validação mais robusta de parâmetros de entrada em alguns pontos
- Alguns métodos poderiam ter documentação JavaDoc mais detalhada
- Ausência de circuit breaker ou retry para chamadas externas (resiliência)
- Logs poderiam incluir mais informações de contexto para troubleshooting
- Testes de integração e funcionais estão vazios (apenas estrutura)

---

## 14. Observações Relevantes

1. **Arquitetura Modular**: O projeto está dividido em três módulos Maven (common, domain, application), facilitando manutenção e evolução

2. **Preparado para Expansão**: A estrutura com Strategy Pattern permite fácil adição de novos tipos de transação sem modificar código existente

3. **Observabilidade**: Integração completa com Prometheus/Grafana para monitoramento de métricas customizadas

4. **Segurança**: Implementa OAuth2 com JWT para autenticação e autorização, com endpoints públicos configuráveis

5. **DevOps Ready**: Possui Dockerfile, configurações Kubernetes/OpenShift e pipeline Jenkins configurado

6. **Testes Estruturados**: Separação clara entre testes unitários, integração e funcionais, com suporte a testes de contrato (Pact)

7. **Versionamento de API**: Utiliza versionamento na URL (/v1/) seguindo boas práticas REST

8. **Configuração por Ambiente**: Suporte completo a múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas

9. **Auditoria**: Integração com biblioteca de trilha de auditoria do Banco Votorantim

10. **Limitação Atual**: Sistema atualmente suporta apenas consultas de grade horária para TED, outras transações retornarão erro 400