## Visão Geral
Este script é projetado para buscar informações sobre investimentos do site [Startupi](https://startupi.com.br/ranking-investimentos-2024/), organizá-las por mês e ano, e armazenar os dados relevantes em um banco de dados PostgreSQL. O script é estruturado em uma classe `InvestmentScraper` que lida com a coleta, análise e operações de banco de dados.

## Estrutura do Arquivo
- **Imports**: O script importa bibliotecas necessárias para requisições HTTP, operações de banco de dados, logging e outras utilidades.
- **Constantes**: Define constantes como mapeamento de meses, cabeçalhos HTTP e o nome da tabela do banco de dados.
- **Classe InvestmentScraper**: Contém métodos para inicializar o scraper, configurar o banco de dados, buscar conteúdo de páginas, analisar conteúdo e salvar dados no banco de dados.
- **Função Principal**: Inicializa a classe `InvestmentScraper` e aciona o processo de busca e salvamento.

## Componentes Principais

### Imports
- **requests**: Para fazer requisições HTTP.
- **BeautifulSoup**: Para analisar o conteúdo HTML.
- **psycopg2**: Para operações com o banco de dados PostgreSQL.
- **logging**: Para registrar informações e erros.
- **datetime**: Para manipulação de data e hora.
- **sys**: Para manipular o ambiente de execução do Python.

### Constantes
- **MES_NUMERAL**: Mapeamento de meses em português para seus respectivos números.
- **TABLE_NAME**: Nome da tabela do banco de dados para armazenar os dados de investimentos.
- **BASE_URL**: URL base para buscar os rankings de investimentos por ano.
- **HEADERS**: Cabeçalhos HTTP para a requisição.

### Classe InvestmentScraper
#### Inicialização
```python
class InvestmentScraper:
    """Classe para coletar e processar investimentos do Startupi."""

    def __init__(self, start_year: int = 2022) -> None:
        self.all_news_investments: List[Dict[str, str]] = []
        self.start_year = start_year
        self.end_year = datetime.now().year - 1
        self._setup_database()
```
- Inicializa o scraper com as configurações fornecidas e configura o banco de dados.

#### Configuração do Banco de Dados
```python
def _setup_database(self) -> None:
```
- Cria a tabela do banco de dados se ela não existir.

#### Obter Conteúdo da Página
```python
def get_page_content(self, url: str) -> Optional[str]:
```
- Obtém o conteúdo HTML da página especificada.

#### Analisar Conteúdo
```python
def parse_content(self, html: str, year: int) -> List[Dict[str, str]]:
```
- Extrai os textos organizados por mês e ano, formatando a data.

#### Coletar Investimentos
```python
def scrape_investments(self) -> None:
```
- Executa o fluxo completo para coletar os dados dos investimentos.

#### Salvar no PostgreSQL
```python
def save_to_postgres(self) -> None:
```
- Salva os artigos extraídos no banco de dados PostgreSQL.

### Função Principal
```python
def main() -> None:
    """Função principal para executar o scraper e salvar os dados."""
    scraper = InvestmentScraper(start_year=2022)
    scraper.scrape_investments()
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
```
- Inicializa a classe `InvestmentScraper` e aciona o processo de busca e salvamento.

## Logging
- O script usa o módulo `logging` para registrar informações e erros.
- Os logs são salvos em um arquivo chamado `startupi.log` e também são impressos no console.

## Conexão com o Banco de Dados
- O script usa uma classe personalizada `DatabaseConnection` do módulo `config.db_connection` para lidar com conexões de banco de dados.

## Pontos Importantes para Manutenção
- **Atualizar Anos**: Se novos anos precisarem ser adicionados para buscar investimentos, atualize o parâmetro `start_year` na inicialização da classe `InvestmentScraper`.
- **Esquema do Banco de Dados**: Certifique-se de que o esquema do banco de dados corresponda à estrutura definida no método `_setup_database`.
- **Tratamento de Erros**: O script inclui tratamento básico de erros para requisições HTTP e operações de banco de dados. Certifique-se de que isso seja suficiente para seu caso de uso.
- **Logging**: Verifique o arquivo `startupi.log` para logs detalhados e erros.

## Instalação e Execução

### Instalação das Bibliotecas
Para instalar as bibliotecas necessárias, você pode usar o `pip` e o arquivo `requirements.txt` que deve conter todas as dependências. Crie um arquivo `requirements.txt` com o seguinte conteúdo:

```text
requests
beautifulsoup4
psycopg2-binary
```

Em seguida, execute o comando:

```bash
pip install -r requirements.txt
```

### Execução do Script
Para executar o script, basta rodar o seguinte comando no terminal:

```bash
python scrape_startupi_investments.py
```

Certifique-se de que o banco de dados PostgreSQL esteja configurado corretamente e que as credenciais de conexão estejam corretas no módulo `config.db_connection`.