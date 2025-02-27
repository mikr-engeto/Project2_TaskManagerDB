import sys
from mysql_db import DbLayer
from app_config import Cfg


class TaskManager:

    def __init__(self):
        self.ukoly = []
        self.polozky_menu = {
            "1" : ["Přidat nový úkol", self.akce_pridat_ukol],
            "2" : ["Zobrazit všechny úkoly", self.akce_zobrazit_ukoly],
            "3" : ["Aktualizovat úkol", self.akce_aktualizovat_ukol],
            "4" : ["Odstranit úkol", self.akce_odstranit_ukol],
            "5" : ["Konec programu", self.akce_konec_programu],
        }
        self.volba_konec = "5"

        self.db = DbLayer(host=Cfg.host, user=Cfg.user, password=Cfg.password, database=Cfg.database)
        
        # vytvoření připojení k DB
        try:
            self.db.pripojeni_db(check_table_exists=True)
        except:
            print("Nepodařilo se připojit k databázi! Ukončuji aplikaci ...")
            sys.exit(1)


    # destructor
    def __del__(self):
        if self.db is not None:
            self.db.close_db()
            self.db = None


    def hlavni_menu(self):
        """
        Funkce zobrazí hlavní menu a vyčká na pokyny uživatele.
        Funkce řídí běh celé aplikace.
        """
        volba = None
        upozorneni = None
        while volba != self.volba_konec:
            volba = self._zobraz_menu(upozorneni)
            # nastavím upozornění opět na None, aby se nezobrazovalo příště
            upozorneni = None

            # validace vstupní hodnoty
            if volba in self.polozky_menu.keys():
                # zavolat funkci přiřazenou položce
                self.polozky_menu[volba][1]()                    
            else:
                upozorneni = f"Byla zadána neplatná volba '{volba}'. Zadejte platnou volbu z menu."


    def akce_pridat_ukol(self):
        """
        Funkce umožní uživateli přidat nový úkol
        """
        print("") # vytisknu prázdný řádek, ať se v tom lépe orientuje

        ukol = {
            "nazev" : None,
            "popis" : None
        }
        vstup_je_ok = False
        
        while not vstup_je_ok:
            ukol["nazev"] = input("Zadejte název úkolu: ")
            ukol["popis"] = input("Zadejte popis úkolu: ")

            # předpokládám, že vstup je validní
            vstup_je_ok = True

            # pro jistotu ale provedu kontrolu zadaných hodnot
            for hodnota in ukol.values():
                if (hodnota is None or len(hodnota) == 0):
                    vstup_je_ok = False

            if not vstup_je_ok:
                print("\nNázev a popis úkolu nesmí být prázdné! Zadejte platný název a popis úkolu.\n")
                # ... a uživatel musí zadat hodnoty znoavu

        # byly zadány validní vstupní údaje, přidám úkol do seznamu
        try:
            self.db.pridat_ukol(ukol["nazev"], ukol["popis"])
        except Exception as err:
            print("Úkol se nepodařilo přidat!")
            print(err)

        pridany_ukol = None
        try:
            pridany_ukol = self.db.vrat_posledni_vlozeny_ukol()
        except:
            # něco se stalo, ale úkol byl přidán a tak jen nevypíšu nový úkol na obrazovku
            pass

        if pridany_ukol:
            print("\nByl přidán nový úkol:")
            self._vytiskni_ukol(pridany_ukol, True)
            print()


    def _zobraz_ukoly(self, filter_tasks=True, single_row_style=False):
        """
        Funkce vypíše seznam úkolů a vrátí jejich počet
        """
        pocet_ukolu = 0

        print("\n---- Seznam úkolů ----")
        try:
            for ukol in self.db.zobrazit_ukoly(filter=filter_tasks):
                pocet_ukolu += 1
                # vypiš úkol na obrazovku
                self._vytiskni_ukol(ukol, single_row_style)
        except Exception as err:
            print(f"Nepodařilo se získat seznam úkolů!")
            print(err)

        if pocet_ukolu == 0:
            print(f"\n Seznam úkolů je prázdný ...")

        return pocet_ukolu
            
    def akce_zobrazit_ukoly(self):
        """
        Funkce zobrazí všechny evidované úkoly
        """        
        pocet_ukolu = self._zobraz_ukoly(filter_tasks=True)

        # vypíšu prázdný řádek
        print()

        return pocet_ukolu
    

    def akce_aktualizovat_ukol(self):
        """
        Funkce provede aktualizaci stavu úkolu
        """
        pocet_ukolu = self._zobraz_ukoly(filter_tasks=True, single_row_style=True)

        if pocet_ukolu == 0:
            return

        print() # vytisknu prázdný řádek pro lepší čitelnost

        vstup_je_ok = False

        while not vstup_je_ok:

            volba = input("Zadejte číslo úkolu, který chcete aktualizovat: ")
            print() # vytisknu prázdný řádek pro lešpí čitelnost

            ukol_index = -1 # nevalidní index
            try:
                ukol_index = int(volba)
            except:
                print(f"Byl zadán neplatný vstup '{volba}'! Vstup musí být číslo.")
                ukol_index = -1

            #validace vstupu
            if (ukol_index >= 0):
                try:
                    ukol = self.db.vrat_ukol_s_id(ukol_index)
                except Exception as err:
                    print(f"Nastala chyba: {err}")
                    print("Vracím se do hlavního menu\n")
                    return

                if ukol is not None:
                    # vypíšu vybraný úkol
                    print("Vybraný úkol:")
                    self._vytiskni_ukol(ukol, False)
                    print()
                    volba = input("Zvolte nový stav úkolu - (P)robíhá, (H)otovo : ")
                                  
                    if volba in ('P', 'p'):
                        volba = "probíhá"
                        vstup_je_ok = True
                    elif volba in ('H', 'h'):
                        volba = "hotovo"
                        vstup_je_ok = True

                    if vstup_je_ok:
                        try:
                            self.db.aktualizovat_ukol(ukol_index, volba)
                        except:
                            print(f"Nastala chyba: {err}")
                            print("Vracím se do hlavního menu\n")
                            return                            

                        print(f"\nStav úkolu ID {ukol_index} byl změněn na '{volba}'\n")
                else:
                    print(f"Úkol s ID '{ukol_index}' neexistuje! Vyberte existující úkol")



    def akce_odstranit_ukol(self):
        """
        Funkce odstraní požadovaný úkol ze seznamu
        """

        # zobrazím všechny úkoly, ať je z čeho vybírat
        pocet_ukolu = self._zobraz_ukoly(filter_tasks=False, single_row_style=True)

        if pocet_ukolu == 0:
            return
        
        print() # prázdný řádek pro lepší čitelnost
        
        vstup_je_ok = False

        while not vstup_je_ok:

            volba = input("Zadejte číslo úkolu, který chcete odstranit: ")
            print() # vytisknu prázdný řádek pro lešpí čitelnost

            ukol_index = -1 # nevalidní index
            try:
                ukol_index = int(volba)
            except:
                print(f"Byl zadán neplatný vstup '{volba}'! Vstup musí být číslo.")
                ukol_index = -1

            #validace vstupu
            if (ukol_index >= 0):
                try:
                    ukol = self.db.vrat_ukol_s_id(ukol_index)
                except Exception as err:
                    print(f"Nastala chyba: {err}")
                    print("Vracím se do hlavního menu\n")
                    return

                if ukol is not None:
                    # vypíšu vybraný úkol
                    print("Vybraný úkol bude odstraněn:")
                    self._vytiskni_ukol(ukol, False)
                    print()
                    volba = input("Skutečně odstranit úkol - (A)no, (N)e : ")
                                  
                    if volba in ('A', 'a'):
                        try:
                            self.db.odstranit_ukol(ukol_index)
                        except:
                            print(f"Nastala chyba: {err}")
                            print("Vracím se do hlavního menu\n")
                            return        
                        print(f"\nÚkolu ID {ukol_index} byl odstraněn\n")                                       
                        vstup_je_ok = True
                    elif volba in ('N', 'n'):
                        vstup_je_ok = True
                        print()
                else:
                    print(f"Úkol s ID '{ukol_index}' neexistuje! Vyberte existující úkol")
    

    def akce_konec_programu(self):
        self.db.close_db()
        self.db = None

        print("\nKonec programu.")


    def _vytiskni_ukol(self, ukol, single_row_style):
        """
        Funkce vypíše úkol na více řádků (single_row_styly = False), nebo úsporně na jeden řádek
        """
        if not single_row_style:
            print(f"Úkol ID #{ukol[0]} -------------------------------\n"
                f"Název:           {ukol[1]}\n"
                f"Popis:           {ukol[2]}\n"
                f"Stav:            {ukol[3]}")
        else: # vypsat úkol na jeden řádek
            print(f"ID {ukol[0]:3}: {ukol[1]} [{ukol[3]}]")


    def _zobraz_menu(self, upozorneni=None):
        """
        Funkce zobrazí menu aplikace a vrátí vstup uživatele
        """
        if upozorneni:
            print(f"\n{upozorneni}\n")

        print("Správce úkolů - Hlavní menu")
        for item in self.polozky_menu:
            print(f"{item}. {self.polozky_menu[item][0]}")

        volba = input(f"Vyberte možnost (1-{len(self.polozky_menu)}): ")
        
        return volba


if __name__ == '__main__':    
    app = TaskManager()
    app.hlavni_menu()    
    app = None

