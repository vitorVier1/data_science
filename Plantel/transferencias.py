import requests
from bs4 import BeautifulSoup
import pandas as pd
from prettytable import PrettyTable

# URL para as transferências de entrada
url = "https://www.transfermarkt.com.br/real-madrid-cf/transferrekorde/verein/418/saison_id/2023/pos//detailpos/0/w_s//altersklasse//plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

# Coletando transferências de entrada
print("\nTransferências da Temporada 2023/24\n")
print("\nENTRADAS")

jogadores_entrada = []

# Seleção da tabela de transferências de entrada
jogadores_in = soup.select('table[class="items"] tbody tr')
for jogador in jogadores_in:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 9:  # Verifica se existem dados suficientes
        nome = dados_jogador[2]
        posicao = dados_jogador[3]
        idade = dados_jogador[4]
        
        # Coletando a nacionalidade
        nacionalidade_imgs = jogador.select('td img[alt]')
        nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 6 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
        nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) >= 6 else ''
        
        origem = dados_jogador[6].split('\n')[0]
        valorJogador = dados_jogador[9]
        valorPago = dados_jogador[10]
        
        # Adicionando dados à lista de entradas
        jogadores_entrada.append([nome, posicao, idade, f"{nacionalidade} {nacionalidade2}", origem, valorJogador, valorPago])

# Criando o DataFrame para entradas
df_entradas = pd.DataFrame(jogadores_entrada, columns=["Jogador", "Posição", "Idade", "Nacionalidade", "Origem", "Valor da Época", "Valor Pago"])

# Exibindo a tabela de entradas
print(df_entradas.to_string(index=False))

print('\n-------------------------------------------------------------------------------------------------------------------------------------------------------------\n')

# Coletando transferências de saída
print("SAÍDAS")

urlOut = "https://www.transfermarkt.com.br/real-madrid-cf/rekordabgaenge/verein/418/saison_id/2023/pos//detailpos/0/w_s//plus/1"
responseOut = requests.get(urlOut, headers=headers)
soupOut = BeautifulSoup(responseOut.content, "html.parser")

jogadores_saida = []

# Seleção da tabela de transferências de saída
jogadores_out = soupOut.select('table[class="items"] tbody tr')
for jogador in jogadores_out:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) > 10:  # Verifica se existem dados suficientes
        nome = dados_jogador[2]
        posicao = dados_jogador[3]
        idade = dados_jogador[4]
        
        # Coletando a nacionalidade
        nacionalidade_imgs = jogador.select('td img[alt]')
        nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 6 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
        nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) >= 6 else ''
        
        destino = dados_jogador[6].split('\n')[0]
        valorJogador = dados_jogador[9]
        valorPago = dados_jogador[10]
        
        # Adicionando dados à lista de saídas
        jogadores_saida.append([nome, posicao, idade, f"{nacionalidade} {nacionalidade2}", destino, valorJogador, valorPago])

# Criando o DataFrame para saídas
df_saidas = pd.DataFrame(jogadores_saida, columns=["Jogador", "Posição", "Idade", "Nacionalidade", "Destino", "Valor da Época", "Valor Pago"])

# Exibindo a tabela de saídas
print(df_saidas.to_string(index=False))
