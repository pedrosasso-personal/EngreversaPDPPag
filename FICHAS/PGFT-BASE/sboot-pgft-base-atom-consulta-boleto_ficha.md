# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **sboot-pgft-base-atom-consulta-boleto** é um serviço atômico desenvolvido em Spring Boot para gerenciar a consulta e persistência de informações de boletos de pagamento. O sistema consome mensagens de uma fila RabbitMQ contendo dados completos de boletos (incluindo informações de pagadores, beneficiários, cálculos, juros, multas, descontos e baixas) e persiste essas informações em um banco de dados Sybase. O componente atua como um consumidor de eventos de negócio relacionados a boletos de pagamento, realizando validações e transformações antes da persistência.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **Application** | Classe principal que inicializa a aplicação Spring Boot |
| **EventListener** | Listener que consome mensagens da fila RabbitMQ e aciona o serviço de persistência |
| **ConsultaBoletoService** | Serviço de domínio que orquestra a lógica de negócio para inserção de boletos |
| **ConsultaBoletoRepository** | Interface de repositório que define operações de persistência |
| **ConsultaBoletoRepositoryImpl** | Implementação do repositório usando JDBI para acesso ao banco de dados |
| **PagamentoBoletoValidator** | Classe responsável por validar e extrair dados dos objetos de boleto |
| **TituloCIPUtil** | Classe utilitária para manipulação de datas e valores de juros/multas |
| **Conversores** | Classe utilitária para conversão de códigos de barras e validação de CPF |
| **ConsultaBoletoConfiguration** | Configuração de beans do Spring |
| **JdbiConfiguration** | Configuração do JDBI para acesso ao banco de dados |
| **OpenApiConfiguration** | Configuração do Swagger para documentação da API |
| **TituloVoRowMapper** | Mapper para conversão de ResultSet em objetos de domínio |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework principal
- **Java 11** - Linguagem de programação
- **Maven** - Gerenciamento de dependências e build
- **JDBI 3.9.1** - Framework de acesso a dados
- **Sybase jConnect 16.3** - Driver JDBC para Sybase
- **RabbitMQ** - Message broker para consumo de eventos
- **Spring AMQP** - Integração com RabbitMQ
- **Lombok** - Redução de código boilerplate
- **Jackson** - Serialização/deserialização JSON
- **Swagger/Springfox 2.9.2** - Documentação de API
- **Micrometer/Prometheus** - Métricas e monitoramento
- **Logback** - Framework de logging
- **JUnit 5** - Testes unitários
- **Mockito** - Mocks para testes
- **Docker** - Containerização
- **Grafana** - Visualização de métricas

---

## 4. Principais Endpoints REST

não se aplica

*Observação: O sistema não expõe endpoints REST públicos. É um consumidor de mensagens assíncrono.*

---

## 5. Principais Regras de Negócio

1. **Consumo de Mensagens**: O sistema consome mensagens JSON da fila `events.business.PGFT-BASE.inserirBoletoPagamentoCompleto` contendo dados completos de boletos de pagamento.

2. **Validação de Dados**: Antes da persistência, todos os campos do boleto são validados, com tratamento de valores nulos e conversão de tipos.

3. **Persistência Incremental**: O sistema persiste o código de barras primeiro, consulta o ID gerado, e então persiste os dados relacionados (boleto, cálculos, juros, multas, descontos, baixas).

4. **Cálculo de Juros e Multas**: O sistema identifica a data futura mais próxima para aplicação de juros e multas, selecionando os valores apropriados das listas fornecidas.

5. **Tratamento de Pessoas**: O sistema diferencia e valida dados de pessoas físicas e jurídicas (beneficiários e pagadores), extraindo CPF/CNPJ, endereços e demais informações.

6. **Baixas Operacionais e Efetivas**: Suporta registro de baixas operacionais e efetivas de títulos, com suas respectivas datas e valores.

7. **Conversão de Datas**: Todas as datas são convertidas do formato ISO para o formato esperado pelo banco de dados.

8. **Logging de Processamento**: O sistema registra o tempo de processamento de cada boleto e erros detalhados em caso de falha.

9. **Tratamento de Erros**: Em caso de erro no processamento, a mensagem é logada mas não reprocessada, evitando loops infinitos.

10. **Validação de Código de Barras**: O sistema valida e converte códigos de barras, extraindo informações como banco, moeda, fator de vencimento e valor.

---

## 6. Relação entre Entidades

**Entidade Principal: BoletoPagamentoCompleto**
- Contém: BoletoPagamento (dados básicos do boleto)
- Contém: PercentualBoletoPagamento (percentuais mínimo/máximo)
- Contém: ListaCalculoTitulo (cálculos de valores)
- Contém: ListaTitulo (juros, multas, descontos)
- Contém: ListaBaixaTitulo (baixas operacionais)
- Contém: ListaBaixaEfetiva (baixas efetivas)

**BoletoPagamento**
- Relaciona-se com: PessoaCompleta (beneficiário original, beneficiário final, pagador)
- Contém: dados de identificação do título (número, referência, sequência)
- Contém: valores e datas (vencimento, valor do título)

**PessoaCompleta**
- Pode ser: PessoaFisica ou PessoaJuridica
- Contém: ListaDocumentoIdentificacao
- Contém: ListaEnderecoPessoa
- Contém: ListaTelefonePessoa
- Contém: outras listas de dados complementares

**Relacionamento com Banco de Dados:**
- TbSolicitacaoConsultaTitulo (tabela principal, gera CdSolicitacaoConsultaTitulo)
- TbRetornoConsultaTitulo (dados do boleto)
- TbCalculoTitulo (cálculos)
- TbJuroBoleto (juros)
- TbMultaBoleto (multas)
- TbDescontoBoleto (descontos)
- TbBaixaOperacionalTitulo (baixas operacionais)
- TbBaixaEfetivaTitulo (baixas efetivas)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSolicitacaoConsultaTitulo | tabela | SELECT | Consulta código de barras para verificar se já existe e obter o ID gerado |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbSolicitacaoConsultaTitulo | tabela | INSERT | Insere código de barras digitável do boleto |
| TbRetornoConsultaTitulo | tabela | INSERT | Insere dados completos do boleto de pagamento |
| TbCalculoTitulo | tabela | INSERT | Insere cálculos de valores do título |
| TbJuroBoleto | tabela | INSERT | Insere informações de juros do boleto |
| TbMultaBoleto | tabela | INSERT | Insere informações de multa do boleto |
| TbDescontoBoleto | tabela | INSERT | Insere informações de desconto do boleto |
| TbBaixaOperacionalTitulo | tabela | INSERT | Insere baixas operacionais do título |
| TbBaixaEfetivaTitulo | tabela | INSERT | Insere baixas efetivas do título |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| application.yml | leitura | Spring Boot | Arquivo de configuração da aplicação com profiles (local, des, qa, uat, prd) |
| logback-spring.xml | leitura | Logback | Configuração de logging em formato JSON para diferentes ambientes |
| *.sql | leitura | JDBI/ConsultaBoletoRepositoryImpl | Arquivos SQL para operações de banco de dados (consultas e inserções) |

---

## 10. Filas Lidas

**Fila:** `events.business.PGFT-BASE.inserirBoletoPagamentoCompleto`
- **Tecnologia:** RabbitMQ
- **Formato:** JSON
- **Listener:** EventListener.consumer()
- **Descrição:** Consome eventos de negócio contendo dados completos de boletos de pagamento para persistência no banco de dados

---

## 11. Filas Geradas

não se aplica

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| Banco de Dados Sybase (DBPGF_TES) | Database | Banco de dados principal para persistência de informações de boletos |
| RabbitMQ | Message Broker | Consumo de mensagens de eventos de negócio relacionados a boletos |
| Prometheus | Monitoring | Exportação de métricas da aplicação para monitoramento |
| Grafana | Visualization | Visualização de métricas e dashboards de monitoramento |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com arquitetura em camadas (domain, application)
- Uso adequado de frameworks modernos (Spring Boot, JDBI)
- Implementação de testes unitários
- Configuração de métricas e monitoramento
- Uso de Lombok para redução de boilerplate
- Documentação via Swagger

**Pontos Negativos:**
- **Classe ConsultaBoletoService muito extensa** (mais de 500 linhas) com múltiplas responsabilidades, violando o princípio de responsabilidade única
- **Classe PagamentoBoletoValidator extremamente longa** (mais de 1000 linhas) com métodos repetitivos e falta de abstração
- **Tratamento de erros genérico**: uso excessivo de `catch (Exception e)` sem tratamento específico
- **Validações com muita duplicação**: métodos de validação seguem padrão repetitivo que poderia ser abstraído
- **Falta de testes de integração** e cobertura de testes limitada
- **Acoplamento forte** entre camadas de serviço e validação
- **Código defensivo excessivo**: muitas validações de null que poderiam ser tratadas com Optional ou validações em nível de framework
- **Falta de constantes**: strings e números mágicos espalhados pelo código
- **Comentários em português misturados com código em inglês**
- **Métodos privados muito longos** na classe de serviço, dificultando manutenção

**Recomendações:**
1. Refatorar ConsultaBoletoService dividindo em serviços menores e mais coesos
2. Criar abstrações para validações repetitivas usando reflection ou anotações
3. Implementar tratamento de exceções específico por tipo de erro
4. Aumentar cobertura de testes e adicionar testes de integração
5. Extrair constantes e configurações para classes dedicadas
6. Aplicar padrões de design como Strategy ou Chain of Responsibility para validações

---

## 14. Observações Relevantes

1. **Ambiente Multi-Profile**: O sistema suporta múltiplos ambientes (local, des, qa, uat, prd) com configurações específicas de banco de dados e logging para cada um.

2. **Processamento Assíncrono**: Todo o processamento é assíncrono via mensageria, não há endpoints REST síncronos para inserção de boletos.

3. **Banco de Dados Legado**: Utiliza Sybase, um banco de dados menos comum atualmente, com nomenclatura de tabelas em português.

4. **Modelo de Dados Complexo**: O modelo de domínio é extremamente rico, com mais de 70 classes de entidades relacionadas a pessoas, endereços, documentos, etc.

5. **Infraestrutura como Código**: Possui configuração completa de infraestrutura (infra.yml) para deploy em OpenShift/Kubernetes.

6. **Monitoramento Completo**: Implementa stack completa de observabilidade com Prometheus, Grafana e métricas do Spring Actuator.

7. **Containerização**: Aplicação preparada para execução em containers Docker com Dockerfile otimizado.

8. **Dependência de Bibliotecas Internas**: Utiliza bibliotecas proprietárias do Banco Votorantim (arqt-base) para funcionalidades comuns.

9. **Processamento de Tempo**: O sistema registra e loga o tempo de processamento de cada boleto, indicando preocupação com performance.

10. **Tratamento de Datas Complexo**: Implementa lógica sofisticada para determinar datas futuras mais próximas para aplicação de juros e multas.

11. **Ausência de Rollback Explícito**: Não há evidências de tratamento transacional explícito ou rollback em caso de falha parcial na persistência.

12. **Configuração de Pools de Conexão**: Utiliza HikariCP para gerenciamento de conexões com o banco de dados, com métricas expostas.