# Ficha Técnica do Sistema

## 1. Descrição Geral

Sistema batch Java responsável por gerar arquivos de extrato bancário no formato CNAB 240 para o Banco Rendimento. O sistema consulta movimentações de débitos veiculares (IPVA, licenciamento, multas, etc.) em um período específico e gera arquivos padronizados contendo header, lotes de detalhes e trailers, seguindo o layout CNAB 240 do Itaú/Banco Rendimento.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **ItemReader** | Lê os dados de movimentações bancárias do banco de dados MySQL, calculando o período de consulta baseado em dias úteis |
| **ItemProcessor** | Processa os registros lidos (atualmente apenas repassa os dados sem transformação) |
| **ItemWriter** | Gera o arquivo CNAB 240 com os movimentos processados, incluindo headers, detalhes e trailers |
| **ExtratoServiceImpl** | Orquestra a geração do arquivo CNAB 240, mapeando dados para os VOs correspondentes |
| **RegraPagamentoParceiroImpl** | Calcula as datas de movimento considerando dias úteis e feriados |
| **DebitosVeicularesRepositoryImpl** | Repositório para consulta de movimentações de débitos veiculares no MySQL |
| **DataUtilRepositoryImpl** | Repositório para consulta de feriados e dias úteis via API REST e banco Sybase |
| **ItauCNAB240Helper** | Helper para gravação do arquivo CNAB 240 usando a biblioteca Flatworm |
| **DateUtilImpl** | Utilitário para manipulação e conversão de datas |
| **RestClient** | Cliente HTTP para consumo de APIs REST com suporte a TLS 1.2 |

---

## 3. Tecnologias Utilizadas

- **Java 8** (JDK 1.8.0_202)
- **Maven** (gerenciamento de dependências e build)
- **Spring Framework 2.0** (injeção de dependências e configuração)
- **BV Framework Batch** (framework proprietário para processamento batch)
- **MySQL 8.0.22** (banco de dados principal - CCBDDebitoVeicular)
- **Sybase ASE** (banco de dados DBGLOBAL para consulta de feriados)
- **Bitronix** (gerenciador de transações JTA)
- **Flatworm 2.0.1** (geração de arquivos de layout fixo)
- **Apache HttpClient** (cliente HTTP)
- **BouncyCastle** (criptografia e suporte TLS)
- **Gson 2.8.2** (serialização/deserialização JSON)
- **JUnit 4** e **Mockito 2.28.2** (testes unitários)
- **Log4j** (logging)

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | https://sboot-dcor-base-atom-dias-uteis.appdes.bvnet.bv/v1/corporativo/calendario/dias-uteis/{data}/ultimo?codigoPraca=1 | RestClient | Consulta o último dia útil anterior a uma data específica |

---

## 5. Principais Regras de Negócio

1. **Cálculo de Período de Movimentação**: O sistema calcula automaticamente o período de consulta baseado no último dia útil e no dia útil anterior, considerando feriados e finais de semana.

2. **Mapeamento de Tipos de Operação**: As operações são classificadas em tipos específicos (Multa, IPVA, Licenciamento, TED, Renainf) através do enum `TipoOperacaoEnum`, com fallback para operações não mapeadas.

3. **Geração de CNAB 240**: O arquivo segue o padrão CNAB 240 com estrutura hierárquica: Header do Arquivo → Header de Lote → Detalhes → Trailer de Lote → Trailer do Arquivo.

4. **Dados Bancários Específicos**: O sistema trabalha com contas específicas do Banco Rendimento (código 633) e BVSA (código 413), com CNPJs e contas pré-configurados.

5. **Controle de Sequenciais**: Mantém controle de sequenciais gerais e por lote para garantir integridade do arquivo CNAB.

6. **Remoção de Caracteres Especiais**: Aplica normalização de strings removendo acentos e caracteres especiais dos dados antes da gravação no arquivo.

7. **Formatação de Valores**: Valores monetários são formatados com 18 posições, sendo 2 decimais implícitos.

---

## 6. Relação entre Entidades

**ExtratoDomain** (entidade principal de movimentação):
- Contém: data de pagamento, hora, valor total, descrição do histórico, documento de identificação, tipo de operação

**BaseVO** (dados base da conta):
- Contém: tipo de inscrição, CPF/CNPJ, código da empresa, agência, conta, nome da empresa, data, banco COMPE
- É herdado por: ArquivoHeaderVO, LoteHeaderVO, LoteTrailerVO

**ArquivoHeaderVO**: Header do arquivo CNAB (herda BaseVO)

**LoteHeaderVO**: Header de lote com saldo inicial (herda BaseVO)

**LoteDetalheVO**: Detalhe de movimentação no lote (herda BaseVO)
- Adiciona: dados do lançamento, valores, histórico, dados do titular

**LoteTrailerVO**: Trailer de lote com totalizadores (herda BaseVO)
- Adiciona: saldo final, totais de débito/crédito, quantidade de registros

**ArquivoTrailerVO**: Trailer do arquivo com totalizadores gerais

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbExtratoPagamento | tabela | SELECT | Tabela de movimentações de pagamentos de débitos veiculares no MySQL (CCBDDebitoVeicular) |
| TbFeriado | tabela | SELECT | Tabela de feriados no Sybase (DBGLOBAL) para cálculo de dias úteis |

---

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| ExtratoBancoRendimento.dat | gravação | ExtratoServiceImpl / ItauCNAB240Helper | Arquivo CNAB 240 gerado com os extratos de movimentação, gravado em ./arquivo/processados/ |
| itauCNAB240.xml | leitura | ItauCNAB240Helper | Arquivo XML de configuração do layout CNAB 240 usado pela biblioteca Flatworm |
| DataUtilRepositoryImpl-sql.xml | leitura | SqlUtil | Arquivo XML contendo queries SQL para consulta de feriados |
| DebitosVeicularesRepositoryImpl-sql.xml | leitura | SqlUtil | Arquivo XML contendo queries SQL para consulta de movimentações |
| job-resources.xml | leitura | Spring Framework | Arquivo de configuração de datasources e recursos do job |
| job-definitions.xml | leitura | Spring Framework | Arquivo de definição do job batch e seus componentes |
| log4j.properties / log4j.xml | leitura | Log4j | Arquivos de configuração de logging |
| robo.log | gravação | Log4j | Arquivo de log da aplicação |
| statistics-{executionId}.log | gravação | BvDailyRollingFileAppender | Arquivo de estatísticas de execução do batch |

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
| API Dias Úteis (sboot-dcor-base-atom-dias-uteis) | REST API | Serviço REST para consulta de dias úteis e feriados, usado para calcular o período de movimentação |
| MySQL CCBDDebitoVeicular | Banco de Dados | Banco de dados principal contendo as movimentações de débitos veiculares |
| Sybase DBGLOBAL | Banco de Dados | Banco de dados corporativo para consulta de feriados e dias úteis |

---

## 13. Avaliação da Qualidade do Código

**Nota: 6/10**

**Justificativa:**

**Pontos Positivos:**
- Boa separação de responsabilidades com uso de interfaces e implementações
- Uso adequado de enums para constantes e mapeamentos
- Presença de testes unitários (embora básicos)
- Configuração externalizada via Spring
- Uso de padrões de projeto (Repository, Service)

**Pontos Negativos:**
- **Código comentado e não utilizado**: Presença de código comentado em várias classes (ex: DadosContaBVRendimentoEnum)
- **Hardcoding excessivo**: Muitos valores fixos em código (listas de CPF/CNPJ, contas, códigos)
- **Falta de tratamento de exceções**: Muitos métodos apenas propagam exceções genéricas
- **Documentação insuficiente**: Javadoc presente mas incompleto, muitos comentários em português misturados
- **Complexidade desnecessária**: Classe ExtratoServiceImpl com método muito extenso (gerarExtrato)
- **Código morto**: ContaCorrenteRepositoryImpl implementa interface mas todos os métodos retornam null
- **Mistura de responsabilidades**: ItemWriter acumula lógica de negócio que deveria estar no Service
- **Falta de validações**: Pouca validação de entrada de dados
- **Logs inadequados**: Uso de System.out em alguns lugares, mensagens de log pouco informativas
- **Testes fracos**: Cobertura de testes baixa e mocks não testam cenários de erro

---

## 14. Observações Relevantes

1. **Ambientes**: O sistema possui configurações específicas para ambientes DES (desenvolvimento) e UAT (homologação), com credenciais e URLs diferentes.

2. **Segurança**: Utiliza criptografia BVCrypto para senhas de banco de dados, mas as chaves estão expostas nos XMLs de configuração.

3. **Execução**: O job pode ser executado via linha de comando (.bat para Windows, .sh para Linux) recebendo como parâmetros o executionId e a data de movimento.

4. **Parâmetro Opcional**: O parâmetro `dataMovimento` é opcional; se não informado, o sistema usa a data atual.

5. **Limitação de Bancos**: O sistema está preparado para gerar arquivos apenas para BVSA (código 436/413), embora tenha referências ao Banco Votorantim.

6. **Dependência de API Externa**: O sistema depende de uma API REST para cálculo de dias úteis, o que pode ser um ponto de falha.

7. **Framework Proprietário**: Utiliza framework batch proprietário da BV Sistemas, o que pode dificultar manutenção por equipes externas.

8. **Versões Antigas**: Utiliza versões antigas de bibliotecas (Spring 2.0, Java 8), o que pode representar riscos de segurança e falta de suporte.

9. **Transações**: Utiliza Bitronix para gerenciamento de transações distribuídas, mas com `allowLocalTransactions=true` e `automaticEnlistingEnabled=false`.

10. **Nomenclatura**: Alguns nomes de classes e métodos estão em português, outros em inglês, faltando padronização.