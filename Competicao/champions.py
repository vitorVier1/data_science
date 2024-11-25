import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd


class EstatisticasClube:
    def __init__(self, url, headers, db_name="dados_championsLeague.db"):
        self.url = url
        self.headers = headers
        self.db_name = db_name
        self.conexao = self._criar_conexao()
        self._criar_tabela()

    def _criar_conexao(self):
        return sqlite3.connect(self.db_name)

    def _criar_tabela(self):
        cursor = self.conexao.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatisticas_clube (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogador TEXT,
            posicao TEXT,
            jogos INTEGER,
            gols INTEGER,
            assistencias INTEGER,
            amarelos INTEGER,
            vermelhos INTEGER
        )
        """)
        self.conexao.commit()

    def obter_dados(self):
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        plantel = soup.select('table[class="items"] tbody tr')

        jogadores_data = []
        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
            
            if len(dados_jogador) >= 12:
                nome = dados_jogador[1]
                sobreNome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
                gols = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0
                assistencias = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0
                amarelos = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0
                vermelhos = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0

                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobreNome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobreNome = ""

                jogadores_data.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, gols, assistencias, amarelos, vermelhos])

        return jogadores_data

    def salvar_dados(self, jogadores_data):
        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM estatisticas_clube")  # Limpa os dados antigos
        for linha in jogadores_data:
            cursor.execute("""
            INSERT INTO estatisticas_clube (jogador, posicao, jogos, gols, assistencias, amarelos, vermelhos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, linha)
        self.conexao.commit()

    def exibir_dados(self, tipo):
        cursor = self.conexao.cursor()
        if tipo == "gols":
            query = "SELECT jogador, posicao, jogos, gols FROM estatisticas_clube ORDER BY gols DESC"
            titulo = "Artilharia do Clube - Liga dos Campeões da Europa 2023/24"
            colunas = ["Jogador", "Posição", "Jogos", "Gols"]
        elif tipo == "assistencias":
            query = "SELECT jogador, posicao, jogos, assistencias FROM estatisticas_clube ORDER BY assistencias DESC"
            titulo = "Maiores Assistentes do Clube - Liga dos Campeões da Europa 2023/24"
            colunas = ["Jogador", "Posição", "Jogos", "Assistências"]
        elif tipo == "amarelos":
            query = "SELECT jogador, posicao, jogos, amarelos FROM estatisticas_clube ORDER BY amarelos DESC"
            titulo = "Cartões Amarelos do Clube - Liga dos Campeões da Europa 2023/24"
            colunas = ["Jogador", "Posição", "Jogos", "Cartões Amarelos"]
        elif tipo == "vermelhos":
            query = "SELECT jogador, posicao, jogos, vermelhos FROM estatisticas_clube ORDER BY vermelhos DESC"
            titulo = "Cartões Vermelhos do Clube - Liga dos Campeões da Europa 2023/24"
            colunas = ["Jogador", "Posição", "Jogos", "Cartões Vermelhos"]
        else:
            print("Tipo inválido.")
            return

        cursor.execute(query)
        resultados = cursor.fetchall()
        df = pd.DataFrame(resultados, columns=colunas)

        print(f"\n{titulo}\n")
        print(df.to_string(index=False))
        print("\n" + "-" * 150)

    def fechar_conexao(self):
        self.conexao.close()


# URL e headers para requisição
url = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=CL%262023"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

# Instanciando a classe
estatisticas = EstatisticasClube(url, headers)

# Coletando e salvando dados no banco
jogadores_data = estatisticas.obter_dados()
estatisticas.salvar_dados(jogadores_data)

# Exibindo as tabelas
estatisticas.exibir_dados("gols")
estatisticas.exibir_dados("assistencias")
estatisticas.exibir_dados("amarelos")
estatisticas.exibir_dados("vermelhos")

# Fechando a conexão
estatisticas.fechar_conexao()
