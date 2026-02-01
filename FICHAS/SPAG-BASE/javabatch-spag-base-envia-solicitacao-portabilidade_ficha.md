# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java desenvolvido para processar solicitações de portabilidade de conta salário. O sistema consome mensagens de filas RabbitMQ contendo solicitações de portabilidade, valida se há cancelamentos pendentes, gera arquivos XML no formato APCS101 (padrão CIP - Câmara Interbancária de Pagamentos) e envia confirmações para filas de destino. O processamento segue o padrão Spring Batch com leitura, processamento e escrita de dados.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê mensagens de portabilidade da fila RabbitMQ |
| **ItemProcessor** | Transforma objetos Portabilidade em PortabilidadeArquivo com estrutura APCS |
| **ItemWriter** | Gera arquivo XML APCS101 e envia mensagens para fila de confirmação |
| **PortabilidadeIterator** | Gerencia iteração sobre mensagens, validando cancelamentos |
| **PortabilidadeRepository** | Gerencia comunicação com filas de solicitação de portabilidade |
| **PortabilidadeCancelamentoRepository** | Gerencia comunicação com filas de cancelamento |
| **ApcsEstrutura / Apcs101Impl** | Cria estrutura XML do arquivo APCS101 conforme schema CIP |
| **PortabilidadeMapper** | Converte entidades de domínio para estruturas APCS |
| **MyResumeStrategy** | Define estratégia de retomada do job em caso de falha |

---

## 3. Tecnologias Utilizadas

- **Java** (versão não especificada no código)
- **Spring Batch** (framework de processamento batch)
- **Spring AMQP / RabbitMQ** (mensageria)
- **Maven** (gerenciamento de dependências)
- **Jackson** (serialização/deserialização JSON)
- **Log4j** (logging)
- **JUnit / Mockito** (testes - não incluídos na análise)
- **BV Framework Batch** (framework proprietário baseado em Spring Batch)
- **XML/XSD** (geração e validação de arquivos)

---

## 4. Principais Endpoints REST

não se aplica

---

## 5. Principais Regras de Negócio

1. **Validação de Cancelamentos**: Antes de processar uma solicitação de portabilidade, o sistema verifica se existe cancelamento pendente para o mesmo número de controle do participante
2. **Geração de Arquivo APCS101**: Solicitações válidas são convertidas em arquivo XML seguindo o padrão APCS101 da CIP
3. **Controle de Emissão**: Cada arquivo gerado recebe um número de controle único do emissor
4. **Validação de Schema**: Arquivos XML gerados são validados contra o schema XSD APCS101 antes da finalização
5. **Transbordo de Cancelamentos**: Cancelamentos não processados são enviados para fila de transbordo
6. **Tipo de Conta**: O sistema diferencia tipos de conta (CC - Conta Corrente, PP - Poupança, PG - Conta Pagamento) e preenche campos específicos conforme o tipo
7. **Codificação UTF-16BE**: Arquivos XML são gerados em codificação UTF-16BE conforme especificação
8. **Nomenclatura de Arquivo**: Nome do arquivo segue padrão APCS101_[ISPB]_[AAAAMMDD]_[Sequencial]

---

## 6. Relação entre Entidades

**Portabilidade** (entidade principal)
- Contém: Cliente, BancoFolha, BancoDestino, Empregador, ControleArquivo
- Representa uma solicitação de portabilidade de conta salário

**Cliente**
- Dados pessoais: CPF, nome, telefone, email

**BancoFolha**
- Banco onde está a folha de pagamento atual
- Atributos: ISPB, CNPJ, código, razão social

**BancoDestino**
- Banco para onde será feita a portabilidade
- Atributos: ISPB, CNPJ, código, tipo conta, agência, número conta

**Empregador**
- Dados do empregador do cliente
- Atributos: CPF/CNPJ, razão social, tipo pessoa

**ControleArquivo**
- Metadados do arquivo gerado
- Atributos: nome arquivo, data envio CIP, número controle emissor

**PortabilidadeCancelamento**
- Representa cancelamento de portabilidade
- Vinculada à Portabilidade pelo número de controle do participante

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
| APCS101_[ISPB]_[DATA]_[SEQ] | Gravação | ItemWriter / ApcsEstrutura | Arquivo XML com solicitações de portabilidade no formato APCS101 |
| APCS101.xsd | Leitura | ApcsEstrutura (método validateXml) | Schema XSD para validação do arquivo gerado |
| APCSTIPOS.xsd | Leitura | Referenciado no APCS101.xsd | Schema com definições de tipos globais |
| job-resources.xml | Leitura | Spring Context (DES/UAT/PRD) | Configurações de conexão RabbitMQ por ambiente |
| job-definitions.xml | Leitura | Spring Batch | Definições do job batch e beans |
| log4j.xml | Leitura | Log4j | Configurações de logging |

---

## 10. Filas Lidas

| Nome da Fila | Tecnologia | Classe Responsável | Descrição |
|--------------|------------|-------------------|-----------|
| events.business.SPAG-BASE.solicitacao.portabilidade.cip | RabbitMQ | PortabilidadeIterator | Fila de solicitações de portabilidade de conta salário |
| events.business.SPAG-BASE.cancelamento.portabilidade.interna | RabbitMQ | PortabilidadeIterator | Fila de cancelamentos de portabilidade |

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Routing Key | Classe Responsável | Descrição |
|-----------------------|-------------|-------------------|-----------|
| events.business.portabilidade | SPAG.solicitacaoArqPortabilidade | PortabilidadeRepository | Confirmação de solicitação processada com dados do arquivo gerado |
| events.business.portabilidade | SPAG.confCancelamentoPortabilidadeInterna | PortabilidadeCancelamentoRepository | Confirmação de cancelamento processado |
| events.business.portabilidade | SPAG.transbordoPortabilidadeInterna | PortabilidadeCancelamentoRepository | Cancelamentos não processados (transbordo) |

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **RabbitMQ** | Mensageria | Sistema de filas para comunicação assíncrona. Configurações por ambiente (DES: 10.39.216.217, UAT: 10.39.88.128, PRD: 10.39.48.27) |
| **CIP (Câmara Interbancária de Pagamentos)** | Arquivo XML | Destinatário final dos arquivos APCS101 gerados (ISPB: 02992335) |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso adequado do padrão Spring Batch (Reader/Processor/Writer)
- Uso de mappers para conversão de dados
- Validação de XML contra schema XSD
- Tratamento de exceções customizado com códigos de erro
- Uso de logging adequado
- Configurações externalizadas por ambiente

**Pontos Negativos:**
- **Lógica complexa no Iterator**: A classe `PortabilidadeIterator` mistura responsabilidades de leitura de filas e validação de cancelamentos
- **Código comentado**: Presença de código comentado em várias classes (ex: telefone do cliente)
- **Hardcoded values**: Valores fixos como ISPBs, nomes de filas e routing keys espalhados pelo código
- **Falta de constantes**: Strings mágicas em vários locais
- **Método `limitaTamanho` mal posicionado**: Deveria estar em classe utilitária, não em `GrupoFolhaPagamento`
- **Tratamento de encoding complexo**: Conversão UTF-16BE poderia ser simplificada
- **Falta de documentação**: Javadoc ausente ou incompleto na maioria das classes
- **Segurança**: Senhas em texto claro nos arquivos de configuração (job-resources.xml)
- **Acoplamento**: Forte dependência do framework BV proprietário

---

## 14. Observações Relevantes

1. **ISPB Votorantim**: 59588111 (emissor dos arquivos)
2. **ISPB CIP**: 02992335 (destinatário dos arquivos)
3. **Versão do Schema**: APCS101 versão 1.3.1
4. **Framework Proprietário**: Sistema utiliza framework BV Sistemas (bv-framework-batch.standalone) versão 13.0.19
5. **Processamento Sequencial**: O sistema processa uma mensagem por vez, validando cancelamentos antes de cada processamento
6. **Estratégia de Falha**: Em caso de erro, o job não retoma automaticamente (MyResumeStrategy retorna false)
7. **Limitação de Tamanho**: Denominação social do empregador é limitada a 50 caracteres
8. **Campos Opcionais**: Telefone e código de autenticação do beneficiário são opcionais no arquivo XML
9. **Validação de Tipo de Conta**: Sistema valida e diferencia preenchimento de campos conforme tipo de conta (CC/PP vs PG)
10. **Ambiente de Execução**: Sistema preparado para 3 ambientes (DES, UAT, PRD) com configurações específicas de RabbitMQ