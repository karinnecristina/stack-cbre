# Autor: Karinne Cristina
# Data: 2025-02-19
# Descrição: Script para extração de notícias do site Fusões & Aquisições e salvamento no banco de dados.
import logging
import os
import sys
import locale
from datetime import datetime
from typing import List, Optional

import cloudscraper
import psycopg2
from bs4 import BeautifulSoup
from psycopg2.extras import execute_values

# Adiciona o caminho do diretório src para importar módulos personalizados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from config.db_connection import DatabaseConnection

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("fusoes_aquisicoes.log"), logging.StreamHandler()]
)

# Constantes globais
BASE_URL: str = 'https://fusoesaquisicoes.com/destaques-do-dia/page/'
DATA_LIMIT: datetime.date = datetime(2023, 12, 30).date()
MAX_PAGES: int = 1
TABLE_NAME: str = "fusoes_aquisicoes"
locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

class NewsScraper:
    def __init__(self, base_url: str, max_pages: int = MAX_PAGES) -> None:
        self.base_url = base_url
        self.max_pages = max_pages
        self.news: List[List[str]] = []
        self.scraper = cloudscraper.create_scraper()
        self._setup_database()

    def _setup_database(self) -> None:
        """Cria a tabela no banco de dados se não existir."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            titulo TEXT,
            resumo TEXT,
            data DATE NOT NULL,
            CONSTRAINT unique_news_fusoes UNIQUE (titulo, data)
        );
        """
        try:
            with DatabaseConnection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(create_table_query)
                    conn.commit()
            logging.info(f"Tabela {TABLE_NAME} verificada/criada com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao configurar banco de dados: {e}")

    def extract_full_content(self, article_url: str) -> str:
        """Extrai o conteúdo completo de um artigo."""
        try:
            response = self.scraper.get(article_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find('div', class_='content post-excerpt entry-content clearfix')

            if content:
                full_text = content.get_text(strip=True)
                start_delimiter = "INSIGHT DO DIA: Humores & Rumores"
                end_delimiter = "Saiba quais são as mais recentespostagens de humores e rumoresdo mercado"

                if start_delimiter in full_text:
                    full_text = full_text.split(start_delimiter, 1)[-1]
                full_text = full_text.split(end_delimiter)[0]
            else:
                logging.warning("Conteúdo não encontrado na div com a classe especificada.")
                return "Conteúdo não encontrado"

            return full_text
        except Exception as e:
            logging.error(f"Erro ao acessar o artigo {article_url}: {e}")
            return ""

    def extract_data(self, url: str) -> Optional[List[List[str]]]:
        """Extrai os dados das notícias da página fornecida."""
        try:
            response = self.scraper.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')

            data: List[List[str]] = []
            for article in articles:
                summary_element = article.find('div', class_='post-excerpt')
                date_element = article.find('time', class_='entry-date')
                link_element = article.find('a', href=True)

                if not summary_element or not date_element or not link_element:
                    continue

                summary = summary_element.get_text(strip=True)
                date_str = date_element.get_text(strip=True)
                article_link = link_element['href']

                try:
                    publish_date = datetime.strptime(date_str, '%d de %B de %Y').date()
                except ValueError:
                    logging.error(f'Erro ao processar a data: {date_str}')
                    continue

                if publish_date <= DATA_LIMIT:
                    logging.info(f"Encontrada notícia com data anterior ao limite ({DATA_LIMIT}). Parando a extração.")
                    return None

                full_text = self.extract_full_content(article_link)
                data.append([summary, full_text, publish_date])

            return data if data else None
        except Exception as e:
            logging.error(f'Erro ao acessar a página {url}: {e}')
            return None

    def save_to_postgres(self) -> None:
        """Salva os dados extraídos no banco de dados."""
        if not self.news:
            logging.info("Nenhum artigo para salvar no banco de dados.")
            return
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (titulo, resumo, data)
        VALUES %s
        ON CONFLICT (titulo, data) DO NOTHING;
        """
        try:
            with DatabaseConnection() as conn:
                with conn.cursor() as cursor:
                    execute_values(cursor, insert_query, self.news)
                    conn.commit()
            logging.info("Dados inseridos no banco de dados com sucesso.")
        except Exception as e:
            logging.error(f"Erro ao inserir dados no banco de dados: {e}")

    def run(self) -> None:
        """Executa o scraper para coletar e armazenar as notícias."""
        self.news = []
        for page in range(1, self.max_pages + 1):
            page_url = f'{self.base_url}{page}/'
            data = self.extract_data(page_url)

            if data is None:
                break

            self.news.extend(data)
            logging.info(f'Página {page} processada.')

        if self.news:
            logging.info("Extração de dados concluída com sucesso.")
            self.save_to_postgres()
        else:
            logging.warning("Nenhum dado extraído.")


def main() -> None:
    scraper = NewsScraper(BASE_URL)
    scraper.run()

if __name__ == "__main__":
    main()
