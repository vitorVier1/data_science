import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.transfermarkt.com.br/real-madrid-cf/kader/verein/418/saison_id/2023/plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers = headers)

soup = BeautifulSoup(response.content, "html.parser")


# Coletando Nome da Equipe
team_name = soup.select_one('h1[class="data-header__headline-wrapper data-header__headline-wrapper--oswald"]').text.split('\n')[-1].strip()
print("\n" + team_name + " | Temporada 2023/24\n")

#Coletando dados do Plantel da Equipe
plantel_madrid = soup.select_one('h2[class="content-box-headline"]').text.split('\n')[1].strip()
print(plantel_madrid + " 2023/24")


jogadores_data = []
# Coletando dados do plantel
plantel = soup.select('table[class="items"] tbody tr')
for jogador in plantel:
    dados_jogador = [td.text.strip() for td in jogador.find_all('td') if td.text.strip()]
    
    if len(dados_jogador) >= 8:  # Verifica se existem dados suficientes
        num = dados_jogador[0]
        nome = dados_jogador[1]
        sobreNome = dados_jogador[2].split()[-1].strip()
        posicao = dados_jogador[3]
        altura = dados_jogador[5]
        pe = dados_jogador[6] if len(dados_jogador) > 7 else "-"  # Podem não haver dados cadastrados
        idade = dados_jogador[4].split()[1]

        nacionalidade_imgs = jogador.select('td img[alt]')
        nacionalidade = ''.join([img['alt'] for img in nacionalidade_imgs][1]) if len(nacionalidade_imgs) < 5 else ''.join([img['alt'] for img in nacionalidade_imgs][1]) + "/"
        nacionalidade2 = ''.join([img['alt'] for img in nacionalidade_imgs][2]) if len(nacionalidade_imgs) > 4 else ''
        
        # Ajuste Especificos
        if([img['alt'] for img in nacionalidade_imgs][1] == "Joselu"):
            nacionalidade = ""
            nome = "Joselu"
            sobreNome = ""
        if dados_jogador[0] == "11":
            nome = "Rodrygo"
            sobreNome = ""

        valor = dados_jogador[8] if len(dados_jogador) > 8 else "-"  # Podem não haver dados cadastrados
        
        # Adicionando dados à tabela
        jogadores_data.append([num,  f"{nome.split()[0]} {sobreNome}",  posicao,  altura,  pe,  idade,  f"{nacionalidade}{nacionalidade2}",  valor])

dados_jogador = pd.DataFrame(jogadores_data, columns=["Numero", "Nome", "Posicao", "Altura", "Pe", "Idade", "Nacionalidade", "Valor"])

# Exibindo a tabela
print("\n\n\nPlantel Real Madrid - Temporada 2023/24\n")
print(dados_jogador.to_string(index=False))