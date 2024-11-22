import requests
from bs4 import BeautifulSoup
import pandas as pd

class RealMadridStats:
    def __init__(self, url):
        self.url = url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        self.soup = None
        self.jogadores_data = []

    def fetch_data(self):
        """Faz a requisição e armazena o conteúdo HTML da página."""
        response = requests.get(self.url, headers=self.headers)
        if response.status_code == 200:
            self.soup = BeautifulSoup(response.content, "html.parser")
        else:
            raise Exception("Erro ao acessar a página.")

    def collect_player_stats(self):
        """Coleta os dados dos jogadores do plantel e armazena na lista jogadores_data."""
        plantel = self.soup.select('table[class="items"] tbody tr')
        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]

            if len(dados_jogador) >= 12:  # Verifica se existem dados suficientes
                num = dados_jogador[0]
                nome = dados_jogador[1]
                sobreNome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                noPlantel = dados_jogador[5][0]
                jogos = dados_jogador[6] if len(dados_jogador) > 7 else "-"  # Podem não haver dados cadastrados
                gols = dados_jogador[7].split()[0]
                ass = dados_jogador[8].split()[0]
                amarelos = dados_jogador[9].split()[0]
                amarelos2 = dados_jogador[10].split()[0]
                vermelhos = dados_jogador[11].split()[0]
                ppj = dados_jogador[14].split()[0]
                minJogados = dados_jogador[15].split()[0]

                # Correção para casos específicos de nomes de jogadores
                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobreNome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobreNome = ""

                # Adicionando os dados coletados à lista
                self.jogadores_data.append([num, f"{nome.split()[0]} {sobreNome}", posicao, noPlantel, jogos, gols, ass, amarelos, amarelos2, vermelhos, ppj, minJogados])

    def create_dataframe(self):
        """Cria um DataFrame com os dados coletados."""
        return pd.DataFrame(self.jogadores_data, columns=[
            "Numero", "Nome", "Posicao", "No Plantel", "Jogos", "Gols", "Assistencias", "Amarelos", 
            "Expulsões (2 Amarelos)", "Vermelhos", "PPJ", "Minutos Jogados"
        ])

    def display_stats(self):
        """Exibe as estatísticas gerais do plantel."""
        df_jogadores = self.create_dataframe()
        print("\n\n\nEstatisticas Gerais do Plantel na Temporada 2023/24\n")
        print(df_jogadores.to_string(index=False))


# Exemplo de uso:
url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/reldata/%262023/plus/1"

# Instancia a classe e coleta os dados
real_madrid_stats = RealMadridStats(url)
real_madrid_stats.fetch_data()  # Coleta os dados da página
real_madrid_stats.collect_player_stats()  # Coleta as estatísticas dos jogadores
real_madrid_stats.display_stats()  # Exibe as estatísticas na forma de tabela
