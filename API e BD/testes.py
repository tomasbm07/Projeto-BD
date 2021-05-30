import requests
import names
import random
import time as t

"""
pip3 install names requests
"""

#password para todos os users
PASSWORD = '123'


nomes = []
tokens = []
leilao_ids = []

#------------SignUp------------
URL = "http://localhost:8080/dbproj/user"

for i in range(15):
    nome = names.get_first_name()
    nomes.append(nome)

    PARAMS = {
        'username': f'{nome}',
        'email': f'{nome}{random.randint(1,100)}@gmail.com',
        'password': PASSWORD
    }

    r = requests.post(url = URL, json = PARAMS)
    data = r.json()
    if 'erro' in data.keys():
        print(f"erro - {data['erro']}")
    else:
        print(f"Created user {data['userid']} - username: {nome}")
    t.sleep(0.1)


#------------Login------------
URL = "http://localhost:8080/dbproj/user"

for i in nomes:
    PARAMS = {
        'username': i,
        'password': '123'
    }

    r = requests.put(url = URL, json = PARAMS)
    data = r.json()
    tokens.append(data['authToken'])
    if 'erro' in data.keys():
        print(f"erro - {data['erro']}")
    else:
        print(f"username:{i} - token:{data['authToken']}")
    t.sleep(0.1)


#------------Criar Leilao------------
URL = "http://localhost:8080/dbproj/leilao"

titles = [
    "O melhor leilao de sempre", 
    "Preco INCRIVEL",
    "NAO PERCA ESTE INCRIVEL LEILAO",
    "Vendo artigo",
    "Vendo artigo - NAO NEGOCIAVEL",
    "Artigo para troca",
    "Um leilao FANTASTICO",
    "Barato e Bom!!!!!"
]

for i in range(random.randint(5, 8)):
    PARAMS = {
        "artigoId": random.randint(1, 10),
        "precomin": random.randint(20, 100),
        "titulo": random.choice(titles),
        "descricao": "Apenas uma descricao generica",
        "endDate" : "2021-05-30 20:30:00",
        "userAuthToken": random.choice(tokens) # random user para autor do leilao
    }   

    r = requests.post(url = URL, json = PARAMS)
    data = r.json()
    leilao_ids.append(data['leilaoId'])
    print(f"Auction {data['leilaoId']} created")
    t.sleep(0.1)


#------------Random Bids------------
for i in range(random.randint(10, 20)):
    id = random.choice(leilao_ids)
    user = random.choice(tokens)
    bid = random.randint(50, 1000)

    URL = f"http://localhost:8080/dbproj/licitar/{id}/{bid}"
    PARAMS = {
        "userAuthToken": user
    }
    r = requests.get(url = URL, json = PARAMS)
    data = r.json()
    if 'erro' in data.keys():
        print(f"erro - {data['erro']}")
    else:
        print(f'{user} made a bid on {id} of {bid}£')


#------------Random Messages------------
for i in range(random.randint(5, 15)):
    user = random.choice(tokens)
    id = random.choice(leilao_ids)
    URL = f"http://localhost:8080/dbproj/leilao/{id}"
    PARAMS = {
        "mensagem" : "Apenas uma mensagem generica",
        "authToken" : user
}
    r = requests.post(url = URL, json = PARAMS)
    data = r.json()
    if 'erro' in data.keys():
        print(data)
        print(f"erro - {data['erro']}")
    else:
        print(f"{user} adicionou uma mensagem no leilao {id}")
