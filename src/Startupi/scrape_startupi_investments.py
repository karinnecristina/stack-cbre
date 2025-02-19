import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import quote

import requests
import psycopg2
from psycopg2.extras import execute_values
from bs4 import BeautifulSoup

# Adiciona o diretório src ao caminho de pesquisa
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))
from config.db_connection import DatabaseConnection

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("startupi.log"), logging.StreamHandler()]
)

# Constantes
MES_NUMERAL = {
    "JAN": "01", "FEV": "02", "MAR": "03", "ABR": "04", "MAI": "05", "JUN": "06",
    "JUL": "07", "AGO": "08", "SET": "09", "OUT": "10", "NOV": "11", "DEZ": "12"
}
TABLE_NAME = "startupi"
BASE_URL = "https://startupi.com.br/ranking-investimentos-{}/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

class InvestmentScraper:
    """Classe para coletar e processar investimentos do Startupi."""

    def __init__(self, start_year: int = 2022) -> None:
        self.all_news_investments: List[Dict[str, str]] = []
        self.start_year = start_year
        self.end_year = datetime.now().year - 1
        self._setup_database()

    def _setup_database(self) -> None:
        """Configura a conexão com o banco de dados e cria a tabela se necessário."""
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            resumo TEXT,
            data DATE NOT NULL,
            CONSTRAINT unique_news_investment UNIQUE (resumo, data)
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

    def get_page_content(self, url: str) -> Optional[str]:
        """Obtém o conteúdo HTML da página especificada."""
        try:
            logging.info(f"Acessando a página: {url}")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar {url}: {e}")
            return None

    def parse_content(self, html: str, year: int) -> List[Dict[str, str]]:
        """Extrai os textos organizados por mês e ano, formatando a data."""
        soup = BeautifulSoup(html, "html.parser")
        month_elements = soup.select(".elementor-tab-title.elementor-tab-desktop-title")
        investments = []

        for month in month_elements:
            month_name = month.get_text(strip=True).upper()
            month_num = MES_NUMERAL.get(month_name)
            if not month_num:
                logging.warning(f"Mês não reconhecido: {month_name}")
                continue

            content_id = month.get("aria-controls")
            content_section = soup.find("div", {"id": content_id})

            if content_section:
                text = content_section.get_text(separator=" ").strip()
                data_formatada = f"01/{month_num}/{year}"
                investments.append({"resumo": text, "data": data_formatada})

        return investments

    def scrape_investments(self) -> None:
        """Executa o fluxo completo para coletar os dados dos investimentos."""
        for year in range(self.start_year, self.end_year + 1):
            url = BASE_URL.format(year)
            html_content = self.get_page_content(url)

            if html_content:
                investment_data = self.parse_content(html_content, year)
                self.all_news_investments.extend(investment_data)
            else:
                logging.warning(f"Pulando ano {year} devido a erro na página.")

        logging.info("Scraping concluído.")

    def save_to_postgres(self) -> None:
        """Salva os artigos extraídos no banco de dados."""
        if not self.all_news_investments:
            logging.info("Nenhum artigo para salvar no banco de dados.")
            return

        data_to_insert = [(news["resumo"], news["data"]) for news in self.all_news_investments]
        insert_query = f"""
        INSERT INTO {TABLE_NAME} (resumo, data)
        VALUES %s
        ON CONFLICT (resumo, data) DO NOTHING;
        """

        try:
            with DatabaseConnection() as conn:
                with conn.cursor() as cursor:
                    execute_values(cursor, insert_query, data_to_insert)
                    conn.commit()
            logging.info("Dados inseridos no banco de dados com sucesso.")
        except psycopg2.DatabaseError as e:
            logging.error(f"Erro ao salvar dados no banco: {e}")


def main() -> None:
    """Função principal para executar o scraper e salvar os dados."""
    scraper = InvestmentScraper(start_year=2022)
    scraper.scrape_investments()
    scraper.save_to_postgres()

if __name__ == "__main__":
    main()
