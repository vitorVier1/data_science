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
        """Cria as tabelas para armazenar as transferências de entrada e saída."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transferencias_entrada (
            jogador TEXT,
            posicao TEXT,
            idade INTEGER,
            nacionalidade TEXT,
            origem TEXT,
            valor_da_epoca TEXT,
            valor_pago TEXT
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transferencias_saida (
            jogador TEXT,
            posicao TEXT,
            idade INTEGER,
            nacionalidade TEXT,
            destino TEXT,
            valor_da_epoca TEXT,
            valor_pago TEXT
        )
        """)
        self.conn.commit()

    def inserir_transferencias(self, tabela, dados):
        """Insere os dados de transferências no banco de dados."""
        if tabela == 'entrada':
            self.cursor.executemany("""
                INSERT INTO transferencias_entrada (jogador, posicao, idade, nacionalidade, origem, valor_da_epoca, valor_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dados)
        elif tabela == 'saida':
            self.cursor.executemany("""
                INSERT INTO transferencias_saida (jogador, posicao, idade, nacionalidade, destino, valor_da_epoca, valor_pago)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, dados)
        self.conn.commit()

    def consultar_transferencias(self, tabela):
        """Consulta os dados de transferências do banco de dados."""
        if tabela == 'entrada':
            query = "SELECT * FROM transferencias_entrada"
        elif tabela == 'saida':
            query = "SELECT * FROM transferencias_saida"
        return pd.read_sql_query(query, self.conn)

    def fechar(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()


class ScraperTransferencias:
    """Classe responsável por realizar o scraping das transferências."""
    
    def __init__(self, url, headers):
        self.url = url
        self.headers = headers

    def coletar_transferencias(self, tipo):
        """Coleta as transferências de entrada ou saída."""
        transferencias = []
        response = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        
        if tipo == 'entrada':
            jogadores = soup.select('table[class="items"] tbody tr')
        else:
            jogadores = soup.select('table[class="items"] tbody tr')

        for jogador in jogadores:
            dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
            
            if len(dados_jogador) > 10:  # Verifica se existem dados suficientes
                nome = dados_jogador[2]
                posicao = dados_jogador[3]
                idade = dados_jogador[4]
                
                # Coletando a nacionalidade
                nacionalidade_imgs = jogador.select('td img[alt]')
                nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 6 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
                nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) >= 6 else ''
                
                if tipo == 'entrada':
                    origem = dados_jogador[6].split('\n')[0]
                    valorJogador = dados_jogador[9]
                    valorPago = dados_jogador[10]
                    transferencias.append([nome, posicao, idade, f"{nacionalidade}{nacionalidade2}", origem, valorJogador, valorPago])
                elif tipo == 'saida':
                    destino = dados_jogador[6].split('\n')[0]
                    valorJogador = dados_jogador[9]
                    valorPago = dados_jogador[10]
                    transferencias.append([nome, posicao, idade, f"{nacionalidade}{nacionalidade2}", destino, valorJogador, valorPago])
        
        return transferencias


class TransferenciasManager:
    """Classe que gerencia o processo de scraping, armazenamento e exibição das transferências."""
    
    def __init__(self, url_entrada, url_saida, headers, db_name):
        self.scraper_entrada = ScraperTransferencias(url_entrada, headers)
        self.scraper_saida = ScraperTransferencias(url_saida, headers)
        self.banco = BancoDeDados(db_name)

    def executar(self):
        """Executa o processo completo: coleta, armazena e exibe as transferências."""
        # Coletando as transferências de entrada
        transferencias_entrada = self.scraper_entrada.coletar_transferencias('entrada')
        # Coletando as transferências de saída
        transferencias_saida = self.scraper_saida.coletar_transferencias('saida')

        # Inserindo as transferências no banco de dados
        self.banco.inserir_transferencias('entrada', transferencias_entrada)
        self.banco.inserir_transferencias('saida', transferencias_saida)

        # Exibindo os resultados
        self._exibir_resultados()

        # Fechando a conexão com o banco
        self.banco.fechar()

    def _exibir_resultados(self):
        """Exibe os dados das transferências coletadas do banco de dados."""
        print("\nTransferências da Temporada 2023/24\n")

        # Consultando as transferências de entrada e saída
        df_entrada = self.banco.consultar_transferencias('entrada')
        df_saida = self.banco.consultar_transferencias('saida')

        # Exibindo as transferências de entrada
        print("\nEntradas:")
        print(df_entrada.to_string(index=False))

        # Exibindo as transferências de saída
        print("\nSaídas:")
        print(df_saida.to_string(index=False))


# Configurações
URL_ENTRADA = "https://www.transfermarkt.com.br/real-madrid-cf/transferrekorde/verein/418/saison_id/2023/pos//detailpos/0/w_s//altersklasse//plus/1"
URL_SAIDA = "https://www.transfermarkt.com.br/real-madrid-cf/rekordabgaenge/verein/418/saison_id/2023/pos//detailpos/0/w_s//plus/1"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}
DB_NAME = "transferencias_real_madrid.db"

# Executando o programa
manager = TransferenciasManager(URL_ENTRADA, URL_SAIDA, HEADERS, DB_NAME)
manager.executar()
