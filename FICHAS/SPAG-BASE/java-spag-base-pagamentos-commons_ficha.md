---
## Ficha Técnica do Sistema

### 1. Descrição Geral
Sistema de processamento de arquivos CNAB (Centro Nacional de Automação Bancária) no padrão 240 posições, específico para o layout Votorantim. O sistema realiza leitura, validação, conversão e geração de arquivos CNAB para processamento de pagamentos diversos (DOC, TED, boletos, tributos, salários, etc). Atua como biblioteca comum (commons) para a esteira de pagamentos, fornecendo estruturas de dados, validadores, conversores e utilitários para manipulação de arquivos de remessa e retorno bancário.

### 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **CnabLayoutReader** | Parse de arquivos CNAB para POJOs, detecção de charset, validação de encoding ISO-8859-1 |
| **CnabLayoutWritter** | Geração de strings CNAB a partir de lista de POJOs via FFPojo |
| **CnabLayoutValidator** | Validação de estrutura, layout, campos, tipos, domínios, formatos e totalizadores CNAB |
| **CnabLayoutVotorantimValidator** | Validador específico para layout Votorantim, identifica e valida segmentos A/B/Z/J/J52/J53/C |
| **CnabLayoutVotorantimObjectTranslator** | Tradutor bidirecional entre DTOs de domínio e POJOs CNAB, calcula totalizadores, gera linha digitável |
| **CnabLayoutHelper** | Singleton que carrega layout XML CNAB via XStream, configura aliases para classes DTO |
| **CnabUtil** | Utilitários para processamento: descompactação GZIP, detecção charset, parse linha-a-linha |
| **PagamentoUtil** | Utilitários de conversão de datas e formatação de números para pagamentos |
| **VotorantimMoneyDecorator** | Decorator FFPojo para conversão de valores monetários (divide por 100, 2 decimais) |
| **VotorantimDateDecorator** | Decorator FFPojo para conversão de datas formato ddMMyyyy |
| **VotorantimDateTimeDecorator** | Decorator FFPojo para conversão de datetime formato ddMMyyyyHHmmss |
| **CnabLayoutPojoAbstractClass** | Classe base para POJOs CNAB, identifica TipoRegistro por códigos |
| **DicionarioPagamento** | Classe central da biblioteca (mencionada no README) |

### 3. Tecnologias Utilizadas

- **Java 1.6/1.7** (IBM JDK 7)
- **Maven** (gerenciamento de dependências e build)
- **FFPojo 0.1-parser** (parsing de arquivos posicionais)
- **XStream** (serialização/deserialização XML para configuração de layouts)
- **Apache Commons Lang3** (utilitários)
- **JUnit** (testes unitários)
- **PowerMock** (mocks para testes)
- **BV Framework Commons Datatypes** (framework interno Banco Votorantim)
- **BV Apoio Operação Core** (biblioteca interna)
- **Jenkins** (CI/CD)
- **Padrão CNAB 240 posições** (especificação bancária)

### 4. Principais Endpoints REST

Não se aplica. Esta é uma biblioteca comum (commons) que não expõe endpoints REST diretamente. Segundo o README, a biblioteca é consumida por 15+ serviços REST da esteira de pagamentos:

- Validação de solicitação
- Processamento CIP
- Cálculo de valores
- Consulta de saldo
- Agendamento
- Débito/Crédito em conta
- Transferências
- Baixa operacional
- Processamento CNAB retorno
- Notificações (ITP, PGFT, NCSS)
- Gestão de ocorrências

**URLs base dos consumidores (DEV):** appbvdes.bvnet.bv

### 5. Principais Regras de Negócio

1. **Validação de Layout CNAB 240**: Estrutura de 240 caracteres por linha, validação de posições, tipos de dados, domínios e formatos
2. **Conversão Monetária**: Valores monetários em CNAB são armazenados sem vírgula (multiplicados por 100), conversão automática para BigDecimal com 2 decimais
3. **Validação de Sequências**: Controle de sequência de registros (header arquivo → header lote → detalhes → trailer lote → trailer arquivo)
4. **Totalizadores**: Cálculo e validação de totalizadores de quantidade de registros e valores nos trailers
5. **Geração de Linha Digitável**: Cálculo de linha digitável para boletos bancários
6. **Validação de CPF/CNPJ**: Validação de formato e dígitos verificadores
7. **Interoperabilidade Segmento C**: Validação específica para segmento C (boletos)
8. **Tipos de Operação**: Diferenciação entre operações de Crédito, Débito, Extrato, Remessa e Retorno
9. **Formas de Pagamento**: Suporte a 28+ tipos de pagamento (DOC, TED, boleto, tributos, salário, etc)
10. **Códigos de Ocorrência**: Mapeamento de 366+ códigos de ocorrências de pagamento
11. **Sistemas de Origem**: Identificação de 78+ sistemas origem de lançamentos
12. **Processamento de Arquivos**: Suporte a arquivos compactados GZIP, detecção automática de charset (UTF-8/ISO-8859-1)
13. **Validação de Datas**: Formato lenient=false para datas, garantindo validação rigorosa
14. **Câmaras de Compensação**: Mapeamento de câmaras (TED=18, DOC=700)
15. **Fluxo de Retorno**: 26 pontos de identificação de retorno no fluxo de pagamento

### 6. Relação entre Entidades

**Estrutura Hierárquica CNAB:**
```
CnabArquivoDTO (Arquivo CNAB)
├── CnabLayoutVotorantimHeaderArquivoDTO (Header do Arquivo)
├── List<CnabArquivoLoteDTO> (Lotes)
│   ├── CnabLayoutVotorantimHeaderLoteDTO (Header do Lote)
│   ├── List<CnabArquivoDetalheDTO> (Detalhes)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoADTO (Segmento A - Crédito)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoBDTO (Segmento B - Complemento A)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoCDTO (Segmento C - Boleto)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoZDTO (Segmento Z - Complemento)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoJDTO (Segmento J - Tributos)
│   │   ├── CnabLayoutVotorantimDetalheSegmentoJ52DTO (Segmento J52 - DARF)
│   │   └── CnabLayoutVotorantimDetalheSegmentoJ53DTO (Segmento J53 - GPS)
│   └── CnabLayoutVotorantimTraillerLoteDTO (Trailer do Lote)
└── CnabLayoutVotorantimTraillerArquivoDTO (Trailer do Arquivo)
```

**Relacionamentos de Domínio:**
- **CnabArquivoDTO** 1:N **CnabArquivoLoteDTO**
- **CnabArquivoLoteDTO** 1:N **CnabArquivoDetalheDTO**
- **CnabArquivoDetalheDTO** 1:1 **Segmento específico** (A, B, C, Z, J, J52, J53)
- **CnabArquivoDTO** 1:1 **SituacaoCnabArquivoValidadoEnum** (VALIDADO/DUPLICADO/ERROLAYOUT)
- **CnabArquivoDetalheDTO** N:1 **TipoSegmentoDetalheEnum**
- **CnabArquivoDetalheDTO** N:1 **StatusPosicaoConsolidadaEnum**

### 7. Estruturas de Banco de Dados Lidas

Não se aplica. A biblioteca trabalha exclusivamente com arquivos CNAB e não realiza acesso direto a banco de dados. O acesso a dados é responsabilidade dos serviços consumidores da biblioteca.

### 8. Estruturas de Banco de Dados Atualizadas

Não se aplica. A biblioteca não realiza operações de escrita em banco de dados diretamente.

### 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Arquivos CNAB 240 (.txt, .rem, .ret) | Leitura | CnabLayoutReader, CnabUtil | Arquivos de remessa e retorno bancário no padrão CNAB 240 posições |
| Arquivos CNAB compactados (.gz) | Leitura | CnabUtil.descompactarArquivo() | Arquivos CNAB compactados em formato GZIP |
| layout_cnab_votorantim.xml | Leitura | CnabLayoutHelper | Arquivo XML de configuração do layout CNAB Votorantim |
| Arquivos CNAB gerados | Gravação | CnabLayoutWritter | Geração de strings CNAB formatadas (240 caracteres por linha) |

### 10. Filas Lidas

Não se aplica. A biblioteca não consome mensagens de filas diretamente. O processamento de filas é responsabilidade dos serviços consumidores.

### 11. Filas Geradas

Não se aplica. A biblioteca não publica mensagens em filas diretamente.

### 12. Integrações Externas

Não se aplica diretamente. A biblioteca é um componente comum (commons) que não realiza integrações externas por si só. As integrações são realizadas pelos 15+ serviços REST que consomem esta biblioteca, incluindo:

- **Sistemas Legados**: NCSS, PGFT, ITP (notificações)
- **CIP** (Câmara Interbancária de Pagamentos)
- **SPB** (Sistema de Pagamentos Brasileiro)
- **Sistemas Internos**: TARF, GDCC, SPBB, COBR, SEMP, RECT, SAPR, GRNT, PGFO, INTB

### 13. Avaliação da Qualidade do Código

**Nota: 7/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem estruturada com separação clara de responsabilidades (readers, writers, validators, translators)
- Uso adequado de padrões de projeto (Decorator, Singleton, Strategy)
- Enumerações bem definidas para domínios de negócio (366+ códigos de ocorrência, 78+ sistemas origem)
- Boa cobertura de testes com mocks estruturados
- Uso de annotations para mapeamento posicional (FFPojo)
- Tratamento de exceções customizadas
- Documentação técnica presente (README, XML de layout)
- Validações rigorosas de formato e domínio

**Pontos de Melhoria:**
- Uso de Java 1.6/1.7 (versões obsoletas e sem suporte)
- Algumas classes muito extensas (CnabLayoutVotorantimObjectTranslator, validadores)
- Acoplamento com frameworks internos específicos do Banco Votorantim
- Falta de documentação inline (JavaDoc) em algumas classes críticas
- Uso de SimpleDateFormat (não thread-safe) ao invés de DateTimeFormatter
- Algumas validações poderiam ser extraídas para classes especializadas
- Nomenclatura mista (português/inglês) em alguns pontos

O código demonstra maturidade e experiência no domínio bancário, com tratamento robusto de casos de borda, mas poderia se beneficiar de refatoração para versões mais modernas de Java e melhor modularização de algumas classes complexas.

### 14. Observações Relevantes

1. **Versão do Componente**: 0.20.25 (biblioteca em evolução ativa)

2. **Padrão CNAB 240**: Sistema implementa especificamente o padrão CNAB de 240 posições, que é diferente do CNAB 400 (padrão mais antigo)

3. **Layout Específico Votorantim**: Embora exista enum para layout Itaú (TipoLayoutEnum), a implementação atual é específica para o layout Votorantim

4. **Charset e Encoding**: Sistema trata especificamente problemas de encoding, removendo BOM UTF-8 e validando ISO-8859-1, comum em arquivos bancários legados

5. **Segmentos CNAB**: Suporte completo aos segmentos A (crédito), B (complemento), C (boleto), Z (complemento geral), J (tributos), J52 (DARF) e J53 (GPS)

6. **Tipos de Arquivo**: Suporta Remessa (envio ao banco), Retorno (resposta do banco) e Varredura DDA (Débito Direto Autorizado)

7. **Processamento em Lote**: Arquivos CNAB são organizados em lotes, cada lote pode conter múltiplos detalhes de pagamento

8. **Validação Multinível**: 
   - Estrutural (formato, tamanho, posições)
   - Semântica (tipos de dados, domínios)
   - Negócio (totalizadores, sequências, interoperabilidade)

9. **Linha Digitável**: Sistema calcula e valida linha digitável de boletos bancários (código de barras)

10. **Código Banco**: Fixo como 655 (constante em CnabLayoutPojoInteface), identificando o Banco Votorantim

11. **Ambiente de Desenvolvimento**: URLs base em appbvdes.bvnet.bv indicam ambiente de desenvolvimento interno

12. **CI/CD**: Integração com Jenkins configurada (jenkins.properties)

13. **Dependências Internas**: Forte dependência de frameworks internos do Banco Votorantim (bv-framework-commons-datatypes, bv-apoio-operacao-core)

14. **Extensibilidade**: Arquitetura permite adição de novos layouts através de implementação de interfaces e configuração XML

15. **Tratamento de Erros**: Sistema diferencia erros de layout, validação, duplicação e estrutura através de enums específicos

---