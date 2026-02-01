# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por consultar transações de débitos veiculares pagas via conta corrente que ainda não possuem comprovante fiscal gerado, e publicar essas transações em uma fila RabbitMQ para processamento posterior. O sistema opera em lotes de até 500 registros por execução, consultando o banco de dados MySQL e enviando as informações para uma fila de mensageria para geração de comprovantes fiscais.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Consulta transações de débitos veiculares pagos via conta corrente sem comprovante fiscal no banco de dados MySQL |
| **ItemProcessor** | Processa os itens lidos (atualmente apenas repassa os dados sem transformação) |
| **ItemWriter** | Publica as transações na fila RabbitMQ para processamento de comprovantes fiscais |
| **ConsultaComprovanteFiscal** | Entidade de domínio que representa os dados de uma transação de débito veicular |
| **DebitosVeicularesRepositoryImpl** | Implementação do repositório para consulta de transações no banco MySQL |
| **FilaTransacaoRepositoryImpl** | Implementação do repositório para publicação de mensagens na fila RabbitMQ |
| **MyResumeStrategy** | Estratégia de tratamento de erros do framework batch (atualmente configurada para não retomar em caso de erro) |
| **TransacaoRowMapper** | Mapeador de ResultSet para objeto ConsultaComprovanteFiscal |

---

## 3. Tecnologias Utilizadas

- **Java 8** (JDK 1.8.0_202)
- **Maven** - Gerenciamento de dependências e build
- **Spring Framework** - Injeção de dependências e configuração
- **Spring AMQP / Spring Rabbit** - Integração com RabbitMQ
- **Framework BV Batch** (br.com.bvsistemas.framework.batch) - Framework proprietário para processamento batch
- **MySQL 8.0.22** - Banco de dados relacional
- **Bitronix** - Gerenciador de transações JTA
- **RabbitMQ** - Message broker para filas de mensagens
- **BVCrypto** - Biblioteca proprietária para criptografia de senhas
- **Jackson 2.13.3** - Serialização/deserialização JSON
- **Log4j** - Framework de logging
- **JUnit** - Testes unitários

---

## 4. Principais Endpoints REST

Não se aplica. Este é um sistema batch que não expõe endpoints REST.

---

## 5. Principais Regras de Negócio

1. **Seleção de Transações**: Consulta apenas transações com status "PAGO" (código 1) e forma de pagamento "CONTA_CORRENTE" (código 2)
2. **Filtro de Comprovantes**: Seleciona apenas transações que ainda não possuem comprovante fiscal gerado (LEFT JOIN com TbComprovanteFiscal IS NULL)
3. **Limite de Processamento**: Processa no máximo 500 transações por execução (LIMIT 500)
4. **Tipos de Débito**: Suporta múltiplos tipos de débitos veiculares: DPVAT, IPVA, Licenciamento, Multa e RENAINF
5. **Tratamento de Erros**: Em caso de erro, o sistema realiza rollback da transação e finaliza o processamento (não retoma)
6. **Publicação em Fila**: Cada transação é convertida para JSON e publicada individualmente na fila RabbitMQ
7. **Confirmação de Publicação**: Utiliza publisher confirms e publisher returns para garantir entrega das mensagens

---

## 6. Relação entre Entidades

**ConsultaComprovanteFiscal** (Entidade Principal):
- Representa uma transação de débito veicular
- Atributos: cpfCnpj, renavam, tipoDebito, codigoBanco, vrPagamento, dtQuitacao, anoExercicioDpvat, anoExercicioIpva, anoExercicioLicenciamento, cdTransacaoDebito

**Relacionamentos no Banco de Dados** (conforme query SQL):
- TbTransacaoDebito (1) → (1) TbConsultaRenavam
- TbConsultaRenavam (1) → (1) TbVeiculo
- TbTransacaoDebito (1) → (0..1) TbComprovanteFiscal
- TbTransacaoDebito (1) → (0..1) TbDebitoDpvat
- TbTransacaoDebito (1) → (0..1) TbDebitoIPVA
- TbTransacaoDebito (1) → (0..1) TbDebitoLicenciamento
- TbTransacaoDebito (1) → (0..1) TbDebitoMulta
- TbTransacaoDebito (1) → (0..1) TbDebitoRenainf

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbTransacaoDebito | Tabela | SELECT | Tabela principal de transações de débitos veiculares |
| TbConsultaRenavam | Tabela | SELECT | Informações de consultas realizadas por RENAVAM |
| TbVeiculo | Tabela | SELECT | Dados cadastrais dos veículos (CPF/CNPJ, RENAVAM) |
| TbComprovanteFiscal | Tabela | SELECT | Comprovantes fiscais já gerados (usado para filtro) |
| TbDebitoDpvat | Tabela | SELECT | Débitos de DPVAT com ano de exercício |
| TbDebitoIPVA | Tabela | SELECT | Débitos de IPVA com ano de exercício |
| TbDebitoLicenciamento | Tabela | SELECT | Débitos de Licenciamento com ano de exercício |
| TbDebitoMulta | Tabela | SELECT | Débitos de Multas |
| TbDebitoRenainf | Tabela | SELECT | Débitos de RENAINF |

---

## 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. O sistema apenas realiza consultas (SELECT), não executa operações de INSERT, UPDATE ou DELETE no banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| DebitosVeicularesRepositoryImpl-sql.xml | Leitura | SqlUtil / DebitosVeicularesRepositoryImpl | Arquivo XML contendo queries SQL parametrizadas |
| robo.log | Gravação | Log4j (RollingFileAppender) | Log principal da aplicação com rotação de 2MB e 5 backups |
| statistics-{executionId}.log | Gravação | BvDailyRollingFileAppender | Log de estatísticas do framework batch com rotação diária |
| btm1.tlog / btm2.tlog | Gravação | Bitronix Transaction Manager | Arquivos de log de transações do Bitronix (removidos ao final) |

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas, apenas publica.

---

## 11. Filas Geradas

| Nome da Fila/Exchange | Tipo | Descrição |
|----------------------|------|-----------|
| **Exchange**: ex.ccbd.debitos.veiculares.comprovantes | Exchange RabbitMQ | Exchange para roteamento de mensagens de comprovantes fiscais |
| **Routing Key**: ccbd.debitos.veiculares.comprovantes | Routing Key | Chave de roteamento para direcionar mensagens ao destino correto |

**Configurações por Ambiente**:
- **DES**: Host 10.179.172.71, porta 5672, usuário _ccbd_des
- **UAT**: Host 10.183.100.70, porta 5672, usuário _ccbd_uat
- **PRD**: Host 10.39.49.197, porta 5672, usuário _ccbd

**Formato da Mensagem**: JSON (via JsonMessageConverter) contendo objeto ConsultaComprovanteFiscal

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|----------------|------|-----------|
| **MySQL CCBDDebitoVeicular** | Banco de Dados | Banco de dados principal contendo informações de débitos veiculares e transações |
| **RabbitMQ** | Message Broker | Sistema de mensageria para publicação de transações que necessitam geração de comprovante fiscal |
| **BVCrypto** | Serviço de Segurança | Biblioteca proprietária para descriptografia de senhas de acesso ao banco e RabbitMQ |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de interfaces e implementações
- Uso adequado de padrões de projeto (Repository, Strategy)
- Configuração externalizada por ambiente (DES/UAT/PRD)
- Tratamento de exceções com códigos de erro específicos
- Uso de framework batch estruturado
- Logging adequado em pontos críticos

**Pontos Negativos:**
- ItemProcessor não realiza nenhum processamento (método vazio), questionável sua necessidade
- Falta de documentação JavaDoc nas classes e métodos
- Senhas criptografadas hardcoded nos arquivos de configuração (mesmo criptografadas)
- Query SQL complexa embutida em arquivo XML, dificultando manutenção
- Falta de testes unitários (apenas teste de integração básico)
- Classe MyResumeStrategy com comentários em português e implementação mínima
- Uso de caracteres especiais com encoding incorreto em alguns comentários
- Falta de validações nos construtores e setters
- Ausência de constantes para valores mágicos (ex: "500" no LIMIT)
- Configuração de pool de conexões muito restritiva (maxPoolSize=1 em alguns ambientes)

---

## 14. Observações Relevantes

1. **Execução Agendada**: O sistema é executado via scripts batch (.bat para Windows, .sh para Linux) com parâmetro de executionId
2. **Gerenciamento de Memória**: Configurado com heap de 512MB (-Xms512M -Xmx512M)
3. **Execução Concorrente**: Permite execução concorrente (--concurrentExecution=true)
4. **Versionamento**: Versão atual 0.2.0, gerenciado via Git
5. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas (versão 13.0.19)
6. **Ambientes**: Possui configurações específicas para 3 ambientes (DES, UAT, PRD)
7. **Limitação de Processamento**: Processa apenas 500 registros por execução, necessitando múltiplas execuções para grandes volumes
8. **Dependência de Token**: Requer variável de ambiente BV_CRYPTO_TOKEN para descriptografia de senhas
9. **Cleanup Automático**: Remove arquivos de log do Bitronix ao final da execução
10. **Integração Jenkins**: Possui arquivo jenkins.properties para integração com pipeline CI/CD