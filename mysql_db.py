import mysql.connector
from mysql.connector import errorcode
from app_config import Cfg

class DbLayer:
    sql_crate_table = """CREATE TABLE ukoly (
        id int NOT NULL AUTO_INCREMENT,
        nazev varchar(255) NOT NULL,
        popis varchar(500) NOT NULL,
        stav ENUM ('nezahájeno', 'probíhá', 'hotovo') NOT NULL DEFAULT 'nezahájeno',
        datum_vytvoreni datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (id) );"""
    # DROP TABLE ukoly:
    # INSERT INTO ukoly (nazev, popis) VALUES ('nazev', 'popis'); 

    sql_insert_ukol = "INSERT INTO ukoly (nazev, popis) VALUES ('{0}', '{1}');"

    sql_update_ukol = "UPDATE ukoly SET stav = '{1}' WHERE id = {0};"

    sql_delete_ukol = "DELETE FROM ukoly WHERE id = {0};"

    sql_get_inserted_ukol = """SELECT 
        u.id,
        u.nazev,
        u.popis,
        u.stav,
        u.datum_vytvoreni
    FROM ukoly u INNER JOIN (SELECT max(id) AS last_id FROM ukoly) uid ON u.id = uid.last_id;"""

    # constructor
    def __init__(self,
        host=None,          # Adresa serveru
        user=None,          # Uživatelské jméno
        password=None,      # Heslo k databázi
        database=None       # Název databáze
    ):
        if host is not None and user is not None and password is not None and database is not None:
            self.connection_params = {
                "host" : host,
                "user" : user,
                "password" : password,
                "database" : database
            }
            print(f"Byly předány uživatelské údaje pro přístup k databázi:")
        else:
            print(f"Nebyly předány údaje pro připojení k databázi, použiji default nastavení z konfigurace:")
            self.connection_params = {
                "host" : Cfg.host,
                "user" : Cfg.user,
                "password" : Cfg.password,
                "database" : Cfg.database
            }
        print(f"host: '{Cfg.host}', user: '{Cfg.user}', password: ******, database: '{Cfg.database}'")

        self.conn = None
        self.cursor = None


    # destructor
    def __del__(self):
        if self.conn is not None:
            self.conn.close()


    # Připojení k databázi
    def connect_to_db(self):
        """
        Funkce vytvoří připojení k databázi
        """
        if self.conn is None:
            try:
                self.conn = mysql.connector.connect(**self.connection_params)
                self.cursor = self.conn.cursor()
                print("Připojení do databáze bylo úspěšné")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print(f"Přístup k databázi pro uživatele {self.connection_params['user']} byl zamítnut!")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print(f"Databáze {self.connection_params['database']} neexistuje!")
                else:
                    print(f"Při připojení do databáze nastala chyba: {err}")
                raise # pošlu výjímku nahoru
        else:
            print("Připojení k databázi již existuje!")
            
    
    def check_create_table(self):
        """
        Funkce zkontroluje, zda existuje tabulka 'ukoly'.
        Pokud tabulka neexistuje, vytvoří ji.
        """
        table_ukoly_exists = True

        if self.conn is not None:
            try:
                self.cursor.execute("select count(*) from ukoly")
            except Exception as err:
                if err.errno == errorcode.ER_NO_SUCH_TABLE:
                    table_ukoly_exists = False
                else:
                    print(f"Při kontrole existence tabulky 'ukoly' nastala neznámá chyba! ERROR: {err}")
                    raise # pošlu výjimku nahoru
        else:
            raise("Nebylo vytvořeno připojení do databáze!")
    
        if table_ukoly_exists == False:
            print(f"Tabulka 'ukoly' neexistuje, vytvořím ji")
            try:
                self.cursor.execute(DbLayer.sql_crate_table)
            except:
                print(f"Při vytváření tabulky 'ukoly' nastala neznámá chyba!")
                raise # pošlu výjimku nahoru
            print("Tabulka úkoly byla úspěšně vytvořena")
        else:
            print(f"Tabulka 'ukoly' již existuje")


    def insert_task(self, nazev, popis):
        """
        Funkce vloží do tabulky 'ukoly' nový úkol
        """
        if self.conn is not None:
            try:
                print(f"DEBUG: {DbLayer.sql_insert_ukol.format(nazev, popis)}")
                self.cursor.execute(DbLayer.sql_insert_ukol.format(nazev, popis))
            except:
                print(f"Při ukládání úkolu se vyskytla neočekávaná chyba!")
                raise
            
            # záznam byl úspěšně vytvořen
            self.cursor.execute(DbLayer.sql_get_inserted_ukol)
            ukol = self.cursor.fetchone()
            print(f"Byl přidán nový úkol:\n"
                  f"  ID:              {ukol['id']}\n"
                  f"  Název:           {ukol['nazev']}\n"
                  f"  Popis:           {ukol['popis']}\n"
                  f"  Stav:            {ukol['stav']}\n"
                  f"  Datum vytvoření: {ukol['id']}\n")
        else:
            raise("Nebylo vytvořeno připojení do databáze!")


if __name__ == '__main__':    
    db = DbLayer()
    db.connect_to_db()
    db.check_create_table()
    db.insert_task("Jít s Matějem na brusle", "Je potřeba se trochu zabavit a jít na čerstvý vzduch!")
