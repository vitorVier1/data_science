import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

class BancoDeDados:
    """Classe para gerenciar a interação com o banco de dados SQLite."""
    
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self._criar_tabelas()

    def _criar_tabelas(self):
        """Cria as tabelas para armazenar as estatísticas dos jogadores."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatisticas (
            jogador TEXT,
            posicao TEXT,
            jogos INTEGER,
            gols INTEGER,
            assistencias INTEGER,
            amarelos INTEGER,
            vermelhos INTEGER
        )
        """)
        self.conn.commit()

    def inserir_estatisticas(self, dados):
        """Insere os dados de estatísticas no banco de dados."""
        self.cursor.executemany("""
            INSERT INTO estatisticas (jogador, posicao, jogos, gols, assistencias, amarelos, vermelhos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, dados)
        self.conn.commit()

    def consultar_estatisticas(self):
        """Consulta os dados de estatísticas no banco de dados."""
        query = "SELECT * FROM estatisticas"
        return pd.read_sql_query(query, self.conn)

    def fechar(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()


class ScraperTransfermarkt:
    """Classe responsável por realizar o scraping dos dados do Transfermarkt."""
    
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def coletar_dados_estatisticos(self, estatistica):
        """Coleta os dados estatísticos do site Transfermarkt."""
        dados_estatisticos = []
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        plantel = soup.select('table[class="items"] tbody tr')
        
        for jogador in plantel:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
            
            if len(dados_jogador) >= 12:
                nome = dados_jogador[1]
                sobreNome = dados_jogador[2].split()[-1].strip()
                posicao = dados_jogador[3]
                jogos = int(dados_jogador[6]) if dados_jogador[6].isdigit() else 0
                
                # Ajustes de nome para Rodrygo e Joselu
                if dados_jogador[0] == "11":
                    nome = "Rodrygo"
                    sobreNome = ""
                if dados_jogador[1] == "JoseluJoseluCentroavante":
                    nome = "Joselu"
                    sobreNome = ""
                
                if estatistica == 'gols':
                    valor = int(dados_jogador[7].split()[0]) if dados_jogador[7].split()[0].isdigit() else 0
                    dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, valor, 0, 0, 0])
                elif estatistica == 'assistencias':
                    valor = int(dados_jogador[8].split()[0]) if dados_jogador[8].split()[0].isdigit() else 0
                    dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, 0, valor, 0, 0])
                elif estatistica == 'amarelos':
                    valor = int(dados_jogador[9].split()[0]) if dados_jogador[9].split()[0].isdigit() else 0
                    dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, 0, 0, valor, 0])
                elif estatistica == 'vermelhos':
                    valor = int(dados_jogador[11].split()[0]) if dados_jogador[11].split()[0].isdigit() else 0
                    dados_estatisticos.append([f"{nome.split()[0]} {sobreNome}", posicao, jogos, 0, 0, 0, valor])
        
        return dados_estatisticos


class EstatisticasManager:
    """Classe que gerencia o processo de scraping, armazenamento e exibição de estatísticas."""
    
    def __init__(self, url, headers, db_name):
        self.scraper = ScraperTransfermarkt(url, headers)
        self.banco = BancoDeDados(db_name)

    def executar(self):
        """Executa o processo completo: coleta, armazena e exibe os dados."""
        # Coletando os dados para cada estatística
        gols_data = self.scraper.coletar_dados_estatisticos('gols')
        assistencias_data = self.scraper.coletar_dados_estatisticos('assistencias')
        amarelos_data = self.scraper.coletar_dados_estatisticos('amarelos')
        vermelhos_data = self.scraper.coletar_dados_estatisticos('vermelhos')

        # Unindo todos os dados em uma lista de estatísticas
        all_data = gols_data + assistencias_data + amarelos_data + vermelhos_data

        # Inserindo os dados no banco de dados
        self.banco.inserir_estatisticas(all_data)

        # Exibindo os resultados
        self._exibir_resultados()

        # Fechando a conexão com o banco
        self.banco.fechar()

    def _exibir_resultados(self):
        """Exibe os dados das estatísticas coletadas do banco de dados."""
        print("\n\n\nEstatísticas da Temporada 2023/24\n")
        
        # Consultando os dados do banco
        df_estatisticas = self.banco.consultar_estatisticas()

        # Exibindo as estatísticas utilizando pandas DataFrame
        print(df_estatisticas.to_string(index=False))


# Configurações
URL = "https://www.transfermarkt.com.br/real-madrid-cf/leistungsdaten/verein/418/plus/1?reldata=%262023"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
DB_NAME = "players_stats.db"

# Executando o programa
manager = EstatisticasManager(URL, HEADERS, DB_NAME)
manager.executar()
