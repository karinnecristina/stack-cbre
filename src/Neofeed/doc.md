## Visão Geral
Este script é projetado para buscar artigos de notícias do site [Neofeed](https://neofeed.com.br/), filtrá-los com base em certos termos e armazenar os artigos relevantes em um banco de dados PostgreSQL. O script é estruturado em uma classe `NewsScraper` que lida com a busca, filtragem e operações de banco de dados.

## Estrutura do Arquivo
- **Imports**: O script importa bibliotecas necessárias para requisições HTTP, operações de banco de dados, logging e outras utilidades.
- **Constantes**: Define constantes como termos de busca, cabeçalhos HTTP e o nome da tabela do banco de dados.
- **Classe NewsScraper**: Contém métodos para inicializar o scraper, configurar o banco de dados, buscar notícias, analisar artigos e salvar dados no banco de dados.
- **Função Principal**: Inicializa a classe `NewsScraper` e aciona o processo de busca e salvamento.

## Componentes Principais

### Imports
- **requests**: Para fazer requisições HTTP.
- **BeautifulSoup**: Para analisar o conteúdo HTML.
- **psycopg2**: Para operações com o banco de dados PostgreSQL.
- **logging**: Para registrar informações e erros.
- **datetime**: Para manipulação de data e hora.
- **sys**: Para manipular o ambiente de execução do Python.

### Constantes
- **SEARCH_TERMS**: Lista de termos para filtrar artigos de notícias relevantes.
- **HEADERS**: Cabeçalhos HTTP para a requisição.
- **TABLE_NAME**: Nome da tabela do banco de dados para armazenar os artigos de notícias.

### Classe NewsScraper
#### Inicialização
```python
class NewsScraper:
    def __init__(self) -> None:
        self.found_articles: List[List[str]] = []
        self.current_year = datetime.now().year
        self.previous_year = self.current_year - 1
        self._setup_database()
```
- Inicializa o scraper com as configurações fornecidas e configura o banco de dados.

#### Configuração do Banco de Dados
```python
def _setup_database(self) -> None:
```
- Cria a tabela do banco de dados se ela não existir.

#### Buscar Notícias
```python
def fetch_news(self, term: str) -> None:
```
- Busca notícias para um termo específico.

#### Analisar Artigos
```python
def parse_articles(self, page_content: str, term: str) -> None:
```
- Extrai e processa artigos do HTML.

#### Extrair Data
```python
def _extract_date(self, date_str: str) -> Optional[str]:
```
- Converte uma string de data para o formato aceito pelo PostgreSQL.

#### Verificar e Adicionar Artigo
```python
def check_and_append_article(self, title: str, summary: str, term: str, news_date: str) -> None:
```
- Adiciona o artigo à lista se o termo estiver no título ou resumo e a data for do ano corrente ou anterior.

#### Salvar no PostgreSQL
```python
def save_to_postgres(self) -> None:
```
- Salva os artigos de notícias filtrados no banco de dados PostgreSQL.

### Função Principal
```python
def main() -> None:
    scraper = NewsScraper()
    for term in SEARCH_TERMS:
        scraper.fetch_news(term)
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
```
- Inicializa a classe `NewsScraper` e aciona o processo de busca e salvamento.

## Logging
- O script usa o módulo `logging` para registrar informações e erros.
- Os logs são salvos em um arquivo chamado `neofeed.log` e também são impressos no console.

## Conexão com o Banco de Dados
- O script usa uma classe personalizada `DatabaseConnection` do módulo `config.db_connection` para lidar com conexões de banco de dados.

## Pontos Importantes para Manutenção
- **Atualizar Termos**: Se novos termos precisarem ser adicionados para filtrar notícias, atualize a lista `SEARCH_TERMS`.
- **Esquema do Banco de Dados**: Certifique-se de que o esquema do banco de dados corresponda à estrutura definida no método `_setup_database`.
- **Tratamento de Erros**: O script inclui tratamento básico de erros para requisições HTTP e operações de banco de dados. Certifique-se de que isso seja suficiente para seu caso de uso.
- **Logging**: Verifique o arquivo `neofeed.log` para logs detalhados e erros.

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
python scrape_neofeed_news.py
```

Certifique-se de que o banco de dados PostgreSQL esteja configurado corretamente e que as credenciais de conexão estejam corretas no módulo `config.db_connection`.