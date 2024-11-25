import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3


class BancoDeDados:
    """Gerencia o banco de dados para armazenar estatísticas de futebol."""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._criar_tabela()

    def _criar_tabela(self):
        """Cria a tabela no banco de dados."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatisticas (
            jogador TEXT,
            posicao TEXT,
            jogos INTEGER,
            gols INTEGER,
            assistencias INTEGER,
            cartoes_amarelos INTEGER,
            cartoes_vermelhos INTEGER
        )
        """)
        self.conn.commit()

    def inserir_dados(self, jogadores_data):
        """Insere os dados dos jogadores no banco."""
        self.cursor.executemany("""
            INSERT INTO estatisticas (jogador, posicao, jogos, gols, assistencias, cartoes_amarelos, cartoes_vermelhos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, jogadores_data)
        self.conn.commit()

    def consultar_dados(self, campo, ordem="DESC"):
        """Consulta dados do banco ordenados por um campo específico."""
        query = f"SELECT jogador, posicao, jogos, {campo} FROM estatisticas ORDER BY {campo} {ordem}"
        return pd.read_sql_query(query, self.conn)

    def fechar(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()


class ScraperTransfermarkt:
    """Gerencia o scraping de dados do site Transfermarkt."""
    
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def _extrair_estatisticas(self, jogador, indices_estatisticas):
        """Extrai estatísticas de um jogador."""
        dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
        if len(dados_jogador) >= 12:
            nome = dados_jogador[1]
            sobrenome = dados_jogador[2].split()[-1].strip()
            posicao = dados_jogador[3]
            jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
            estatisticas = [int(dados_jogador[i].split()[0]) if dados_jogador[i].split()[0].isdigit() else 0 for i in indices_estatisticas]

            # Corrigindo nomes específicos
            if dados_jogador[0] == "11":
                nome = "Rodrygo"
                sobrenome = ""
            if dados_jogador[1] == "JoseluJoseluCentroavante":
                nome = "Joselu"
                sobrenome = ""

            return [f"{nome.split()[0]} {sobrenome}", posicao, jogos, *estatisticas]
        return None

    def coletar_dados(self):
        """Realiza o scraping e retorna os dados processados."""
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        plantel = soup.select('table[class="items"] tbody tr')

        indices_estatisticas = [7, 8, 9, 11]
        jogadores_data = []

        for jogador in plantel:
            dados = self._extrair_estatisticas(jogador, indices_estatisticas)
            if dados:
                jogadores_data.append(dados)

        return jogadores_data


class EstatisticasManager:
    """Gerencia todo o processo de scraping e manipulação do banco de dados."""
    
    def __init__(self, url, headers, db_name):
        self.scraper = ScraperTransfermarkt(url, headers)
        self.banco = BancoDeDados(db_name)

    def executar(self):
        """Realiza o scraping, armazena os dados no banco e exibe os resultados."""
        # Coletando dados
        jogadores_data = self.scraper.coletar_dados()

        # Inserindo no banco
        self.banco.inserir_dados(jogadores_data)

        # Consultando os dados
        self._exibir_resultados("gols", "Artilharia do Clube - La Liga 2023/24")
        self._exibir_resultados("assistencias", "Maiores Assistentes do Clube - La Liga 2023/24")
        self._exibir_resultados("cartoes_amarelos", "Cartões Amarelos do Clube - La Liga 2023/24")
        self._exibir_resultados("cartoes_vermelhos", "Cartões Vermelhos do Clube - La Liga 2023/24")

        # Fechando conexão com o banco
        self.banco.fechar()

    def _exibir_resultados(self, campo, titulo):
        """Consulta e exibe os resultados de uma estatística específica."""
        print(f"\n\n{titulo}\n")
        df = self.banco.consultar_dados(campo)
        print(df.to_string(index=False))


# Configurações
URL = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=ES1%262023"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
DB_NAME = "dados_laLiga.db"

# Executando o programa
manager = EstatisticasManager(URL, HEADERS, DB_NAME)
manager.executar()
