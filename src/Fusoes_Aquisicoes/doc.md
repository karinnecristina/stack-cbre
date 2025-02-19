## Visão Geral
Este script é projetado para buscar notícias do site [Fusões & Aquisições](https://fusoesaquisicoes.com/destaques-do-dia/), extrair o conteúdo relevante e armazenar os dados em um banco de dados PostgreSQL. O script é estruturado em uma classe `NewsScraper` que lida com a coleta, análise e operações de banco de dados.

## Estrutura do Arquivo
- **Imports**: O script importa bibliotecas necessárias para requisições HTTP, operações de banco de dados, logging e outras utilidades.
- **Constantes**: Define constantes como a URL base, limite de data, número máximo de páginas e o nome da tabela do banco de dados.
- **Classe NewsScraper**: Contém métodos para inicializar o scraper, configurar o banco de dados, extrair conteúdo completo, extrair dados de notícias e salvar dados no banco de dados.
- **Função Principal**: Inicializa a classe `NewsScraper` e aciona o processo de busca e salvamento.

## Componentes Principais

### Imports
- **cloudscraper**: Para fazer requisições HTTP que contornam proteções de sites.
- **BeautifulSoup**: Para analisar o conteúdo HTML.
- **psycopg2**: Para operações com o banco de dados PostgreSQL.
- **logging**: Para registrar informações e erros.
- **datetime**: Para manipulação de data e hora.
- **sys**: Para manipular o ambiente de execução do Python.

### Constantes
- **BASE_URL**: A URL base para buscar as notícias.
- **DATA_LIMIT**: Limite de data para filtrar notícias.
- **MAX_PAGES**: Número máximo de páginas a serem raspadas.
- **TABLE_NAME**: Nome da tabela do banco de dados para armazenar os dados de notícias.

### Classe NewsScraper
#### Inicialização
```python
class NewsScraper:
    def __init__(self, base_url: str, max_pages: int = MAX_PAGES) -> None:
        self.base_url = base_url
        self.max_pages = max_pages
        self.news: List[List[str]] = []
        self.scraper = cloudscraper.create_scraper()
        self._setup_database()
```
- Inicializa o scraper com as configurações fornecidas e configura o banco de dados.

#### Configuração do Banco de Dados
```python
def _setup_database(self) -> None:
```
- Cria a tabela do banco de dados se ela não existir.

#### Extrair Conteúdo Completo
```python
def extract_full_content(self, article_url: str) -> str:
```
- Extrai o conteúdo completo de um artigo.

#### Extrair Dados
```python
def extract_data(self, url: str) -> Optional[List[List[str]]]:
```
- Extrai os dados das notícias da página fornecida.

#### Salvar no PostgreSQL
```python
def save_to_postgres(self) -> None:
```
- Salva os dados extraídos no banco de dados PostgreSQL.

#### Executar o Scraper
```python
def run(self) -> None:
```
- Executa o scraper para coletar e armazenar as notícias.

### Função Principal
```python
def main() -> None:
    scraper = NewsScraper(BASE_URL)
    scraper.run()

if __name__ == "__main__":
    main()
```
- Inicializa a classe scrape_fusoes_aquisicoes.py  e aciona o processo de busca e salvamento.

## Logging
- O script usa o módulo scrape_fusoes_aquisicoes.py  para registrar informações e erros.
- Os logs são salvos em um arquivo chamado `fusoes_aquisicoes.log` e também são impressos no console.

## Conexão com o Banco de Dados
- O script usa uma classe personalizada scrape_fusoes_aquisicoes.py  do módulo scrape_fusoes_aquisicoes.py  para lidar com conexões de banco de dados.

## Pontos Importantes para Manutenção
- **Atualizar Limite de Data**: Se o limite de data precisar ser ajustado, atualize a constante scrape_fusoes_aquisicoes.py .
- **Ajustar Máximo de Páginas**: Se mais páginas precisarem ser raspadas, atualize a constante scrape_fusoes_aquisicoes.py .
- **Esquema do Banco de Dados**: Certifique-se de que o esquema do banco de dados corresponda à estrutura definida no método scrape_fusoes_aquisicoes.py .
- **Tratamento de Erros**: O script inclui tratamento básico de erros para requisições HTTP e operações de banco de dados. Certifique-se de que isso seja suficiente para seu caso de uso.
- **Logging**: Verifique o arquivo `fusoes_aquisicoes.log` para logs detalhados e erros.

## Instalação e Execução

### Instalação das Bibliotecas
Para instalar as bibliotecas necessárias, você pode usar o `pip` e o arquivo `requirements.txt` que deve conter todas as dependências. Crie um arquivo `requirements.txt` com o seguinte conteúdo:

```text
cloudscraper
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
python scrape_fusoes_aquisicoes.py
```

Certifique-se de que o banco de dados PostgreSQL esteja configurado corretamente e que as credenciais de conexão estejam corretas no módulo scrape_fusoes_aquisicoes.py .