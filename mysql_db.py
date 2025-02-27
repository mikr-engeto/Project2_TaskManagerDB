import mysql.connector
from mysql.connector import errorcode
from app_config import Cfg

class DbLayer:

    def _prepare_sql(self, table_name):
        """
        Funkce připraví SQL dotazy pro použití v aplikaci
        """
        # SQL  pro založení tabulky 'ukoly'
        self.sql_crate_table = "CREATE TABLE " + table_name + """ (
            id int NOT NULL AUTO_INCREMENT,
            nazev varchar(255) NOT NULL,
            popis varchar(500) NOT NULL,
            stav ENUM ('nezahájeno', 'probíhá', 'hotovo') NOT NULL DEFAULT 'nezahájeno',
            datum_vytvoreni datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id) );"""
        # DROP TABLE ukoly:
        # INSERT INTO ukoly (nazev, popis) VALUES ('nazev', 'popis'); 

        # SQL pro vložení úkolu
        self.sql_insert_ukol = "INSERT INTO " + table_name + " (nazev, popis) VALUES ('{0}', '{1}');"

        # SQL pro aktualizaci stavu úkolu
        self.sql_update_ukol = "UPDATE " + table_name + " SET stav = '{1}' WHERE id = {0};"

        # SQL pro odstranění úkolu
        self.sql_delete_ukol = "DELETE FROM " + table_name + " WHERE id = {0};"

        # SQL vrátí poslední vložený úkol (po insertu)
        self.sql_get_last_inserted_ukol = """SELECT 
            u.id,
            u.nazev,
            u.popis,
            u.stav,
            u.datum_vytvoreni
        FROM """ + table_name + " u INNER JOIN (SELECT max(id) AS last_id FROM " + table_name + ") uid ON u.id = uid.last_id;"

        # SQL vrátí seznam všech úkolů
        self.sql_select_all = """SELECT 
            id,
            nazev,
            popis,
            stav,
            datum_vytvoreni
        FROM """ + table_name + " {};"

        # WHERE podmínka pro filtrování úkolů
        self.sql_select_filter = "WHERE stav IN ('nezahájeno', 'probíhá')"

        # SQL pro získání záznamu s daným ID
        self.sql_record_by_id = "SELECT * FROM " + table_name + " WHERE id = {}"

        # SQL pro získání počtu záznamů v tabulce (kontrola existence tabulky)
        self.sql_select_count = "SELECT count(*) from " + table_name


    # constructor
    def __init__(self,
        host=None,          # Adresa serveru
        user=None,          # Uživatelské jméno
        password=None,      # Heslo k databázi
        database=None,      # Název databáze
        table_name=None     # Název tabulky s úkoly
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

        self._table_name = table_name if table_name is not None else Cfg.table_name
        print(f"host: '{Cfg.host}', user: '{Cfg.user}', password: ******, database: '{Cfg.database}', table_name: '{self._table_name}'")

        # připravím si SQL dotazy
        self._prepare_sql(self._table_name)

        # připravím proměnné pro connection a cursor
        self.conn = None
        self.cursor = None


    # destructor
    def __del__(self):
        self.close_db()


    def close_db(self):
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.conn is not None:
            self.conn.close()
            self.conn = None


    # Připojení k databázi
    def pripojeni_db(self, check_table_exists=True):
        """
        Funkce vytvoří připojení k databázi
        """
        if self.conn is None:
            try:
                self.conn = mysql.connector.connect(**self.connection_params)   
                # nastavím autocommit
                self.conn.autocommit = True
                self.cursor = self.conn.cursor(buffered=True)             
                print("Připojení do databáze bylo úspěšné")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print(f"Přístup k databázi pro uživatele {self.connection_params['user']} byl zamítnut!")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print(f"Databáze {self.connection_params['database']} neexistuje!")
                else:
                    print(f"Při připojení do databáze nastala chyba: {err}")
                raise # pošlu výjímku nahoru

            if check_table_exists:
                self.vytvoreni_tabulky()

        else:
            print("Připojení k databázi již existuje!")
            
    
    def vytvoreni_tabulky(self):
        """
        Funkce zkontroluje, zda existuje tabulka 'ukoly'.
        Pokud tabulka neexistuje, vytvoří ji.
        """
        table_ukoly_exists = True

        if self.conn is not None:
            try:
                self.cursor.execute(self.sql_select_count)
                # self.conn.commit() #autocommit
            except Exception as err:
                if err.errno == errorcode.ER_NO_SUCH_TABLE:
                    table_ukoly_exists = False
                else:
                    print(f"Při kontrole existence tabulky 'ukoly' nastala neznámá chyba!")
                    raise # pošlu výjimku nahoru            

            if table_ukoly_exists == False:
                print(f"Tabulka 'ukoly' neexistuje, vytvořím ji")
                try:
                    self.cursor.execute(self.sql_crate_table)
                    # self.conn.commit() #autocommit
                except:
                    print(f"Při vytváření tabulky 'ukoly' nastala neznámá chyba!")
                    raise # pošlu výjimku nahoru
                print("Tabulka úkoly byla úspěšně vytvořena")
            else:
                print(f"Tabulka 'ukoly' již existuje")

        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")

    def pridat_ukol(self, nazev, popis):
        """
        Funkce vloží do tabulky 'ukoly' nový úkol
        """
        if self.conn is not None:
            pocet_pridanych = 0
            try:
                self.cursor.execute(self.sql_insert_ukol.format(nazev, popis))
                pocet_pridanych = self.cursor.rowcount
                # self.conn.commit() #autocommit
            except:
                print(f"Při ukládání úkolu se vyskytla neočekávaná chyba!")
                raise
            
            return pocet_pridanych
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")


    def vrat_posledni_vlozeny_ukol(self):
        """
        Funkce vrátí poslední vložený úkol
        """
        if self.conn is not None:
            ukol = None
            try:            
                self.cursor.execute(self.sql_get_last_inserted_ukol)
                ukol = self.cursor.fetchone()
                # self.conn.commit() #autocommit
            except:
                print(f"Nastala neočekáváná chyba při získávání posledního přidaného úkolu")
                raise

            return ukol
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")


    def zobrazit_ukoly(self, filter=True):
        """
        Funkce funguje jako generátor a vrací seznam úkolů.
        Pokud je parametr filter=True, funkce vrací pouze úkoly se stavy 'Nezahájeno' a 'Probíhá' (default)
        """
        if self.conn is not None:
            # přidám WHERE podmínku pro filtrování úkolů, pokud filter=True
            where_clause = self.sql_select_filter if filter == True else '';
            try:
                self.cursor.execute(self.sql_select_all.format(where_clause))
            except:
                print(f"Při získávání seznamu úkolu se vyskytla neočekávaná chyba!")
                raise

            # načtu první záznam
            ukol = self.cursor.fetchone()            
            # self.conn.commit() #autocommit

            # pokud první záznam existuje, pokračuj ve smyčce a vracej další
            if ukol is not None:
                while ukol:
                    yield ukol
                    # načti další záznam
                    ukol = self.cursor.fetchone()
                # self.conn.commit() #autocommit
            else:
                # nevrátily se žádné záznamy, vrať prázdný seznam
                # self.conn.commit() #autocommit
                return []
                        
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")


    def vrat_ukol_s_id(self, id):        
        if self.conn is not None:
            try:
                self.cursor.execute(self.sql_record_by_id.format(id))
            except:
                print(f"Při získávání získávání záznamu úkolu se vyskytla neočekávaná chyba!")
                raise

            ukol = None
            # pokud byl úkol v tabulce nalezen ...
            if (self.cursor.rowcount == 1):
                # načtu první záznam
                ukol = self.cursor.fetchone()
            # self.conn.commit() #autocommit
            
            return ukol
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")        


    def aktualizovat_ukol(self, id, new_state):
        if self.conn is not None:
            update_count = 0
            try:
                self.cursor.execute(self.sql_update_ukol.format(id, new_state))
                update_count = self.cursor.rowcount
                # self.conn.commit() #autocommit
            except:
                print(f"Při aktualizaci záznamu úkolu se vyskytla neočekávaná chyba!")
                raise

            if update_count == 0:
                raise ValueError("Úkol s daným ID neexistuje!")
            
            return update_count
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")        


    def odstranit_ukol(self, id):        
        if self.conn is not None:
            delete_count = 0
            try:
                self.cursor.execute(self.sql_delete_ukol.format(id))
                delete_count = self.cursor.rowcount
                # self.conn.commit() #autocommit
            except:
                print(f"Při mazání záznamu úkolu se vyskytla neočekávaná chyba!")
                raise

            if delete_count == 0:
                raise ValueError("Úkol s daným ID neexistuje!")

            return delete_count
        else:
            raise Exception("Nebylo vytvořeno připojení do databáze!")        


if __name__ == '__main__':    
    db = DbLayer()
    db.pripojeni_db(check_table_exists=True)
    db.pridat_ukol("Jít s Matějem na brusle", "Je potřeba se trochu zabavit a jít na čerstvý vzduch!")
    db.close_db()
    db = None
