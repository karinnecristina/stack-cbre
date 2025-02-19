import os
import requests
from bs4 import BeautifulSoup
import time
import csv
import logging
from datetime import datetime
import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values
from typing import List, Optional
import sys

# Adiciona o diretório src ao caminho de pesquisa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from config.db_connection import DatabaseConnection


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("startups.log"), logging.StreamHandler()]
)

# Constantes
BASE_URL = "https://startups.com.br/ultimas-noticias/page/"
TERMOS = ["Aporte", "Fusão", "Aquisição", "M&A", "Série A", "Série B", "Série C"]
MAX_PAGES = 2
TABLE_NAME = "startups"

class NewsScraper:
    def __init__(self, base_url: str = BASE_URL, termos: List[str] = TERMOS, max_pages: int = MAX_PAGES) -> None:
        """
        Inicializa o scraper com as configurações fornecidas.
        """
        self.all_news: List[List[str]] = []
        self.base_url = base_url
        self.termos = termos
        self.max_pages = max_pages
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
            CONSTRAINT unique_titulo_data UNIQUE (titulo, data)
        );
        """
        with DatabaseConnection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
                conn.commit()
        logging.info(f"Tabela {TABLE_NAME} verificada/criada com sucesso.")

    def get_news_date(self, news_url: str) -> Optional[str]:
        """
        Obtém a data de uma notícia a partir de sua URL.

        :param news_url: URL da notícia.
        :return: Data da notícia no formato "DD/MM/YYYY" ou None em caso de erro.
        """
        try:
            response = requests.get(news_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            time_element = soup.find("time", class_="text-gray-500")
            if time_element and time_element.get("datetime"):
                date_time = time_element["datetime"]
                date_object = datetime.fromisoformat(date_time)
                return date_object.strftime("%d/%m/%Y")
            else:
                logging.warning(f"Data não encontrada para a notícia: {news_url}")
                return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar a página da notícia {news_url}: {e}")
            return None

    def scrape_paginated_news(self) -> None:
        """
        Realiza o scraping das notícias paginadas e filtra as relevantes com base nos termos especificados.

        :return: Lista de notícias encontradas.
        """
        all_news = []
        page = 1

        while page <= self.max_pages:
            url = f"{self.base_url}{page}/"
            logging.info(f"Acessando página {page}...")

            try:
                response = requests.get(url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser")
                grid_div = soup.find("div", class_="grid gap-row-6")

                if grid_div:
                    news_links = grid_div.find_all("a", class_="feed-link")

                    if not news_links:
                        logging.info(f"Sem mais notícias relevantes na página {page}. Encerrando...")
                        break

                    for link in news_links:
                        title = link.get("title")
                        news_url = link.get("href")
                        summary_element = link.find_next("p", class_="feed-excert feed-excert-md line-clamp-3")

                        if title and news_url:
                            for term in self.termos:
                                if term.lower() in title.lower():
                                    logging.info(f"Termo encontrado: {term}")

                                    news_date = self.get_news_date(news_url)
                                    article_date = datetime.strptime(news_date, "%d/%m/%Y").strftime("%Y-%m-%d")
                                    news_summary = summary_element.get_text(strip=True) if summary_element else "Resumo não encontrado"

                                    self.all_news.append({
                                        "titulo": title,
                                        "resumo": news_summary,
                                        "termo": term,
                                        "data": article_date
                                    })
                                    break

                else:
                    logging.warning(f"Elemento 'grid gap-row-6' não encontrado na página {page}. Pulando para a próxima página.")

                page += 1
                time.sleep(2)

            except requests.exceptions.RequestException as e:
                logging.error(f"Erro ao acessar a página {url}: {e}")
                break

        logging.info(f"Total de notícias encontradas: {len(self.all_news)}")
        if self.all_news:
            logging.info(f"Exemplo de notícia: {self.all_news[0]}")

        logging.info("Scraping concluído.")

    def save_to_postgres(self) -> None:
        """Salva os artigos extraídos no banco de dados."""
        if not self.all_news:
            logging.info("Nenhum artigo para salvar no banco de dados.")
            return

        # Transformando a lista de dicionários em uma lista de tuplas
        data_to_insert = [
            (news["titulo"], news["resumo"], news["termo"], news["data"])
            for news in self.all_news
        ]

        insert_query = f"""
        INSERT INTO {TABLE_NAME} (titulo, resumo, termo, data)
        VALUES %s
        ON CONFLICT (titulo, data) DO NOTHING;
        """
        with DatabaseConnection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, insert_query, data_to_insert)
                conn.commit()
        logging.info("Dados inseridos no banco de dados com sucesso.")


def main() -> None:
    scraper = NewsScraper()
    scraper.scrape_paginated_news()
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
