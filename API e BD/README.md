# Projeto Base de Dados 
### FCTUC - LEI 2020/2021
* Tomás Mendes
* Alexandre Andrade

## Nota
Para uma melhor visualização deste formato de ficheiro, recomendamos instalar o módulo ```grip``` do python com o comando:  
Linux / MacOS
```
$ pip3 install grip
```

Windows
```
$ pip install grip
```

e correr o seguinte comando, na localização do ficheiro:
```
$ grip
```

# Intruções de utilização

* O projeto corre todo em containners do Docker. Como tal será necessário instalar o [Docker](https://docs.docker.com/get-docker/)

* O Projeto não dispõem de nenhum tipo de interface, seja gráfica ou CLI (command line interface) e por isso é necessário enviar http requests pelo [Curl](https://curl.se/download.html) ou preferencialmente pelo [Postman](https://www.postman.com/) por ter uma interface gráfica que permite, de uma forma mais intuitiva, enviar e ver as respostas dos requests. É também disponibilizado um ficheiro ```.json``` com todos os endpoints, que a nossa API suporta, para dar import no Postman.

* Para iniciar o programa correr os seguintes comandos:  

Linux / MacOS
```
$ ./run.sh
```

Windows
```
$ docker-compose up
```

# Informações relevantes

* O DBMS (database management system) escolhido foi o mesmo que foi usado na cadeira ao longo do semestre - [PostgreSQL](https://www.postgresql.org/)

* Caso seja necessário, a base de dados poderá ser acedida com o seguinte comando:

```
$ psql -U admin -d projetobd -h localhost
$ Password for user admin: admin
```
ou pelos dados de acesso:

```
POSTGRES_USER = admin
POSTGRES_PASSWORD = admin
POSTGRES_DB = projetobd
```

## Distribuição do trabalho
* Tomás (cerca de 15 horas)
    * Login, Sign up, e Autenticação
    * Obter todos os comentários num leilão
    * Escrever comentarios / repostas num leilão
    * Atualizar os dados, do perfil, que não são obrigatórios no registo
    * Ver perfil
    * Triggers e funções de   

* Alexandre (cerca de 15 horas)
    * 
    * 
    * 
    * 