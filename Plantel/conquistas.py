import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd

class RealMadridSeasonStats:
    def __init__(self, url, db_name="conquistas.db"):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        self.soup = None
        self.db_name = db_name
        
        # Criação e conexão com o banco de dados SQLite
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        # Criando as tabelas no banco de dados (caso ainda não existam)
        self.create_tables()

    def create_tables(self):
        """Cria as tabelas no banco de dados caso ainda não existam."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS competicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competencia TEXT NOT NULL UNIQUE,
            resultado TEXT NOT NULL
        )
        """)
        
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogos TEXT NOT NULL UNIQUE,
            v INTEGER NOT NULL,
            e INTEGER NOT NULL,
            d INTEGER NOT NULL
        )
        """)

    def fetch_data(self):
        """Faz o scraping da página e cria o objeto BeautifulSoup."""
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, "html.parser")
        else:
            raise Exception(f"Erro ao acessar a URL. Status Code: {response.status_code}")

    def extract_competitions(self):
        """Extrai o balanço das competições e armazena no banco de dados."""
        balanco = self.soup.select('div[class="box saison-bilanz"] table tbody')
        if balanco:
            for comp in balanco:
                dados_comp = [tr.text.strip() for tr in comp.find_all('tr') if tr.text.strip()]
                
                if len(dados_comp) >= 4:
                    copaRei = dados_comp[0].split()[3]
                    champions = dados_comp[1].split()[2] if len(dados_comp) > 4 else "Campeão"
                    laLiga = dados_comp[2] if len(dados_comp) > 4 else "Campeão"
                    superCopa = dados_comp[3] if len(dados_comp) > 4 else "Campeão"

                    # Inserindo os dados na tabela competicoes
                    self.cursor.execute("INSERT OR IGNORE INTO competicoes (competencia, resultado) VALUES (?, ?)", 
                                        ("Copa do Rei", copaRei))
                    self.cursor.execute("INSERT OR IGNORE INTO competicoes (competencia, resultado) VALUES (?, ?)", 
                                        ("Liga dos Campeões", champions))
                    self.cursor.execute("INSERT OR IGNORE INTO competicoes (competencia, resultado) VALUES (?, ?)", 
                                        ("La Liga", laLiga))
                    self.cursor.execute("INSERT OR IGNORE INTO competicoes (competencia, resultado) VALUES (?, ?)", 
                                        ("Super Copa", superCopa))
                    
            self.conn.commit()

    def extract_games(self):
        """Extrai os dados de jogos da temporada e armazena no banco de dados."""
        jogos = self.soup.select('div[class="box box-slider"] ul li div[class="container-content"] div[class="container-match-record"] table tr')
        if jogos:
            for stats in jogos:
                jogos_stats = [td.text.strip() for td in stats.find_all('td') if td.text.strip()]
                
                if len(jogos_stats) >= 4:
                    jogos = jogos_stats[0].split('Jogos')[0]
                    
                    # Verificando se os valores não estão vazios antes de converter para int
                    wins = jogos_stats[1].split('V')[0]
                    draws = jogos_stats[2].split('E')[0]
                    loses = jogos_stats[3].split('D')[0]

                    # Inserindo os dados na tabela jogos
                    self.cursor.execute("INSERT OR IGNORE INTO jogos (jogos, v, e, d) VALUES (?, ?, ?, ?)", 
                                        (jogos, wins, draws, loses))

            self.conn.commit()

    def display_results(self):
        """Consulta os dados no banco de dados e exibe os resultados."""
        # Consultando as competições
        self.cursor.execute("SELECT competencia, resultado FROM competicoes")
        competicoes = self.cursor.fetchall()

        print("\nBalanço da Temporada 2023/24\n")
        print("Competições")
        for comp in competicoes:
            print(f"{comp[0]}: {comp[1]}")
        
        print("\n---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
        
        # Consultando os jogos
        self.cursor.execute("SELECT jogos, v, e, d FROM jogos")
        jogos = self.cursor.fetchall()

        print("Jogos da Temporada")
        for jogo in jogos:
            print(f"Jogos: {jogo[0]} | V: {jogo[1]} | E: {jogo[2]} | D: {jogo[3]}")

    def close_connection(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()

# Uso da classe
if __name__ == "__main__":
    url = "https://www.transfermarkt.com.br/real-madrid/startseite/verein/418/saison_id/2023"
    real_madrid_stats = RealMadridSeasonStats(url)
    
    try:
        real_madrid_stats.fetch_data()
        real_madrid_stats.extract_competitions()
        real_madrid_stats.extract_games()
        real_madrid_stats.display_results()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        real_madrid_stats.close_connection()
