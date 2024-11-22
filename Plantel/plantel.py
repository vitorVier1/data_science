import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.transfermarkt.com.br/real-madrid-cf/kader/verein/418/saison_id/2023/plus/1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.content, "html.parser")

# Coletando Nome da Equipe
team_name = soup.select_one('h1[class="data-header__headline-wrapper data-header__headline-wrapper--oswald"]').text.split('\n')[-1].strip()
print("\n" + team_name + " | Temporada 2023/24\n")

# Coletando dados do Plantel da Equipe
plantel_madrid = soup.select_one('h2[class="content-box-headline"]').text.split('\n')[1].strip()
print(plantel_madrid + " 2023/24")

# Lista para armazenar os dados dos jogadores
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
        pe = dados_jogador[6] if len(dados_jogador) > 7 else "-"  # Pode não haver dados cadastrados
        idade = dados_jogador[4].split()[1]

        # Coletando as nacionalidades a partir das imagens
        nacionalidade_imgs = jogador.select('td img[alt]')
        if len(nacionalidade_imgs) > 1:
            nacionalidade = nacionalidade_imgs[0]['alt']
            if len(nacionalidade_imgs) > 2:
                nacionalidade2 = nacionalidade_imgs[1]['alt']
                nacionalidade = f"{nacionalidade}/{nacionalidade2}"
            else:
                nacionalidade = nacionalidade_imgs[0]['alt']
        else:
            nacionalidade = ""

        # Ajuste Específicos para Joselu e Rodrygo
        if "Joselu" in nome:
            nacionalidade = ""
            nome = "Joselu"
            sobreNome = ""
        if num == "11":
            nome = "Rodrygo"
            sobreNome = ""
        
        valor = dados_jogador[8] if len(dados_jogador) > 8 else "-"  # Pode não haver dados cadastrados
        
        # Adicionando os dados à lista de jogadores
        jogadores_data.append([num, f"{nome.split()[0]} {sobreNome}", posicao, altura, pe, idade, nacionalidade, valor])

# Criando o DataFrame com os dados dos jogadores
dados_jogador = pd.DataFrame(jogadores_data, columns=["Numero", "Nome", "Posicao", "Altura", "Pe", "Idade", "Nacionalidade", "Valor"])

# Exibindo o DataFrame
print("\n\n\nPlantel Real Madrid - Temporada 2023/24\n")
print(dados_jogador.to_string(index=False))
