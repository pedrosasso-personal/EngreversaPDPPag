# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema de Cockpit de Sustentação para Esteira de Implantação de Contrato, desenvolvido em Java com Spring Boot e Camunda BPM. Trata-se de uma aplicação stateful que utiliza o motor de workflow Camunda para gerenciar processos de implantação de contratos, oferecendo interface web para monitoramento e gestão através do Camunda Cockpit.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `Application` | Classe principal Spring Boot que inicializa a aplicação |
| `ImplantacaoContratoCockpitService` | Serviço de domínio responsável pela lógica de negócio de implantação de contratos |
| `CreateImplantacaoContratoCockpitDelegate` | Delegate do Camunda que executa a criação de implantação de contrato no fluxo BPMN |
| `ImplantacaoContratoCockpitClientImpl` | Implementação da interface de cliente para operações de infraestrutura |
| `ImplantacaoContratoCockpitMapper` | Mapper responsável por converter entidades de domínio em variáveis do Camunda |
| `ImplantacaoContratoCockpit` | Entidade de domínio representando uma implantação de contrato |
| `ImplantacaoContratoCockpitConfiguration` | Configuração Spring para beans e integração LDAP |
| `LdapProperties` | Propriedades de configuração para integração LDAP |
| `CsrPreventionFilter` | Filtro customizado que sobrescreve o filtro CSRF padrão do Camunda |

## 3. Tecnologias Utilizadas

- **Framework Principal**: Spring Boot 2.2.1
- **Motor de Workflow**: Camunda BPM 7.12.0 (Spring Boot Starter 3.4.0)
- **Linguagem**: Java 11
- **Build Tool**: Maven 3.3+
- **Banco de Dados**: 
  - H2 (desenvolvimento local)
  - Microsoft SQL Server (ambientes des/qa/uat/prd)
- **Autenticação**: LDAP (Active Directory)
- **Monitoramento**: Spring Boot Actuator + Micrometer Prometheus
- **Documentação API**: Swagger/SpringFox 2.9.2
- **Logging**: Logback
- **Testes**: JUnit 5, Mockito, Rest Assured, Pact (testes de contrato)
- **Containerização**: Docker (OpenJDK 11 com OpenJ9)
- **Orquestração**: OpenShift/Kubernetes

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | `/actuator/health` | Spring Actuator | Health check da aplicação |
| GET | `/actuator/metrics` | Spring Actuator | Métricas da aplicação |
| GET | `/actuator/prometheus` | Spring Actuator | Métricas no formato Prometheus |
| POST | `/rest/process-definition/key/implantacaocontratocockpit-bpmn/start` | Camunda REST API | Inicia uma instância do processo de implantação |
| GET | `/rest/process-instance/{id}/activity-instances` | Camunda REST API | Recupera instâncias de atividades do processo |
| GET | `/rest/history/detail/{id}` | Camunda REST API | Recupera histórico de variáveis |
| GET | `/rest/history/activity-instance` | Camunda REST API | Recupera histórico de atividades |
| GET | `/swagger.json` | Camunda Swagger | Documentação OpenAPI |
| GET | `/webjars/swagger-ui/3.1.4/index.html` | Swagger UI | Interface Swagger UI |

## 5. Principais Regras de Negócio

1. **Criação de Implantação de Contrato**: O sistema cria uma nova implantação de contrato com ID "12345678909" e versão 47 (valores hardcoded na implementação atual)
2. **Controle de Status**: Gerencia o ciclo de vida da implantação através dos status: CREATED, PENDING e FINISHED
3. **Integração com Workflow**: Utiliza delegates do Camunda para executar lógica de negócio dentro de processos BPMN
4. **Mapeamento de Variáveis**: Converte entidades de domínio em variáveis do processo Camunda para persistência no contexto do workflow
5. **Autenticação LDAP**: Integra com Active Directory para autenticação e autorização de usuários no Camunda Cockpit

## 6. Relação entre Entidades

**ImplantacaoContratoCockpit** (Entidade de Domínio)
- Atributos:
  - `id: String` - Identificador da implantação
  - `version: Integer` - Versão da implantação

**ImplantacaoContratoCockpitStatus** (Enum)
- Valores: CREATED, PENDING, FINISHED
- Representa os estados possíveis de uma implantação

**Relacionamentos**:
- `ImplantacaoContratoCockpitService` utiliza `ImplantacaoContratoCockpitClient` (porta/interface)
- `ImplantacaoContratoCockpitClientImpl` implementa `ImplantacaoContratoCockpitClient`
- `CreateImplantacaoContratoCockpitDelegate` depende de `ImplantacaoContratoCockpitService`
- `ImplantacaoContratoCockpitMapper` converte `ImplantacaoContratoCockpit` para HashMap de variáveis

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Tabelas do Camunda (schema flexgeracaocontrato) | tabela | SELECT | Leitura de definições de processos, instâncias, tarefas e histórico do Camunda BPM |

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Tabelas do Camunda (schema flexgeracaocontrato) | tabela | INSERT/UPDATE | Persistência de instâncias de processos, variáveis, tarefas e histórico de execução |

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação |
| logback-spring.xml | leitura | Logback | Configuração de logging (console e formato JSON comentado) |
| arquivos/[ambiente]/logback-spring.xml | leitura | ConfigMap Kubernetes | Configurações de log específicas por ambiente |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| LDAP/Active Directory | Autenticação | Integração para autenticação e autorização de usuários no Camunda Cockpit via protocolo LDAP |
| SQL Server | Banco de Dados | Banco de dados relacional para persistência do Camunda (schema flexgeracaocontrato) |
| Prometheus | Monitoramento | Exportação de métricas para monitoramento via Micrometer |

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application, common)
- Uso adequado de padrões como Ports & Adapters (hexagonal)
- Configuração adequada de profiles para diferentes ambientes
- Presença de testes (unitários, integração e funcionais)
- Uso de Lombok para reduzir boilerplate
- Documentação via Swagger
- Configuração de monitoramento e health checks

**Pontos Negativos:**
- Implementação com valores hardcoded (`ImplantacaoContratoCockpitClientImpl` retorna sempre os mesmos valores)
- Testes praticamente vazios (apenas `assertTrue(true)`)
- Falta de tratamento de erros e exceções
- Ausência de validações de entrada
- Código parece ser um template/scaffold não completamente implementado
- Falta de documentação inline (JavaDoc) nas classes
- Mapper com uso de tipos raw (LinkedHashMap sem generics adequados)
- Ausência de logs significativos além do debug básico

O código apresenta uma estrutura arquitetural sólida, mas a implementação está incompleta e aparenta ser um projeto gerado por template que ainda não foi totalmente desenvolvido.

## 14. Observações Relevantes

1. **Projeto Template**: O sistema aparenta ser um projeto gerado por scaffolding (plugin `br.com.votorantim.arqt:scaffolding-plugin:0.36.0`) que ainda não foi completamente implementado

2. **Ambientes**: Configurado para 4 ambientes (des, qa, uat, prd) com infraestrutura como código (infra.yml)

3. **Deployment**: Preparado para deploy em OpenShift/Kubernetes com configurações de recursos, probes e volumes

4. **Segurança**: 
   - Filtro CSRF customizado que efetivamente desabilita a proteção CSRF do Camunda
   - Integração LDAP apenas em ambientes não-locais
   - Certificados LDAP não confiáveis aceitos (`setAcceptUntrustedCertificates(true)`)

5. **Portas**: 
   - Aplicação: 8080
   - Actuator/Management: 9090

6. **Schema Database**: Utiliza schema `flexgeracaocontrato` com prefixo de tabelas configurado

7. **Recursos Kubernetes**: 
   - Requests: 80m CPU / 384Mi RAM
   - Limits: 500m CPU / 768Mi RAM

8. **Pipeline**: Configurado para Jenkins com tecnologia `springboot-ocp`, JDK 11 e plataforma Google Cloud

9. **Camunda Cockpit**: Interface web disponível para gestão de processos, tarefas e monitoramento de workflows

10. **Arquitetura Multi-módulo**: Projeto Maven com 3 módulos (application, domain, common) seguindo boas práticas de separação