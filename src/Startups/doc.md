## Visão Geral
Este script é projetado para fazer scraping de artigos de notícias do site [startups](https://startups.com.br/ultimas-noticias), filtrá-los com base em certos termos e armazenar os artigos relevantes em um banco de dados PostgreSQL. O script é estruturado em uma classe `NewsScraper` que lida com o scraping, filtragem e operações de banco de dados.

## Estrutura do Arquivo
- **Imports**: O script importa bibliotecas necessárias para web scraping, operações de banco de dados, logging e outras utilidades.
- **Constantes**: Define constantes como a URL base para scraping, termos de busca, número máximo de páginas a serem raspadas e o nome da tabela do banco de dados.
- **Classe NewsScraper**: Contém métodos para inicializar o scraper, configurar o banco de dados, fazer scraping de notícias e salvar dados no banco de dados.
- **Função Principal**: Inicializa a classe `NewsScraper` e aciona o processo de scraping e salvamento.

## Componentes Principais

### Imports
- **requests**: Para fazer requisições HTTP.
- **BeautifulSoup**: Para analisar o conteúdo HTML.
- **psycopg2**: Para operações com o banco de dados PostgreSQL.
- **logging**: Para registrar informações e erros.
- **datetime**: Para manipulação de data e hora.
- **sys**: Para manipular o ambiente de execução do Python.

### Constantes
- **BASE_URL**: A URL base para o site de notícias.
- **TERMOS**: Lista de termos para filtrar artigos de notícias relevantes.
- **MAX_PAGES**: Número máximo de páginas a serem raspadas.
- **TABLE_NAME**: Nome da tabela do banco de dados para armazenar os artigos de notícias.

### Classe NewsScraper
#### Inicialização
```python
class NewsScraper:
    def __init__(self, base_url: str = BASE_URL, termos: List[str] = TERMOS, max_pages: int = MAX_PAGES) -> None:
        self.all_news: List[List[str]] = []
        self.base_url = base_url
        self.termos = termos
        self.max_pages = max_pages
        self._setup_database()
```
- Inicializa o scraper com as configurações fornecidas e configura o banco de dados.

#### Configuração do Banco de Dados
```python
def _setup_database(self) -> None:
```
- Cria a tabela do banco de dados se ela não existir.

#### Obter Data da Notícia
```python
def get_news_date(self, news_url: str) -> Optional[str]:
```
- Extrai a data do artigo de notícias a partir de sua URL.

#### Scraping de Notícias Paginadas
```python
def scrape_paginated_news(self) -> None:
```
- Faz scraping de artigos de notícias de páginas paginadas e os filtra com base nos termos especificados.

#### Salvar no PostgreSQL
```python
def save_to_postgres(self) -> None:
```
- Salva os artigos de notícias filtrados no banco de dados PostgreSQL.

### Função Principal
```python
def main() -> None:
    scraper = NewsScraper()
    scraper.scrape_paginated_news()
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
```
- Inicializa a classe `NewsScraper` e aciona o processo de scraping e salvamento.

## Logging
- O script usa o módulo `logging` para registrar informações e erros.
- Os logs são salvos em um arquivo chamado `startups.log` e também são impressos no console.

## Conexão com o Banco de Dados
- O script usa uma classe personalizada `DatabaseConnection` do módulo `config.db_connection` para lidar com conexões de banco de dados.

## Pontos Importantes para Manutenção
- **Atualizar Termos**: Se novos termos precisarem ser adicionados para filtrar notícias, atualize a lista `TERMOS`.
- **Ajustar Máximo de Páginas**: Se mais páginas precisarem ser raspadas, atualize a constante `MAX_PAGES`.
- **Esquema do Banco de Dados**: Certifique-se de que o esquema do banco de dados corresponda à estrutura definida no método `_setup_database`.
- **Tratamento de Erros**: O script inclui tratamento básico de erros para requisições HTTP e operações de banco de dados. Certifique-se de que isso seja suficiente para seu caso de uso.
- **Logging**: Verifique o arquivo `startups.log` para logs detalhados e erros.

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
python scrape_startups_news.py
```