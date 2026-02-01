# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-ccbd-base-orch-efet-debito** é um microserviço orquestrador corporativo responsável por confirmar operações de débito e gerenciar bloqueios de saldo em contas correntes do Banco Votorantim. O sistema implementa fluxos de efetivação de débito, cancelamento de bloqueios e gerenciamento de monitoramentos de saldo, com suporte a operações em modo stand-in (contingência) para garantir disponibilidade mesmo quando sistemas principais estão indisponíveis.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **EfetDebitoController** | Controlador REST que expõe endpoints para efetivação de débito, cancelamento de bloqueios e gerenciamento de monitoramentos |
| **EfetDebitoService** | Serviço de domínio que orquestra os fluxos de negócio utilizando Apache Camel |
| **EfetDebitoRouter** | Roteador Camel para fluxo de efetivação de débito |
| **EstDebitoRouter** | Roteador Camel para fluxo de cancelamento de bloqueio |
| **CancelarMonitoramentoRouter** | Roteador Camel para fluxo de cancelamento de monitoramento |
| **EfetMonitoramentoRouter** | Roteador Camel para fluxo de efetivação de monitoramento |
| **EfetDebitoRepositoryImpl** | Implementação de repositório para efetivação de débito no sistema principal |
| **EfetDebitoStandInRepositoryImpl** | Implementação de repositório para efetivação de débito no sistema stand-in |
| **CancelarBloqueioRepositoryImpl** | Implementação de repositório para cancelamento de bloqueios |
| **ConsultaMonitoramentoRepositoryImpl** | Implementação de repositório para consulta de monitoramentos |
| **ValidaContasStandin** | Utilitário para validação de contas permitidas no modo stand-in |
| **CamelContextWrapper** | Wrapper para gerenciamento do contexto Apache Camel |

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal da aplicação
- **Apache Camel 3.2.0** - Framework de integração e roteamento
- **Spring Security OAuth2** - Segurança com JWT
- **Springfox/Swagger 3.0.0** - Documentação de APIs
- **RestTemplate** - Cliente HTTP para integrações
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Framework de logging
- **Lombok** - Redução de boilerplate
- **Maven** - Gerenciamento de dependências
- **Docker** - Containerização
- **Kubernetes/OpenShift** - Orquestração de containers
- **Java 11** - Linguagem de programação

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST | /v1/banco-digital/contas/debito/confirmar | EfetDebitoController | Efetiva uma operação de débito em conta corrente |
| POST | /v1/banco-digital/contas/bloqueio/cancelar | EfetDebitoController | Cancela um bloqueio de saldo específico |
| DELETE | /v1/banco-digital/contas/monitoramentos/{codigoAcompanhamentoBloqueio} | EfetDebitoController | Cancela um monitoramento de saldo |
| POST | /v1/banco-digital/contas/monitoramentos/{codigoAcompanhamentoBloqueio} | EfetDebitoController | Efetiva um monitoramento de saldo com débito |

## 5. Principais Regras de Negócio

1. **Validação de Contas Stand-in**: Verifica se a conta está habilitada para operações em modo stand-in através de lista configurável
2. **Fluxo de Contingência**: Quando o sistema principal está indisponível ou a conta está fechada, redireciona operações para o sistema stand-in
3. **Consulta de Transações Pendentes**: Antes de efetivar débito, verifica se existe transação pendente no stand-in
4. **Efetivação Condicional**: Débitos podem ser condicionais ao saldo ou incondicionais (flag flLancamentoIncondicionalSaldo)
5. **Bloqueio de Saldo**: Suporta débitos com bloqueio prévio (sqUltimoBloqueioSaldo) ou débitos legados sem bloqueio
6. **Monitoramento de Saldo**: Permite criar monitoramentos que agregam múltiplos bloqueios e efetiva débito pelo valor total
7. **Cancelamento em Cascata**: Ao cancelar monitoramento, cancela todos os bloqueios associados
8. **Validação de Bloqueio Renda Fixa**: Flag para identificar bloqueios judiciais (flBloqueioRendaFixa)
9. **Tratamento de Erros de Negócio**: Exceções customizadas com códigos específicos (BDCC_SALDO_INSUFICIENTE, BDCC_CONTA_ENCERRADA, etc)
10. **Auditoria**: Integração com trilha de auditoria corporativa

## 6. Relação entre Entidades

**EfetDebito**
- Contém: InfoConta (composição)
- Atributos principais: valorOperacao, codigoTransacao, dataEfetivacaoOperacao, sqUltimoBloqueioSaldo

**InfoConta**
- Atributos: codigoBanco, agencia, conta, tipoConta

**EfetDebitoProcesso**
- Contém: EfetDebito (composição)
- Flags: contaCorrenteFechado, transacaoPendenteStandIn

**CancelarBloqueio**
- Atributos: codigoBanco, agencia, conta, tipoConta, sqBloqueioSaldo
- Flags: contaCorrenteFechado, transacaoPendenteStandIn

**Monitoramento**
- Contém: EfetDebito, MonitoramentoSaldo (composição)
- Atributo: codigoAcompanhamentoBloqueio

**MonitoramentoSaldo**
- Contém: Lista de MonitoramentoSaldoBloqueado
- Atributos: cdMonitoramentoSaldo, nuContaCorrente, vrSolicitado, vrBloqueado

**MonitoramentoSaldoBloqueado**
- Atributos: sqSaldoBloqueado, vrOperacao

## 7. Estruturas de Banco de Dados Lidas

não se aplica

*Observação: O sistema não acessa diretamente banco de dados. Todas as operações são realizadas através de chamadas REST para outros microserviços (atoms).*

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

*Observação: O sistema não atualiza diretamente banco de dados. Todas as operações de escrita são realizadas através de chamadas REST para outros microserviços (atoms).*

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (des, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logs em formato JSON para diferentes ambientes |

## 10. Filas Lidas

não se aplica

## 11. Filas Geradas

não se aplica

## 12. Integrações Externas

| Sistema Externo | Tipo | Descrição |
|-----------------|------|-----------|
| **sboot-ccbd-base-atom-conta-corrente** | REST API | Serviço atômico para operações de débito e cancelamento de bloqueios em conta corrente |
| **sboot-ccbd-base-atom-conta-corrente-stdin** | REST API | Serviço atômico stand-in para operações de débito e consulta de transações em modo contingência |
| **sboot-ccbd-base-atom-bloqueios-saldo** | REST API | Serviço atômico para consulta e inativação de monitoramentos de bloqueio de saldo |
| **OAuth2 JWT Provider** | REST API | Serviço de autenticação e autorização com tokens JWT |

**Detalhamento das Integrações:**

1. **Atom Conta Corrente**: 
   - Endpoints: `/debito/confirmar/`, `/debito-legado/confirmar/`, `/bloqueio/cancelar/`
   - Operações: Efetivação de débito, cancelamento de bloqueios

2. **Atom Conta Corrente Stand-in**:
   - Endpoints: `/contas/transacao`, `/contas/debito/confirmar`, `/contas/bloqueio/cancelar`
   - Operações: Consulta de transações pendentes, efetivação de débito em contingência

3. **Atom Bloqueios Saldo**:
   - Endpoints: `/v1/contas/monitoramentos/{id}` (GET, DELETE)
   - Operações: Consulta e inativação de monitoramentos

## 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (presentation, domain, infrastructure)
- Uso adequado de padrões como Repository e Service
- Implementação de rotas Apache Camel para orquestração clara dos fluxos
- Tratamento de exceções customizado com códigos de erro específicos
- Uso de Lombok para redução de boilerplate
- Configuração adequada de segurança OAuth2
- Documentação OpenAPI/Swagger bem estruturada
- Testes unitários, integração e funcionais separados
- Configuração de métricas e observabilidade (Prometheus)

**Pontos de Melhoria:**
- Falta de validação de entrada nos controllers (Bean Validation)
- Classe `ValidaContasStandin` com método que sempre retorna `true` (implementação incompleta)
- Uso de `@SneakyThrows` que oculta tratamento de exceções
- Logs com informações sensíveis que precisam de sanitização (parcialmente implementado)
- Falta de documentação JavaDoc nas classes principais
- Configuração de recursos (CPU/memória) muito baixa para ambiente de desenvolvimento
- Alguns métodos longos que poderiam ser refatorados (ex: nos repositórios)
- Falta de constantes para strings mágicas em alguns pontos

## 14. Observações Relevantes

1. **Arquitetura Hexagonal**: O projeto segue princípios de arquitetura hexagonal com separação clara entre domínio (domain) e aplicação (application), utilizando ports e adapters.

2. **Apache Camel**: A escolha do Apache Camel para orquestração permite fluxos complexos com tratamento de erro robusto através de `onCompletion` e `onFailureOnly`.

3. **Modo Stand-in**: O sistema implementa um padrão de contingência sofisticado que permite operações mesmo quando sistemas principais estão indisponíveis, essencial para disponibilidade bancária.

4. **Segurança**: Implementa OAuth2 com JWT, com endpoints públicos configuráveis e integração com sistema de auditoria corporativo.

5. **Observabilidade**: Configuração completa de métricas, health checks e logs estruturados em JSON para ambientes produtivos.

6. **Multi-ambiente**: Configuração bem estruturada para múltiplos ambientes (des, qa, uat, prd) através de profiles Spring e ConfigMaps Kubernetes.

7. **Versionamento de API**: Utiliza versionamento de API através do path (`/v1/`), seguindo boas práticas REST.

8. **Containerização**: Dockerfile otimizado com imagem base corporativa e configurações adequadas de JVM.

9. **Pipeline CI/CD**: Integração com Jenkins através de `jenkins.properties` e infraestrutura como código em `infra.yml`.

10. **Limitação Identificada**: A validação de contas stand-in está implementada de forma simplificada, sempre retornando `true`, o que pode indicar funcionalidade em desenvolvimento ou configuração externa necessária.