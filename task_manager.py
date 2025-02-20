class TaskManager:

    def __init__(self):
        self.ukoly = []
        self.polozky_menu = {
            "1" : ["Přidat nový úkol", self.pridat_ukol],
            "2" : ["Zobrazit všechny úkoly", self.zobrazit_ukoly],
            "3" : ["Aktualizovat úkol", self.aktualizovat_ukol],
            "4" : ["Odstranit úkol", self.odstranit_ukol],
            "5" : ["Konec programu", self.konec_programu],
        }
        self.volba_konec = "5"


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


    def pridat_ukol(self):
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
        self.ukoly.append(ukol)

        print(f"Úkol '{ukol["nazev"]}' byl přidán.\n")


    def zobrazit_ukoly(self):
        """
        Funkce zobrazí všechny evodované úkoly
        """

        if len(self.ukoly) > 0:
            print("\nSeznam úkolů:")
            for ukol_index, ukol in enumerate(self.ukoly):
                print(f"{ukol_index + 1}. {ukol['nazev']} - {ukol['popis']}")
            print() # prázdný řádek pro lepší čitelnost
        else:
            print(f"\nSeznam úkolů je prázdný\n")

        return len(self.ukoly)


    def aktualizovat_ukol(self):
        """
        Funkce provede aktualizaci stavu úkolu
        """
        # zobrazím všechny úkoly, ať je z čeho vybírat
        if not self.zobrazit_ukoly():
            return

        vstup_je_ok = False

        while not vstup_je_ok:

            volba = input("Zadejte číslo úkolu, který chcete odstranit: ")

            ukol_index = -1 # nevalidní index
            try:
                ukol_index = int(volba)
                # pozor, indexy v seznamu začínají 0, musím odečíst 1
                ukol_index -= 1
            except:
                ukol_index = -1

            print() # vytisknu prázdný řádek pro lešpí čitelnost

            #validace vstupu
            if (ukol_index >= 0) and (ukol_index < len(self.ukoly)):
                vstup_je_ok = True
                ukol = self.ukoly[ukol_index]
                print(f"Úkol: {ukol_index} - {ukol['nazev']}, stav: {ukol}")
                volba_stav = input(f"Zvolte nový stav úkolu: (P)robíhá, (H)otovo")
                if (volba_stav in ('P', 'p')):
                    pass # provést update
                elif (volba_stav in ('H', 'h')):
                    pass # provést update
                else:
                    print(f"Zadaná volba '{volba_stav}' je neplatná!")
            else:
                print(f"\nZadaná volba '{volba}' je neplatná! Zadejte existující číslo úkolu.\n")


    def odstranit_ukol(self):
        """
        Funkce odstraní požadovaný úkol ze seznamu
        """

        # zobrazím všechny úkoly, ať je z čeho vybírat
        if not self.zobrazit_ukoly():
            return

        vstup_je_ok = False

        while not vstup_je_ok:

            volba = input("Zadejte číslo úkolu, který chcete odstranit: ")

            ukol_index = -1 # nevalidní index
            try:
                ukol_index = int(volba)
                # pozor, indexy v seznamu začínají 0, musím odečíst 1
                ukol_index -= 1
            except:

                ukol_index = -1

            #validace vstupu
            if (ukol_index >= 0) and (ukol_index < len(self.ukoly)):
                ukol = self.ukoly[ukol_index]
                self.ukoly.pop(ukol_index)
                print(f"\nÚkol '{ukol["nazev"]}' byl odstraněn.\n")
                vstup_je_ok = True
            else:
                print(f"\nZadaná volba '{volba}' je neplatná! Zadejte existující číslo úkolu.\n")


    def konec_programu(self):
        print("\nKonec programu.")


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

