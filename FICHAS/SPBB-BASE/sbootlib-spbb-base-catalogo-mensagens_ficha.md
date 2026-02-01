# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sbootlib-spbb-base-catalogo-mensagens** é uma biblioteca Spring Boot desenvolvida para facilitar a integração com o Sistema de Pagamentos Brasileiro (SPB) do Banco Central. Sua principal função é prover conversão bidirecional entre JSON e objetos Java para mensagens do SPB, validação estrutural baseada em esquemas XSD, e geração automática de enums de domínios e erros a partir de planilhas XLS fornecidas pelo BCB. A biblioteca atua como um catálogo centralizado de mensagens, permitindo que aplicações Java manipulem mensagens dos sistemas PAG, STR, DDA, SRC e GEN de forma tipada e validada.

---

## 2. Principais Classes e Responsabilidades

| Classe/Interface | Responsabilidade |
|------------------|------------------|
| **CatalogoMensagemService** | Conversão JSON↔Java de mensagens SPB, validação XSD, obtenção de MensagemGenerica |
| **DominioService** | Consulta domínios, erros e metadados de mensagens |
| **MetadadosService** | Extração de metadados de campos a partir de arquivos XSD |
| **LookupClasseCatalogo** | Resolução de classes Java do catálogo BCB por tipo de mensagem |
| **MensagemGenericaFactory** | Extração de dados básicos (codMsg, numCtrl, sitLanc) de mensagens JSON |
| **EnumGenerator** | Geração de código Java de enums a partir de modelos |
| **EnumProcessor** | Orquestração da leitura de XLS e geração de enums de domínios/erros |
| **XlsReader** | Leitura de planilhas XLS usando Apache POI |
| **CatalogoMensagemConfiguration** | Configuração Spring do ObjectMapper para mensagens BCB |
| **StatusEnum** | Enum com 462 status de operações DDA/BCB associados a situações de lançamento |
| **SitLancINTEnum** | Enum com 33 situações de lançamento INT (Digitada, Pendente, Efetivada, etc) |
| **InstituicaoEnum** | Enum com dados de instituições (CNPJ, ISPB, COMPE) - Votorantim e BV |
| **FlagAcaoEnum** | Enum de flags de ação (Ok, Pendente, Cancelado) |
| **IErroEnum/ISitLancEnum** | Interfaces para enums de erro e situação de lançamento |
| **XMLGregorianCalendar(De)Serializer** | Serialização/deserialização Jackson para XMLGregorianCalendar |
| **SecureDocumentUtils** | Criação segura de DocumentBuilderFactory (proteção XXE) |

---

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** - Framework base
- **Java 11** - Linguagem
- **JAXB** - Binding XML↔Java
- **Jackson XML** - Serialização/deserialização JSON/XML
- **JAXB2 Maven Plugin** - Geração de classes Java a partir de XSD
- **Apache POI** - Leitura de arquivos XLS
- **JavaPoet** - Geração programática de código Java
- **Lombok** - Redução de boilerplate
- **JUnit 5** - Testes unitários (116 testes)
- **Mockito** - Mocks para testes
- **Maven** - Gerenciamento de dependências e build
- **XML Schema Definition (XSD) v5.10/5.11** - Validação estrutural de mensagens

---

## 4. Principais Endpoints REST

**Não se aplica** - Esta é uma biblioteca (lib), não expõe endpoints REST. É utilizada por aplicações que consomem/produzem mensagens SPB.

---

## 5. Principais Regras de Negócio

- **Validação de Mensagens SPB**: Todas as mensagens devem seguir estrutura XSD definida pelo BCB (versões 5.10 e 5.11)
- **Remoção de Duplicatas**: Classes duplicadas do catálogo JAXB (DOCComplexType, BCMSGComplexType, etc) são removidas automaticamente no build
- **Geração de Enums Dinâmicos**: Enums de domínios e erros são gerados em build-time a partir de planilhas XLS, considerando datas de ativação/desativação em produção
- **Identificação de Tipos de Mensagem**: Sistema identifica automaticamente mensagens de resposta (R1/R2/R3) e erro (E) pelo sufixo do código
- **Normalização de Dados**: Conversão de aspas duplas para simples, remoção de espaços duplicados e caracteres especiais (NBSP) em dados de XLS
- **Validação de Instituições**: Suporte a ISPBs específicos (655-Banco Votorantim, 413-Banco BV) com validação de CNPJ e códigos COMPE
- **Conversão de Datas**: Suporte a XMLGregorianCalendar com formatos yyyy-MM-dd e yyyy-MM-dd'T'HH:mm:ss
- **Segurança XML**: Proteção contra ataques XXE (XML External Entity) na leitura de documentos XML
- **Versionamento de Catálogo**: Suporte a múltiplas versões do catálogo BCB (atualmente 5.11)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **Mensagem SPB**: Estrutura base com BCMSG (cabeçalho), SISMSG (corpo) e USERMSG (opcional)
  - Contém: IdentdEmissor, IdentdDestinatario, DomSist, NUOp, CodMsg, NumCtrlIF
  
- **Instituição Financeira (IF)**: Identificada por ISPB (8 chars), CNPJ, código COMPE
  - Relaciona-se com: Contas (RB, CL, bancária, pagamento), Clientes, Lançamentos

- **Cliente**: Pessoa Física ou Jurídica
  - Atributos: TpPessoa, CNPJ_CPF, Nome/RazãoSocial
  - Relaciona-se com: Contas, Transferências

- **Lançamento**: Operação financeira no SPB
  - Atributos: NumCtrlSTR/PAG, SitLanc, VlrLanc, DtMovto, NivelPref
  - Relaciona-se com: IF Debitada, IF Creditada, Clientes

- **Conta**: Bancária ou de Pagamento
  - Atributos: TpCt, Agência, Número, ISPB
  - Relaciona-se com: IF, Cliente

- **Domínio/Erro**: Enums gerados dinamicamente
  - Atributos: código, descrição, datas ativação/desativação
  - Implementam: ISitLancEnum ou IErroEnum

**Relacionamentos:**
- Mensagem 1:N Lançamento
- IF 1:N Conta
- Cliente 1:N Conta
- Lançamento N:1 IF (débito e crédito)
- StatusEnum N:1 ISitLancEnum
- StatusEnum N:1 FlagAcaoEnum

---

## 7. Estruturas de Banco de Dados Lidas

**Não se aplica** - A biblioteca não acessa diretamente banco de dados. Trabalha com mensagens XML/JSON e arquivos XLS/XSD.

---

## 8. Estruturas de Banco de Dados Atualizadas

**Não se aplica** - A biblioteca não realiza operações de escrita em banco de dados.

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| **MensagensSPB/**/*.XSD** | Leitura | MetadadosService, JAXB2 Plugin | Schemas XSD de mensagens SPB (PAG, STR, DDA, SRC, GEN) versões 5.10/5.11 |
| **Dom*.xls** | Leitura | EnumProcessor, XlsReader | Planilhas de domínios BCB para geração de enums |
| **Erros*.xls** | Leitura | EnumProcessor, XlsReader | Planilhas de erros BCB para geração de enums |
| **target/generated-sources/jaxb/** | Gravação | JAXB2 Maven Plugin | Classes Java geradas a partir de XSD |
| **target/generated-sources/enums/** | Gravação | EnumGenerator | Enums Java gerados a partir de XLS |
| **Enums Java (SitLanc*, Erro*)** | Gravação | EnumSpecificator | Código fonte de enums de domínios e erros |

---

## 10. Filas Lidas

**Não se aplica** - A biblioteca não consome mensagens de filas. É responsabilidade da aplicação que a utiliza.

---

## 11. Filas Geradas

**Não se aplica** - A biblioteca não publica mensagens em filas. É responsabilidade da aplicação que a utiliza.

---

## 12. Integrações Externas

| Sistema/Serviço | Tipo | Descrição |
|-----------------|------|-----------|
| **Catálogo BCB** | Fonte de Dados | Download de XSD e XLS de https://www.bcb.gov.br/estabilidadefinanceira/comunicacaodados |
| **Sistema SPB (PAG)** | Mensageria XML | Sistema de Pagamentos - transferências entre IFs, clientes, tributos |
| **Sistema STR** | Mensageria XML | Sistema de Transferência de Reservas - movimentação de reservas bancárias |
| **Sistema DDA** | Mensageria XML | Débito Direto Autorizado - gestão de boletos de pagamento |
| **Sistema SRC** | Mensageria XML | Sistema de Registro de Contratos - consulta permissões produtos |
| **Sistema GEN** | Mensageria XML | Operações Genéricas SPB - ECO, certificados, arquivos |

**Observação**: A biblioteca não realiza a comunicação diretamente. Ela fornece as ferramentas para serialização/deserialização e validação das mensagens que serão trafegadas pela aplicação cliente.

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada com separação clara de responsabilidades (services, factories, utils)
- Uso adequado de padrões de projeto (Factory, Strategy, Builder via JavaPoet)
- Boa cobertura de testes (116 testes JUnit5)
- Uso de Lombok reduzindo boilerplate
- Documentação inline nos XSD (annotations com descrições e regras)
- Tratamento de segurança (proteção XXE)
- Geração automática de código reduzindo manutenção manual
- Versionamento consistente dos schemas
- Uso de interfaces para extensibilidade (IErroEnum, ISitLancEnum)

**Pontos de Melhoria:**
- Falta de documentação JavaDoc em algumas classes públicas
- Alguns métodos longos (ex: MetadadosService.montarMetadadosMensagem)
- Dependência de arquivos XLS externos para geração de enums (fragilidade se formato mudar)
- Falta de logs estruturados em alguns fluxos críticos
- Alguns nomes de variáveis poderiam ser mais descritivos (ex: "Or" em NumCtrlSTROr)
- Ausência de métricas de qualidade de código (SonarQube, etc) documentadas

---

## 14. Observações Relevantes

1. **Build-time Code Generation**: A biblioteca gera código Java (classes JAXB e enums) durante o build Maven, o que pode aumentar o tempo de compilação inicial mas garante tipagem forte em runtime.

2. **Encoding ISO-8859-1**: Todos os XSD utilizam encoding ISO-8859-1, importante considerar ao processar mensagens com caracteres especiais.

3. **Remoção de Duplicatas**: O build Maven inclui um passo (maven-antrun-plugin) que remove classes duplicadas geradas pelo JAXB2, essencial para evitar conflitos de classpath.

4. **Versionamento de Catálogo**: A biblioteca suporta catálogo BCB versão 5.11 (última mensagem STR0052), mas mantém compatibilidade com 5.10.

5. **Anotação @EnableCatalogoMensagem**: Aplicações Spring Boot devem usar esta anotação para ativar a configuração automática da biblioteca.

6. **StatusEnum Extenso**: O enum StatusEnum contém 462 status diferentes, cobrindo todos os sistemas SPB (INT, BMC, CIR, CMP, LDL, LTR, PAG, RCO, RDC, SLB, STR, TES, CCR, CBL, CTP, SEL).

7. **Suporte a Múltiplos Sistemas**: A biblioteca suporta mensagens de 5 sistemas diferentes (PAG, STR, DDA, SRC, GEN), cada um com dezenas de tipos de mensagem.

8. **Validação Estrutural**: A validação é estrutural (baseada em XSD), não semântica. Regras de negócio específicas devem ser implementadas pela aplicação cliente.

9. **Particionamento de Mensagens**: Suporte a mensagens grandes via campo Grupo_Seq, permitindo envio em partes.

10. **Formato de Resposta**: Mensagens de resposta seguem padrão R1 (para requisitante), R2 (para terceiros envolvidos), R3 (para notificados), e E (para erros).

11. **Agendamento**: Suporte a agendamento de operações futuras via campos DtAgendt/HrAgendt.

12. **Priorização**: Campo NivelPref permite controlar prioridade de processamento de lançamentos.

13. **Histórico Limitado**: Campo Hist limitado a 200 caracteres em mensagens.

14. **Arquivos Anexos**: Suporte a transferência de arquivos via campos TamArq, IdentdArq, CodHash.

15. **Contingência**: Suporte a operações de contingência (STR0043/0044 para teste, GEN0031/0032 para avisos).