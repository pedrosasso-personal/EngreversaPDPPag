## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema "Serviço Atômico de ControladoriaCarga" é um microserviço desenvolvido para gerenciar contratos de controladoria, incluindo a criação e adição de parcelas a contratos. Ele utiliza o framework Spring Boot e está configurado para operar em ambientes de desenvolvimento, teste e produção. O serviço expõe endpoints REST para interações HTTP e utiliza o Swagger para documentação de APIs.

### 2. Principais Classes e Responsabilidades
- `Application`: Classe principal que inicia a aplicação Spring Boot.
- `ControladoriaCargaConfiguration`: Configurações de beans para Jdbi, repositórios e serviços.
- `OpenApiConfiguration`: Configuração do Swagger para documentação de APIs.
- `ControladoriaCargaRepositoryJdbi`: Implementação do repositório para operações de banco de dados relacionadas a contratos de controladoria.
- `ControladoriaCargaMapper`: Mapeamento entre entidades de domínio e representações de API.
- `ControladoriaCargaController`: Controlador REST que expõe endpoints para operações de contratos de controladoria.
- `ControladoriaCargaService`: Serviço de domínio que contém lógica de negócios para criação e manipulação de contratos de controladoria.
- `Controladoria`: Entidade de domínio que representa um contrato de controladoria.
- `ParceiroComercial`: Entidade de domínio que representa um parceiro comercial.
- `Parcela`: Entidade de domínio que representa uma parcela de contrato.

### 3. Tecnologias Utilizadas
- Java 11
- Spring Boot
- Jdbi
- Swagger
- Docker
- Jenkins
- Prometheus
- Grafana
- Sybase

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/varejo/contratos/gestao/controladoria | ControladoriaCargaController | Criar Contrato Controladoria |

### 5. Principais Regras de Negócio
- Criação de contratos de controladoria com validação de dados e inserção no banco de dados.
- Adição de parcelas a contratos existentes, com verificação de inconsistências.
- Retorno de identificadores de contratos após criação bem-sucedida.

### 6. Relação entre Entidades
- `Controladoria` possui uma lista de `Parcela`.
- `Controladoria` está associado a um `ParceiroComercial`.

### 7. Estruturas de Banco de Dados Lidas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoContrato | tabela | SELECT | Armazena informações de contratos de controladoria. |

### 8. Estruturas de Banco de Dados Atualizadas
| Nome da Tabela/View/Coleção | Tipo | Operação | Breve Descrição |
|-----------------------------|------|----------|-----------------|
| TbIntegracaoContrato | tabela | INSERT | Insere novos contratos de controladoria. |
| TbIntegracaoContratoParcela | tabela | INSERT | Insere parcelas de contratos de controladoria. |

### 9. Filas Lidas
não se aplica

### 10. Filas Geradas
não se aplica

### 11. Integrações Externas
- Integração com banco de dados Sybase para operações de leitura e escrita de contratos.
- Documentação de APIs via Swagger.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código está bem estruturado, utilizando boas práticas de desenvolvimento como injeção de dependências e separação de responsabilidades. A documentação via Swagger facilita a compreensão dos endpoints disponíveis. No entanto, poderia haver mais comentários explicativos em algumas partes complexas do código.

### 13. Observações Relevantes
- O sistema utiliza Prometheus e Grafana para monitoramento de métricas.
- Configurações de ambiente são gerenciadas via arquivos YAML e Docker.
- A aplicação possui testes automatizados para garantir a qualidade e funcionalidade do código.