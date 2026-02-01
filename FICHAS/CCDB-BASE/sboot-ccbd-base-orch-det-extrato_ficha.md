# Ficha Técnica do Sistema

## 1. Descrição Geral

O **sboot-ccbd-base-orch-det-extrato** é um orquestrador de serviços responsável por fornecer o detalhamento de movimentações bancárias e a geração de comprovantes em formato PDF. O sistema utiliza Apache Camel para orquestração de fluxos complexos, integrando múltiplos serviços atoms e orchs para consolidar informações de diferentes tipos de transações (PIX, TED, DOC, Boletos, Cartões). Atua como camada de agregação e enriquecimento de dados, validando titularidade de contas, categorizando transações e formatando informações para apresentação ao usuário final.

---

## 2. Principais Classes e Responsabilidades

| Classe | Responsabilidade |
|--------|------------------|
| **DetExtratoController** | Controller REST que expõe endpoints para consulta de detalhes de movimentação e geração de comprovantes |
| **DetExtratoService** | Service principal que utiliza CamelContext para orquestrar fluxos de detalhamento e geração de comprovantes |
| **MainExtratoRouter** | Roteador Camel principal que valida titularidade, consulta categoria e direciona para fluxos específicos (PIX/Boleto/SPAG) |
| **DetExtratoRouter** | Roteador Camel para orquestração de detalhamento de extrato, diferenciando boletos agendados de PIX agendados |
| **PixRouter** | Roteador Camel específico para transações PIX, gerenciando tokens e consultas a participantes |
| **SpagRouter** | Roteador Camel para processamento via SPAG (Sistema de Pagamentos), com fallback para DetExtrato |
| **ComprovanteRouter** | Roteador Camel para geração de comprovantes PDF |
| **MovimentacaoConversor** | Converte MovimentacaoDTO para MovimentacaoRepresentation, identificando tipos de transação |
| **BoletoConversor** | Mapeia MovimentacaoDTO para BoletoRepresentation com regras de negócio específicas |
| **PixConsultaPgtoConversor** | Converte resposta SPAG de consulta PIX para MovimentacaoDTO, substituindo PixConversor deprecated |
| **ComprovanteConversor** | Converte MovimentacaoRepresentation para ComprovanteDTO com formatação e mascaramento de dados |
| **ComprovanteRepositoryImpl** | Gera comprovantes PDF usando JasperReports e converte para Base64 |
| **DetExtratoRepositoryImpl** | Consulta movimentações no atom de movimentações |
| **DetPixExtratoRepositoryImpl** | Consulta pagamentos PIX via SPAG consulta pagamento |
| **DetBoletoRepositoryImpl** | Consulta boletos (comum, cartão, agendamento) em diferentes endpoints |
| **SpagRepositoryImpl** | Consulta lançamentos SPAG por código |
| **ClienteDadosCadastraisRepositoryImpl** | Valida titularidade de conta consultando dados cadastrais |
| **CategoriaMovimentacaoRepositoryImpl** | Consulta categoria de movimentação no atom |
| **ListaBancoRepositoryImpl** | Consulta lista de bancos no atom |
| **ParticipantesPixRepositoryImpl** | Consulta participantes PIX para obter nomes de agentes |

---

## 3. Tecnologias Utilizadas

- **Spring Boot** - Framework base da aplicação
- **Apache Camel 3.19** - Orquestração de rotas e integração
- **Spring Security OAuth2** - Segurança e autenticação (@EnableResourceServer)
- **RestTemplate** - Cliente HTTP para integração com APIs
- **JasperReports** - Geração de relatórios PDF (comprovantes)
- **Springfox Swagger 2** - Documentação OpenAPI
- **Logback** - Logging em formato JSON assíncrono
- **Jackson** - Serialização/deserialização JSON
- **Java 11+** - Linguagem de programação
- **Maven** - Gerenciamento de dependências
- **HTTP Basic Authentication** - Autenticação em serviços SPAG
- **OAuth2 Client Credentials** - Geração de tokens JWT para APIs

---

## 4. Principais Endpoints REST

| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| GET | /v1/banco-digital/movimentacao-bancaria/detalhe | DetExtratoController | Retorna detalhamento de uma movimentação bancária específica |
| GET | /v1/banco-digital/movimentacao-bancaria/comprovante | DetExtratoController | Gera e retorna comprovante em PDF (Base64) de uma movimentação |

**Parâmetros comuns:**
- codigoBanco (obrigatório)
- numeroAgencia (obrigatório)
- numeroConta (obrigatório)
- numeroCpfCnpj (extraído do JWT)
- nsu (condicional)
- numeroDocumento (condicional)
- codigoAutorizacaoPagamento (condicional)

*Pelo menos um dos parâmetros condicionais deve ser informado*

---

## 5. Principais Regras de Negócio

1. **Validação de Titularidade**: Antes de retornar detalhes, valida se o CPF/CNPJ do JWT corresponde ao titular da conta consultada
2. **Classificação de Transações**: Identifica automaticamente o tipo de transação (PIX, TED, DOC, Boleto, Cartão) baseado em categoria e código de liquidação
3. **Diferenciação de Fluxos PIX**: Transações PIX seguem fluxo específico com consulta ao SPAG e participantes, diferenciando banco BVSA de outros bancos
4. **Boleto Cartão vs Comum**: Boletos de cartão são identificados por codigoAutorizacaoPagamento e seguem fluxo distinto
5. **Agendamento Legado**: Boletos de cobrança agendados (legado) seguem fluxo diferente de PIX agendados
6. **Enriquecimento de Dados**: Consulta nomes de bancos, participantes PIX e categorias para enriquecer informações da movimentação
7. **Cálculo de IOF**: Para boletos de cartão, adiciona valor de IOF ao detalhamento
8. **Identificação Saque/Troco PIX**: Em transações PIX, identifica saque (OTHR) e troco (GSCB) baseado em códigos específicos
9. **Devoluções PIX**: Separa transação original de devoluções usando prefixo do endToEndId (E=original, D=devolução)
10. **Fallback SPAG**: Se consulta SPAG retornar nula, realiza fallback para consulta DetExtrato
11. **Mascaramento de Dados Sensíveis**: CPF/CNPJ são formatados e parcialmente ocultados nos comprovantes
12. **Conversão de Datas**: Todas as datas são convertidas para UTC no formato ISO 8601
13. **Validação de ISPB**: Valida códigos ISPB de participantes PIX
14. **Retry em Erros 5xx**: Implementa retry automático para erros de servidor (OrquestracaoException)

---

## 6. Relação entre Entidades

**Entidades Principais:**

- **MovimentacaoDTO**: Entidade central que agrega todas as informações de uma movimentação
  - Contém: nsu, tipoTransacao, valores, categoria, dados remetente/favorecido
  - Relaciona-se com: PagamentoPixDTO, BoletoDTO, AgendamentoDTO

- **PagamentoPixDTO**: Detalhes específicos de transações PIX
  - Contém: endToEndId, ispb, contas remetente/favorecido, devolução, saque/troco
  - Relaciona-se com: TransacaoOriginal (para devoluções)

- **BoletoDTO**: Detalhes de boletos
  - Contém: codigoBarras, valores, dados beneficiário/pagador, encargos
  - Tipos: boleto comum, boleto cartão, boleto agendado

- **AgendamentoDTO**: Informações de agendamentos
  - Contém: cdTransacao, vrAgendamento, dtAgendamento

- **CategoriaMovimentacaoDTO**: Categorização da transação
  - Relaciona-se com: CategoriaTransacaoEnum (60+ categorias)

- **ComprovanteDTO**: Dados formatados para geração de PDF
  - Derivado de: MovimentacaoRepresentation
  - Tipos: ComprovantePix, ComprovanteBoleto

**Relacionamentos:**
- MovimentacaoDTO 1:1 CategoriaMovimentacaoDTO
- MovimentacaoDTO 0:1 PagamentoPixDTO
- MovimentacaoDTO 0:1 BoletoDTO
- MovimentacaoDTO 0:1 AgendamentoDTO
- PagamentoPixDTO 0:1 TransacaoOriginal (para devoluções)

---

## 7. Estruturas de Banco de Dados Lidas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | O sistema não acessa diretamente banco de dados. Todas as consultas são realizadas via APIs REST de serviços atoms/orchs |

---

## 8. Estruturas de Banco de Dados Atualizadas

| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| Não se aplica | - | - | O sistema não realiza operações de escrita em banco de dados. É um orquestrador read-only que consome APIs |

---

## 9. Arquivos Lidos e Gravados

| Nome do Arquivo | Operação | Local/Classe Responsável | Breve Descrição |
|-----------------|----------|-------------------------|-----------------|
| *.jrxml | Leitura | ComprovanteRepositoryImpl | Templates JasperReports para geração de comprovantes PIX e Boleto |
| logobv.png | Leitura | ComprovanteRepositoryImpl | Logotipo do banco incluído nos comprovantes PDF |
| application.yml | Leitura | Spring Boot | Arquivo de configuração principal com URLs de serviços e credenciais |
| application-local.yml | Leitura | Spring Boot | Configurações específicas do ambiente local/UAT |
| logback-spring.xml | Leitura | Logback | Configuração de logs em formato JSON assíncrono |
| infra.yml | Leitura | Kubernetes/Deploy | Configurações de infraestrutura (recursos, probes, URLs) |

**Observação:** Os comprovantes PDF gerados são retornados como Base64 em memória, não sendo gravados em disco.

---

## 10. Filas Lidas

Não se aplica. O sistema não consome mensagens de filas (JMS, Kafka, RabbitMQ). Toda integração é realizada via APIs REST síncronas.

---

## 11. Filas Geradas

Não se aplica. O sistema não publica mensagens em filas. Toda comunicação é realizada via APIs REST síncronas.

---

## 12. Integrações Externas

| Sistema/API | Tipo | Descrição |
|-------------|------|-----------|
| **sboot-ccbd-base-atom-movimentacoes** | API REST | Consulta detalhes de movimentações, categorias e extratos bancários |
| **sboot-glob-base-atom-cliente-dados-cadastrais** | API REST | Valida titularidade de conta consultando dados cadastrais do cliente |
| **sboot-glob-base-atom-lista-bancos** | API REST | Consulta lista de bancos BACEN para enriquecimento de dados |
| **sboot-ccdb-base-atom-info-pgto-trib-bol** | API REST | Consulta informações de boletos (segunda via, agendamento, IOF) |
| **sboot-spag-pixx-orch-consultar-pagamento** | API REST | Consulta pagamentos PIX no SPAG (substitui orch-aviso deprecated) |
| **sboot-spag-pixx-atom-participantes** | API REST | Consulta participantes PIX para obter nomes de remetentes/favorecidos |
| **SPAG Base Gestão** | API REST (Basic Auth) | Consulta lançamentos SPAG por código |
| **CCBD Base Atom Movimentações** | API REST | Consulta movimentações CCBD por protocolo |
| **API Gerar Token** | OAuth2 | Gera tokens JWT para autenticação em serviços SPAG |
| **API Gerar Token SPAG PIX** | OAuth2 | Gera tokens JWT específicos para serviços PIX (diferenciado para banco BVSA) |

**Observações:**
- Integração com **sboot-spag-pixx-orch-aviso** está deprecated, substituída por consultar-pagamento
- Diferenciação de geração de token para banco BVSA (ISPB 01858774) vs outros bancos
- Todas as integrações utilizam RestTemplate com tratamento de erros e retry para 5xx

---

## 13. Avaliação da Qualidade do Código

**Nota: 8/10**

**Justificativa:**

**Pontos Positivos:**
- **Arquitetura bem estruturada**: Uso adequado de Apache Camel para orquestração complexa, separando responsabilidades em routers específicos
- **Padrões de projeto**: Implementação consistente de conversores, uso de builders, separação clara entre DTOs e Representations
- **Tratamento de exceções**: Handler centralizado com mapeamento adequado para HTTP status e mensagens de erro padronizadas
- **Documentação OpenAPI**: Especificações Swagger bem definidas para todos os endpoints
- **Configuração externalizada**: Uso apropriado de @ConfigurationProperties e arquivos YAML para diferentes ambientes
- **Separação de concerns**: Repositories, Services, Controllers e Routers bem delimitados
- **Enums bem estruturados**: CategoriaTransacaoEnum, CodigoLiquidacaoEnum e TipoBancoEnum facilitam manutenção

**Pontos de Melhoria:**
- **Código deprecated não removido**: PixConversor e DetPixRepositoryImpl ainda presentes no código
- **Complexidade dos routers**: Alguns routers Camel têm lógica muito extensa, dificultando manutenção
- **Falta de testes unitários evidentes**: Não foram fornecidos testes no resumo
- **Documentação inline limitada**: Alguns métodos complexos carecem de comentários explicativos
- **Acoplamento com múltiplas APIs**: Alta dependência de serviços externos pode impactar resiliência
- **Hardcoded values**: Alguns valores como ISPBs e códigos aparecem hardcoded em vez de configuráveis

**Recomendações:**
1. Remover código deprecated (PixConversor, DetPixRepositoryImpl)
2. Refatorar routers muito extensos em sub-rotas menores
3. Implementar circuit breakers para integrações externas
4. Adicionar testes unitários e de integração
5. Melhorar documentação inline em métodos complexos
6. Considerar externalizar valores hardcoded para configuração

---

## 14. Observações Relevantes

1. **Migração de APIs PIX**: O sistema passou por migração de consulta PIX, substituindo `sboot-spag-pixx-orch-aviso` por `sboot-spag-pixx-orch-consultar-pagamento`. Classes antigas marcadas como deprecated ainda presentes no código.

2. **Diferenciação BVSA**: Existe tratamento especial para o banco BVSA (ISPB 01858774), com geração de token authorization diferenciada em relação a outros bancos.

3. **Orquestração Complexa**: O sistema implementa orquestração sofisticada com múltiplos pontos de decisão (PIX/Boleto/SPAG/Agendamento), utilizando predicates customizados para roteamento.

4. **Geração de Comprovantes**: Utiliza JasperReports para geração de PDFs, convertendo para bitmap e depois Base64 para retorno via API. Templates específicos para PIX e Boleto.

5. **Segurança**: Implementa validação de titularidade antes de retornar dados, garantindo que apenas o titular da conta acesse informações.

6. **Resiliência**: Implementa retry automático para erros 5xx através de OrquestracaoException, mas não há evidência de circuit breakers.

7. **Mascaramento de Dados**: CPF/CNPJ são formatados e parcialmente ocultados nos comprovantes para proteção de dados sensíveis.

8. **Conversão de Datas**: Todas as datas são padronizadas para UTC ISO 8601, garantindo consistência temporal.

9. **Categorização Extensa**: Suporta 60+ categorias de transações através de CategoriaTransacaoEnum, cobrindo ampla gama de operações bancárias.

10. **Fallback Strategies**: Implementa estratégias de fallback (ex: SPAG -> DetExtrato) para garantir disponibilidade de dados.

11. **Configuração por Ambiente**: Suporta múltiplos ambientes (local, UAT, produção) através de profiles Spring e arquivos YAML específicos.

12. **Observabilidade**: Logs estruturados em JSON assíncrono facilitam monitoramento e troubleshooting em ambientes cloud.

13. **Kubernetes Ready**: Configurações de probes (liveness/readiness) e recursos (CPU/memória) preparadas para deploy em Kubernetes.

14. **Integração Extensa**: Integra com 10+ serviços diferentes, atuando como verdadeiro hub de consolidação de informações bancárias.