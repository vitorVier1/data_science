import requests
from bs4 import BeautifulSoup
import pandas as pd


class EstatisticasClube:
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers
        self.plantel = []
        self.jogadores_data = []

    def obter_dados(self):
        """
        Faz a requisição ao site e obtém os dados da página HTML.
        """
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        self.plantel = soup.select('table[class="items"] tbody tr')

    def processar_dados(self, tipo="gols"):
        """
        Processa os dados do plantel com base no tipo de estatística escolhida.
        :param tipo: Tipo de estatística ("gols", "assistencias", "amarelos", "vermelhos").
        """
        self.jogadores_data = []

        for jogador in self.plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]

            if len(dados_jogador) >= 12:
                nome = dados_jogador[1]
                sobreNome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0

                if tipo == "gols":
                    estatistica = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0
                elif tipo == "assistencias":
                    estatistica = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0
                elif tipo == "amarelos":
                    estatistica = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0
                elif tipo == "vermelhos":
                    estatistica = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0
                else:
                    estatistica = 0

                # Correções para casos especiais
                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobreNome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobreNome = ""

                self.jogadores_data.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, estatistica])

    def exibir_tabela(self, titulo, coluna_estatistica):
        """
        Exibe os dados processados em formato tabular.
        :param titulo: Título da tabela.
        :param coluna_estatistica: Nome da coluna que contém a estatística.
        """
        df = pd.DataFrame(self.jogadores_data, columns=["Jogador", "Posição", "Jogos", coluna_estatistica])
        df = df.sort_values(by=coluna_estatistica, ascending=False).reset_index(drop=True)

        print(f"\n{titulo}\n")
        print(df.to_string(index=False))
        print("\n" + "-" * 150)


# URL e headers para requisição
url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=CDR%262023"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# Inicializando a classe
estatisticas = EstatisticasClube(url, headers)

# Obter dados da página
estatisticas.obter_dados()

# Processar e exibir tabelas
estatisticas.processar_dados(tipo="gols")
estatisticas.exibir_tabela("Artilharia do Clube - Copa do Rei 2023/24", "Gols")

estatisticas.processar_dados(tipo="assistencias")
estatisticas.exibir_tabela("Maiores Assistentes do Clube - Copa do Rei 2023/24", "Assistencias")

estatisticas.processar_dados(tipo="amarelos")
estatisticas.exibir_tabela("Cartões Amarelos do Clube - Copa do Rei 2023/24", "Cartões Amarelos")

estatisticas.processar_dados(tipo="vermelhos")
estatisticas.exibir_tabela("Cartões Vermelhos do Clube - Copa do Rei 2023/24", "Cartões Vermelhos")
