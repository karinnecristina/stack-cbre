import os
import re
import logging
from typing import List, Optional
from datetime import datetime
from urllib.parse import quote
import requests
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from bs4 import BeautifulSoup
import sys

# Adiciona o diretório src ao caminho de pesquisa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from config.db_connection import DatabaseConnection

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("neofeed.log"), logging.StreamHandler()]
)


# Constantes
SEARCH_TERMS = ["Aporte", "Aportes", "Fusão", "Aquisição", "M&A", "Série A", "Série B", "Série C"]
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"}
TABLE_NAME = "neofeed"

class NewsScraper:
    def __init__(self) -> None:
        self.found_articles: List[List[str]] = []
        self.current_year = datetime.now().year
        self.previous_year = self.current_year - 1
        self._setup_database()

    def _setup_database(self) -> None:
        """Configura a conexão com o banco de dados e cria a tabela."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            titulo TEXT NOT NULL,
            resumo TEXT,
            termo TEXT NOT NULL,
            data DATE NOT NULL,
            CONSTRAINT unique_news UNIQUE (titulo, data)
        );
        """
        with DatabaseConnection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
                conn.commit()
        logging.info(f"Tabela {TABLE_NAME} verificada/criada com sucesso.")

    def fetch_news(self, term: str) -> None:
        """Busca notícias para um termo específico."""
        search_url = f"https://neofeed.com.br/?s={quote(term)}"
        logging.info(f"Buscando notícias para o termo: {term} ({search_url})")
        try:
            response = requests.get(search_url, headers=HEADERS)
            response.raise_for_status()
            self.parse_articles(response.text, term)
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao buscar notícias para '{term}': {e}")

    def parse_articles(self, page_content: str, term: str) -> None:
        """Extrai e processa artigos do HTML."""
        soup = BeautifulSoup(page_content, "html.parser")
        articles = soup.find_all("article")
        if not articles:
            logging.warning(f"Nenhum artigo encontrado para o termo: {term}")
            return
        for article in articles:
            title_tag = article.find("h3", class_="title-listagem")
            summary_tag = article.find("p")
            date_tag = article.find("span", class_="date")
            if title_tag and date_tag:
                title = title_tag.get_text(strip=True)
                summary = summary_tag.get_text(strip=True) if summary_tag else "Sem resumo"
                news_date = self._extract_date(date_tag.get_text(strip=True))
                if news_date:
                    self.check_and_append_article(title, summary, term, news_date)

    def _extract_date(self, date_str: str) -> Optional[str]:
        """Converte uma string de data para o formato aceito pelo PostgreSQL."""
        try:
            article_date = datetime.strptime(date_str, "%d/%m/%y")
            if article_date.year < 100:
                article_date = article_date.replace(year=2000 + article_date.year)
            return article_date.strftime("%Y-%m-%d")
        except ValueError:
            logging.warning(f"Formato de data inesperado: {date_str}")
            return None

    def check_and_append_article(self, title: str, summary: str, term: str, news_date: str) -> None:
        """Adiciona o artigo à lista se o termo estiver no título ou resumo e a data for do ano corrente ou anterior."""
        # Verifica se a data é do ano corrente ou do ano anterior
        article_year = datetime.strptime(news_date, "%Y-%m-%d").year
        if article_year == self.current_year or article_year == self.previous_year:
            if re.search(term, title, re.IGNORECASE) or re.search(term, summary, re.IGNORECASE):
                term = "Aporte" if term == "Aportes" else term
                self.found_articles.append([title, summary, term, news_date])
                logging.info(f"Notícia encontrada: {news_date}")
        else:
            pass

    def save_to_postgres(self) -> None:
        """Salva os artigos extraídos no banco de dados."""
        if not self.found_articles:
            logging.info("Nenhum artigo para salvar no banco de dados.")
            return
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (titulo, resumo, termo, data)
        VALUES %s
        ON CONFLICT (titulo, data) DO NOTHING;
        """
        with DatabaseConnection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, insert_query, self.found_articles)
                conn.commit()
        logging.info("Dados inseridos no banco de dados com sucesso.")


def main() -> None:
    scraper = NewsScraper()
    for term in SEARCH_TERMS:
        scraper.fetch_news(term)
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
