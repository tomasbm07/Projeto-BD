import psycopg2

connection = psycopg2.connect(dbname="projetobd", user="alexandre", password="12345", host="127.0.0.1", port="5432")
cursor = connection.cursor()

def main():
    login()


def login():
    print("login or signup? (l/s)")
    option=input()
    if option=='s':
        print("Insira o seu username, email e password (separados por espaco):")
        info_user=input().split(" ")
        cursor.execute('''INSERT INTO utilizadores (username, email, password) VALUES (%s, %s, %s);''', (info_user[0], info_user[1], info_user[2]))
        connection.commit()
    elif option=='l':
        print("Insira o seu username e password (separados por espaco):")
        info_user = input().split(" ")
        cursor.execute('''SELECT COUNT(username) FROM utilizadores WHERE username=%s AND password=%s;''', (info_user[0], info_user[1]))
        validation=cursor.fetchone()
        if validation[0]==1:
            print("Autenticado!")
        else:
            print("Combinacao de username e password inexistente")

if __name__ == '__main__':
    main()
    cursor.close()
    connection.close()