# Ficha Técnica do Sistema

## 1. Descrição Geral

O sistema **GDCF (Gestão de Débito em Conta de Financiamento)** é um componente core do Banco Votorantim responsável por gerenciar débitos automáticos em contas correntes de clientes que possuem contratos de financiamento. O sistema permite consultar, alterar e suspender débitos automáticos, tratar estornos, visualizar inconsistências e gerenciar o histórico de alterações de contas vinculadas aos contratos. Integra-se com sistemas legados e oferece serviços através de ESB (Enterprise Service Bus).

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| `AlterarContaServices` | Interface de serviços para alteração de contas de débito, consulta de contratos, parcelas e suspensões |
| `VisualizarSacServices` | Interface para consulta de contratos SAC, parcelas de débito e histórico de alterações |
| `TratarEstornoServices` | Interface para busca e tratamento de estornos de débitos |
| `VisualizarInconsistenciaServices` | Interface para visualização de inconsistências em débitos |
| `ContratoRefinService` | Interface para inserção de contratos de refinanciamento |
| `ContratoDebitoVO` | Value Object representando um contrato de débito |
| `ParcelaDebitoVO` | Value Object representando uma parcela de débito |
| `AlterarContaDTO` | DTO para transferência de dados de alteração de conta |
| `ContratoSacDTO` | DTO agregando dados de contratos para visualização SAC |
| `MotivoSuspensaoEnum` | Enumeração dos motivos de suspensão de débito |
| `StatusParcelaDebitoEnum` | Enumeração dos status possíveis de uma parcela de débito |

---

## 3. Tecnologias Utilizadas

- **Java** (linguagem principal)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework 2.0.2** (injeção de dependências e transações)
- **BV Framework** (framework proprietário do Banco Votorantim para datatypes, exceções e serviços ESB)
- **ESB (Enterprise Service Bus)** (integração e exposição de serviços)
- **JBoss 4.2.3** (servidor de aplicação)
- **Tomcat** (servidor web alternativo)
- **JavaMail 1.4** (envio de emails)

---

## 4. Principais Endpoints REST

não se aplica

**Observação:** O sistema utiliza serviços ESB anotados com `@ESBServiceAnnotation`, não endpoints REST convencionais. Os serviços são expostos através do catálogo ESB "BV-bvf-nnegocios-gdcf".

---

## 5. Principais Regras de Negócio

1. **Alteração de Conta de Débito**: Permite alterar dados bancários (banco, agência, conta) de contratos de débito, com validação de autorização
2. **Suspensão de Débito**: Contratos podem ter débitos suspensos por diversos motivos (quitação, fraude, cessão, cadastro inconsistente, troca de tipo de cobrança, contrato em cobrança)
3. **Autorização de Débito**: Validação de autorização prévia antes de permitir alterações em dados bancários
4. **Tratamento de Estornos**: Identificação e tratamento de débitos estornados, com atualização de data de estorno
5. **Gestão de Inconsistências**: Identificação e visualização de parcelas com inconsistências no processamento
6. **Histórico de Alterações**: Registro completo de todas as alterações realizadas em contas de débito
7. **Status de Parcelas**: Controle de ciclo de vida das parcelas (inicial, agendado, cancelado, erro, retornado, estorno)
8. **Integração com Contratos Refin**: Suporte para inserção de contratos de refinanciamento no sistema de débito

---

## 6. Relação entre Entidades

**Principais Entidades e Relacionamentos:**

- **ContratoDebito** (1) ←→ (N) **ParcelaDebito**: Um contrato possui múltiplas parcelas de débito
- **ContratoDebito** (N) ←→ (1) **MotivoSuspensao**: Contrato pode ter um motivo de suspensão associado
- **ParcelaDebito** (N) ←→ (1) **StatusParcelaDebito**: Cada parcela possui um status
- **ContratoDebito** (1) ←→ (N) **LogContratoDebito**: Histórico de alterações do contrato
- **ContratoDebito** (N) ←→ (1) **ModalidadeProduto**: Contrato vinculado a uma modalidade de produto

**Chaves Primárias:**
- ContratoDebito: `nuContrato` (Long)
- ParcelaDebito: `cdParcelaDebito` (Long)
- LogContratoDebito: `cdLogContratoDebito` (Integer)
- ModalidadeProduto: `cdProduto` + `cdModalidadeProduto` (chave composta)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONTRATO_DEBITO | tabela | SELECT | Consulta de contratos de débito |
| TB_PARCELA_DEBITO | tabela | SELECT | Consulta de parcelas de débito |
| TB_MOTIVO_SUSPENSAO | tabela | SELECT | Consulta de motivos de suspensão |
| TB_LOG_CONTRATO_DEBITO | tabela | SELECT | Consulta de histórico de alterações |
| TB_AUTORIZACAO_DEBITO_PRPSA_CNTRO | tabela | SELECT | Consulta de autorizações de débito |
| TB_MODALIDADE_PRODUTO | tabela | SELECT | Consulta de modalidades de produto |
| TB_COLABORADOR | tabela | SELECT | Consulta de código de colaborador por login |
| TB_PROPOSTA | tabela | SELECT | Consulta de número de proposta por contrato |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TB_CONTRATO_DEBITO | tabela | UPDATE | Atualização de dados bancários e status de débito |
| TB_PARCELA_DEBITO | tabela | UPDATE | Atualização de status e datas de parcelas |
| TB_PARCELA_DEBITO | tabela | INSERT | Inserção de novas parcelas de débito |
| TB_LOG_CONTRATO_DEBITO | tabela | INSERT | Registro de histórico de alterações |
| TB_AUTORIZACAO_DEBITO_PRPSA_CNTRO | tabela | UPDATE | Atualização de registros de autorização |
| TB_CONTRATO_DEBITO | tabela | INSERT | Inserção de novos contratos (refin) |

---

## 9. Arquivos Lidos e Gravados

não se aplica

**Observação:** O sistema não apresenta evidências de leitura/gravação direta de arquivos no código analisado. O processamento parece ser baseado em banco de dados e mensageria.

---

## 10. Filas Lidas

não se aplica

**Observação:** Não foram identificadas referências explícitas a consumo de filas (JMS, Kafka, RabbitMQ) no código analisado.

---

## 11. Filas Geradas

não se aplica

**Observação:** Não foram identificadas referências explícitas a publicação em filas no código analisado.

---

## 12. Integrações Externas

1. **Sistema de Gestão de Contratos (GDCC)**: Integração para consulta de dados de contratos e clientes
2. **Sistema SAC**: Integração para visualização de informações de atendimento
3. **Sistema de Autorização de Débito**: Validação de autorizações prévias
4. **Sistema Legado (Tools)**: Integração com sistema legado através de número de contrato legado
5. **ESB (Enterprise Service Bus)**: Exposição de serviços através do barramento corporativo

---

## 13. Avaliação da Qualidade do Código

**Nota:** 6/10

**Justificativa:**

**Pontos Positivos:**
- Uso de interfaces para definição de contratos de serviço
- Separação entre DTOs, VOs e exceções de negócio
- Uso de enums para valores fixos (status, motivos)
- Documentação JavaDoc presente em algumas classes
- Uso de anotações ESB para exposição de serviços

**Pontos Negativos:**
- Código com encoding ISO-8859-1, causando problemas de acentuação
- Nomenclatura inconsistente (mix de português e inglês)
- Falta de implementação concreta dos serviços (apenas interfaces)
- Algumas classes com responsabilidades não claras (ex: LogContratoDebitoVO não estende AbstractValueObject)
- Uso de tipos primitivos e wrappers de forma inconsistente
- Falta de validações explícitas nos DTOs
- Comentários em português misturados com código
- Dependência de framework legado (Spring 2.0.2, JBoss 4.2.3)

---

## 14. Observações Relevantes

1. **Sistema Legado**: O código indica integração com sistemas legados do Banco Votorantim, com referências a "Tools" e "SCC"
2. **Framework Proprietário**: Uso extensivo do BV Framework, framework proprietário do banco
3. **Versão Antiga**: Tecnologias desatualizadas (Spring 2.0.2, JBoss 4.2.3), indicando sistema legado
4. **Apenas Core**: O código analisado representa apenas a camada core (interfaces e datatypes), sem implementações concretas
5. **Transações Declarativas**: Uso de anotações ESB para controle transacional (REQUIRED, SUPPORTS)
6. **Encoding**: Problemas de encoding podem causar dificuldades na manutenção
7. **Propriedade Intelectual**: Código proprietário do Banco Votorantim com avisos de confidencialidade
8. **Build**: Sistema utiliza Maven com perfis específicos para deploy local em JBoss e Tomcat