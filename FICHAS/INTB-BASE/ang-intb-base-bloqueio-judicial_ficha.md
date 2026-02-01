## Ficha Técnica do Sistema

### 1. Descrição Geral
O sistema é uma aplicação Angular que gerencia bloqueios judiciais, permitindo a visualização e manipulação de dados relacionados a processos judiciais, contas correntes, e outros ativos financeiros. Ele oferece funcionalidades como consulta de bloqueios, exportação de dados em PDF, e navegação entre diferentes componentes e módulos.

### 2. Principais Classes e Responsabilidades
- **EmptyProcessComponent**: Componente que representa um processo vazio, utilizado para indicar a ausência de dados.
- **LoadingComponent**: Componente que exibe um indicador de carregamento.
- **BloqueioTabsComponent**: Componente que gerencia as abas de navegação entre diferentes tipos de bloqueios.
- **ContaCorrenteComponent**: Componente que exibe informações de bloqueios em contas correntes.
- **ProcessoComponent**: Componente que exibe detalhes de um processo judicial específico.
- **BloqueioService**: Serviço responsável por realizar consultas de bloqueios judiciais e exportação de dados em PDF.

### 3. Tecnologias Utilizadas
- Angular 7
- Angular Material
- RxJS
- Moment.js
- JSON Server
- Node.js
- TypeScript

### 4. Principais Endpoints REST
| Método | Endpoint | Classe Controladora | Descrição |
|--------|----------|---------------------|-----------|
| POST   | /v1/ib/bloqueio/judicial | BloqueioService | Consulta tipos de bloqueio judicial. |
| POST   | /v1/ib/bloqueio/judicial/processo | BloqueioService | Consulta bloqueios por processo. |
| POST   | /v1/ib/bloqueio/judicial/pdf | BloqueioService | Exporta dados de bloqueio em PDF. |

### 5. Principais Regras de Negócio
- Consultar bloqueios judiciais por tipo e processo.
- Exportar dados de bloqueios em formato PDF.
- Navegação entre diferentes componentes e módulos para exibição de dados específicos.

### 6. Relação entre Entidades
- **BloqueioJudicialModel**: Representa os dados de um bloqueio judicial.
- **BloqueioJudicialProcessoModel**: Agrupa bloqueios judiciais por tipo de ativo.
- **BloqueioRequestModel**: Modelo para requisição de consulta de bloqueios.

### 7. Estruturas de Banco de Dados Lidas
Não se aplica.

### 8. Estruturas de Banco de Dados Atualizadas
Não se aplica.

### 9. Filas Lidas
Não se aplica.

### 10. Filas Geradas
Não se aplica.

### 11. Integrações Externas
- API BV para consulta de dados de bloqueios judiciais e exportação de PDF.

### 12. Avaliação da Qualidade do Código
**Nota:** 8

**Justificativa:** O código é bem estruturado e organizado, utilizando boas práticas de Angular e TypeScript. A separação de responsabilidades entre componentes e serviços é clara, facilitando a manutenção e evolução do sistema. No entanto, poderia haver uma documentação mais detalhada em alguns trechos do código.

### 13. Observações Relevantes
- O sistema utiliza o JSON Server para simular respostas de API durante o desenvolvimento.
- A aplicação é configurada para rodar em ambiente local com Node.js 8, utilizando o nvm para gerenciar versões do Node.
- O sistema possui integração com o Nexus para gerenciamento de pacotes NPM.