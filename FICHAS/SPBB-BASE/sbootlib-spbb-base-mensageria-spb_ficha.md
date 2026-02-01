# Ficha Técnica do Sistema

## 1. Descrição Geral

Esta biblioteca Java (sbootlib-spbb-base-mensageria-spb) é uma solução corporativa desenvolvida para facilitar a integração e manipulação de mensagens do Sistema de Pagamentos Brasileiro (SPB) do Banco Central do Brasil. A biblioteca oferece funcionalidades de conversão entre formatos XML e JSON, validação de mensagens conforme catálogo do BACEN (versão 5.11), geração automática de enums a partir de planilhas XLS, e serviços para consulta de domínios, erros, metadados e filas de integração. Atua como uma camada de abstração sobre o catálogo oficial de mensagens SPB, facilitando o desenvolvimento de aplicações que necessitam comunicar-se com o sistema de pagamentos.

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **SpbMensagemConversorService** | Serviço principal para conversão entre XML, JSON e objetos Java do catálogo SPB. Realiza validações contra XSD. |
| **DominioService** | Gerencia consultas a domínios, erros, status, instituições, grupos de mensagens e metadados. |
| **MetadadosService** | Extrai metadados de mensagens a partir de arquivos XSD, incluindo campos, tipos, restrições e obrigatoriedade. |
| **GrupoMensagemService** | Lista e organiza grupos de mensagens disponíveis no catálogo. |
| **FilaIntegracaoService** | Monta nomes de filas remotas e locais para integração com o SPB. |
| **MensagemGenericaFactory** | Cria objetos MensagemGenerica a partir de XML, extraindo informações comuns (BCMsg, SISMsg, erros). |
| **LookupClasseCatalogo** | Localiza classes do catálogo SPB (DOCComplexType, ObjectFactory) a partir do identificador da mensagem. |
| **XMLUtils** | Utilitários para conversão entre XML e objetos Java usando JAXB. |
| **XSDUtils** | Utilitários para validação de XML contra schemas XSD. |
| **EnumGenerator** | Gera enums Java a partir de dados lidos de planilhas XLS (domínios, erros, mensagens). |
| **StatusEnum** | Enum consolidado com todos os status possíveis de mensagens SPB, mapeando situações por câmara. |
| **InstituicaoEnum** | Enum com informações de instituições financeiras (CNPJ, ISPB, COMPE). |

## 3. Tecnologias Utilizadas

- **Spring Boot 2.x** (framework base, auto-configuração)
- **Spring Integration** (integração de sistemas)
- **Jackson 2.16.2** (serialização/deserialização JSON/XML)
- **JAXB 2.3.1** (binding XML-Java)
- **Apache POI 5.2.3** (leitura de arquivos XLS)
- **JavaPoet 1.13.0** (geração de código Java)
- **Lombok 1.18.22** (redução de boilerplate)
- **JUnit 5** (testes unitários)
- **Maven** (gerenciamento de dependências e build)
- **Java 11** (versão da linguagem)

## 4. Principais Endpoints REST

não se aplica

## 5. Principais Regras de Negócio

- **Validação de Mensagens SPB**: Todas as mensagens XML são validadas contra os schemas XSD oficiais do BACEN antes de serem processadas ou enviadas.
- **Conversão Bidirecional**: Suporte completo para conversão entre XML ↔ JSON ↔ Java Objects, mantendo compatibilidade com o catálogo SPB.
- **Geração Automática de Enums**: Domínios, erros e mensagens são gerados automaticamente a partir de planilhas XLS fornecidas pelo BACEN, garantindo sincronização com versões do catálogo.
- **Filtro de Domínios Ativos**: Apenas domínios e erros ativos (não desativados) são incluídos nos enums gerados.
- **Mapeamento de Status**: Sistema de mapeamento de status de mensagens por câmara (STR, PAG, CIR, etc.) com flags de ação (OK, Pendente, Cancelado).
- **Resolução de Propriedades**: Extração dinâmica de propriedades de mensagens sem necessidade de conhecer a estrutura completa.
- **Nomenclatura de Filas**: Geração padronizada de nomes de filas (QR/QL) seguindo convenções do SPB (ISPB, sequencial, tipo).
- **Suporte a Múltiplas Câmaras**: Tratamento específico para diferentes câmaras de liquidação (BACEN, CIP, B3, SELIC, etc.).
- **Metadados de Mensagens**: Extração automática de metadados (campos obrigatórios, tipos, restrições) diretamente dos XSDs.

## 6. Relação entre Entidades

**Hierarquia de Mensagens:**
- `MensagemGenerica` contém `BCMsg` (cabeçalho) e `SISMsg` (corpo)
- `BCMsg`: IdentdEmissor, IdentdDestinatario, DomSist, NUOp
- `SISMsg`: CodMsg, VlrLanc, SitLanc, AgCredtd, AgDebtd, NUOpOr, CodErros

**Domínios e Enums:**
- `IMensagemEnum` (interface) ← implementada por MensagemXXXEnum (gerados)
- `IErroEnum` (interface) ← implementada por ErroXXXEnum (gerados)
- `ISitLancEnum` (interface) ← implementada por SitLancXXXEnum (gerados)

**Metadados:**
- `MetadadosMensagem` contém lista recursiva de `MetadadosMensagem` (campos aninhados)
- `MetadadosMensagem` possui `Restricao` (validações: minLength, maxLength, pattern, etc.)

**Catálogo:**
- `LookupClasseCatalogo` localiza classes em pacotes: br.gov.bcb.spb, br.gov.bcb.mes, br.gov.bcb.gen
- Cada mensagem possui DOCComplexType e ObjectFactory correspondentes

## 7. Estruturas de Banco de Dados Lidas

não se aplica

## 8. Estruturas de Banco de Dados Atualizadas

não se aplica

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| Dom20251114.xls | Leitura | DominioXlsMapper (maven) | Planilha com domínios do catálogo SPB para geração de enums |
| Erros20251114.xls | Leitura | ErroXlsMapper (maven) | Planilha com códigos de erro do catálogo SPB |
| Mensagens.xls | Leitura | MensagemXlsMapper (maven) | Planilha com tipos de mensagens e suas características |
| *.XSD (MensagensSPB/*) | Leitura | MetadadosService, XSDUtils | Schemas XML para validação e extração de metadados |
| *.java (generated) | Gravação | EnumGenerator, FileUtils | Enums Java gerados automaticamente durante o build |

## 10. Filas Lidas

A biblioteca não consome filas diretamente, mas fornece o serviço `FilaIntegracaoService` que gera nomes de filas no padrão:
- **Filas Remotas (QR)**: `QR.{TIPO}.{ISPB_INSTITUICAO}.{ISPB_DESTINO}.{SEQUENCIAL}`
- **Filas Locais (QL)**: `QL.{TIPO}.{ISPB_DESTINO}.{ISPB_INSTITUICAO}.{SEQUENCIAL}`

Tipos de fila: REQ (Requisição), RSP (Resposta), REP (Reporte), SUP (Suporte)

## 11. Filas Geradas

não se aplica (a biblioteca apenas monta os nomes das filas, não as cria)

## 12. Integrações Externas

- **Catálogo BACEN SPB**: Integração com schemas XSD e especificações do Sistema de Pagamentos Brasileiro (versão 5.11)
- **Sistema de Mensageria**: Preparação de mensagens para envio/recebimento via filas JMS/MQ (integração indireta)
- **Câmaras de Liquidação**: Suporte para múltiplas câmaras (BACEN, CIP SITRAF, CIP SILOC, CIP C3, B3, SELIC, STN)

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- Arquitetura bem organizada com separação clara de responsabilidades (services, converters, utils, domain)
- Uso adequado de padrões de projeto (Factory, Strategy, Decorator)
- Boa cobertura de testes (estrutura completa de testes unitários)
- Documentação presente (README, comentários em código)
- Uso de Lombok para redução de boilerplate
- Geração automática de código a partir de fontes oficiais (XLS)
- Tratamento de exceções customizado e específico
- Configuração de segurança XML (proteção contra XXE)

**Pontos de Melhoria:**
- Algumas classes com múltiplas responsabilidades (ex: DominioService com 8+ métodos públicos)
- Código de geração de enums (pacote maven) poderia ser melhor modularizado
- Alguns métodos longos que poderiam ser refatorados (ex: MensagemEnumSpecificator)
- Dependências com versões fixas no pom.xml (poderia usar properties)
- Falta de logs estruturados em alguns pontos críticos
- Alguns testes marcados como [NAO_ENVIAR] sugerem possível incompletude

## 14. Observações Relevantes

1. **Build Complexo**: O processo de build utiliza maven-antrun-plugin e exec-maven-plugin para compilar e executar geradores de enum antes da compilação principal. Isso pode causar problemas em IDEs.

2. **Exclusões no Build**: O pacote `maven/**` é excluído do JAR final, mas é necessário durante o build. Isso pode causar confusão e requer atenção especial ao fazer manutenções.

3. **Cobertura Sonar**: Há instruções específicas no README sobre como temporariamente modificar o pom.xml para que o Sonar contabilize corretamente a cobertura do pacote maven.

4. **Auto-configuração Spring**: A biblioteca usa `spring.factories` para auto-configuração, sendo ativada pela anotação `@EnableLibMensageria`.

5. **Versão do Catálogo**: Atualmente configurada para versão 5.11 do catálogo BACEN (propriedade em application.yml).

6. **Segurança**: Implementa proteções contra XXE (XML External Entity) attacks através de `SecureDocumentUtils`.

7. **Múltiplos Pacotes de Catálogo**: Suporta três pacotes diferentes do catálogo (spb, mes, gen) com fallback automático.

8. **Geração de Código**: Três execuções separadas do gerador de enums (domínios, erros, mensagens) durante o build Maven.

9. **Instituições Suportadas**: Enum com Banco Votorantim e Banco BV (CNPJ, ISPB, COMPE).

10. **Repositório Nexus**: Distribuição via Nexus corporativo (nexus.bvnet.bv).