import re
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable

url = "https://www.transfermarkt.com.br/real-madrid-cf/transferrekorde/verein/418/saison_id/2023/pos//detailpos/0/w_s//altersklasse//plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers = headers)

soup = BeautifulSoup(response.content, "html.parser")

print("\nTransferências da Temporada 2023/24\n")


print("\nENTRADAS")
# Criando tabela
table_entradas = PrettyTable()
table_entradas.field_names = ["#", "Jogadores", "Posição", "Idade", "Nacionalidade", "Origem", "Valor de Mercado (na época)", "Valor Pago"]

jogadores_in = soup.select('table[class="items"] tbody tr')
for jogador in jogadores_in:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 9:  # Verifica se existem dados suficientes
        num = dados_jogador[0]
        nome = dados_jogador[2]
        posicao = dados_jogador[3]
        idade = dados_jogador[4]

        nacionalidade_imgs = jogador.select('td img[alt]')
        nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 6 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
        nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) >= 6 else ''

        origem = dados_jogador[6].split('\n')[0]
        valorJogador = dados_jogador[9]
        valorPago = dados_jogador[10]
        
        # Adicionando dados à tabela
        table_entradas.add_row([num, nome, posicao, idade, nacionalidade + nacionalidade2, origem, valorJogador, valorPago])

# Exibindo tabela
print(table_entradas)

print('\n-------------------------------------------------------------------------------------------------------------------------------------------------------------\n')

print("SAÍDAS")
urlOut = "https://www.transfermarkt.com.br/real-madrid-cf/rekordabgaenge/verein/418/saison_id/2023/pos//detailpos/0/w_s//plus/1"
responseOut = requests.get(urlOut, headers = headers)
soupOut = BeautifulSoup(responseOut.content, "html.parser")

table_saidas = PrettyTable()
table_saidas.field_names = ["#", "Jogadores", "Posição", "Idade", "Nacionalidade", "Destino", "Valor de Mercado (na época)", "Valor Pago"]

jogadores_out = soupOut.select('table[class="items"] tbody tr')
for jogador in jogadores_out:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) > 10:  # Verifica se existem dados suficientes
        num = dados_jogador[0]
        nome = dados_jogador[2]
        posicao = dados_jogador[3]
        idade = dados_jogador[4]

        nacionalidade_imgs = jogador.select('td img[alt]')
        nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 6 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
        nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) >= 6 else ''

        origem = dados_jogador[6].split('\n')[0]
        valorJogador = dados_jogador[9]
        valorPago = dados_jogador[10]
        
        # Adicionando dados à tabela
        table_saidas.add_row([num, nome, posicao, idade, nacionalidade + nacionalidade2, origem, valorJogador, valorPago])

# Exibindo tabela
print(table_saidas)