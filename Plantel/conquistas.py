import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

class RealMadridSeasonStats:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        self.soup = None
        self.competitions_table = PrettyTable(field_names=["Competição", "Resultado"])
        self.games_table = PrettyTable(field_names=["Jogos", "V", "E", "D"])

    def fetch_data(self):
        """Faz o scraping da página e cria o objeto BeautifulSoup."""
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, "html.parser")
        else:
            raise Exception(f"Erro ao acessar a URL. Status Code: {response.status_code}")

    def extract_competitions(self):
        """Extrai o balanço das competições."""
        balanco = self.soup.select('div[class="box saison-bilanz"] table tbody')
        if balanco:
            for comp in balanco:
                dados_comp = [tr.text.strip() for tr in comp.find_all('tr') if tr.text.strip()]
                
                if len(dados_comp) >= 4:
                    copaRei = dados_comp[0].split()[3]
                    champions = dados_comp[1].split()[2] if len(dados_comp) > 4 else "Campeão"
                    laLiga = dados_comp[2] if len(dados_comp) > 4 else "Campeão"
                    superCopa = dados_comp[3] if len(dados_comp) > 4 else "Campeão"

                    # Adicionando dados à tabela
                    self.competitions_table.add_row(["Copa do Rei", copaRei])
                    self.competitions_table.add_row(["Liga dos Campeões", champions])
                    self.competitions_table.add_row(["La Liga", laLiga])
                    self.competitions_table.add_row(["Super Copa", superCopa])

    def extract_games(self):
        """Extrai os dados de jogos da temporada."""
        jogos = self.soup.select('div[class="box box-slider"] ul li div[class="container-content"] div[class="container-match-record"] table tr')
        if jogos:
            for stats in jogos:
                jogos_stats = [td.text.strip() for td in stats.find_all('td') if td.text.strip()]
                
                if len(jogos_stats) >= 4:
                    jogos = jogos_stats[0].split('Jogos')[0]
                    wins = jogos_stats[1].split('V')[0]
                    draws = jogos_stats[2].split('E')[0]
                    loses = jogos_stats[3].split('D')[0]

                    # Adicionando dados à tabela
                    self.games_table.add_row([jogos, wins, draws, loses])

    def display_results(self):
        """Exibe os resultados das competições e dos jogos."""
        print("\nBalanço da Temporada 2023/24\n")
        print("Competições")
        print(self.competitions_table)
        print("\n---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
        print("Jogos da Temporada")
        print(self.games_table)

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
