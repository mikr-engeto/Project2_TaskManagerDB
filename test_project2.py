import pytest
from mysql_db import DbLayer

# Zde nakonfiguruj připojení k DB a název testovací tabulky. 
# POZOR! Testovací tabulka je dočasná, na konci testu je smazána!
konfigurace_db_pro_testovani = {
        "host"          : "localhost",      # Adresa serveru
        "user"          : "user",           # Uživatelské jméno
        "password"      : "password",       # Heslo k databázi
        "database"      : "taskmanager",    # Název databáze 
        "table_name"    : "ukoly_test"      # Název tabulky pro ukládání úkolů, na konci bude smazána
}

# příprava databáze
@pytest.fixture(scope="module")
def fixture_db():    
    db = DbLayer(
        host=konfigurace_db_pro_testovani["host"],
        user=konfigurace_db_pro_testovani["user"],
        password=konfigurace_db_pro_testovani["password"],
        database=konfigurace_db_pro_testovani["database"],
        table_name=konfigurace_db_pro_testovani["table_name"]
    )
    db.pripojeni_db(check_table_exists=True)

    # přidám do tabulky 1 záznam, který použiju v testech pro funkce aktualizovat_ukol() a odstranit_ukol()
    db.pridat_ukol("TEST ukol", "TEST popis")
    
    yield db

    # smažu testovací tabulku
    db.cursor.execute(f"DROP TABLE {db._table_name};")
    # ukončím spojení s DB
    db.close_db()
    db = None


# TEST: pozitivní test pridat_ukol()
# test vytvoří v DB nový úkol
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("name,desc,exp_result", [["První úkol", "Popis prvního úkolu", 1]])
def test_pridat_ukol_positive(name, desc, exp_result, fixture_db):
    result = -1
    try:
        result = fixture_db.pridat_ukol(name, desc)
        assert result == exp_result, "Funkce pridat_ukol() měla vrátit hodnotu 1, ale vrátila: {result}"
    except:
        assert result == exp_result, "V průběhu testu nastala neočekávaná výjimka. Test neprošel"


# TEST: negativní test pridat_ukol()
# v názvu úkolu jsou apostrofy, insert skončí výjimkou
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("name,desc,exp_result", [["Nevalidní 'úkol'", "Popis nevalidního úkolu", Exception]])
def test_pridat_ukol_negative(name, desc, exp_result, fixture_db):
    with pytest.raises(exp_result):
        fixture_db.pridat_ukol(name, desc)
    

# TEST: pozitivní test aktualizovat_ukol()
# Funkce aktualizuje stav úkolu ID#1 na 'hotovo'
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("ukol_id,novy_stav,exp_result", [[1, "hotovo", 1]])
def test_aktualizovat_ukol_positive(ukol_id, novy_stav, exp_result, fixture_db):
    result = -1
    try:
        result = fixture_db.aktualizovat_ukol(ukol_id, novy_stav)
        assert result == exp_result, "Funkce aktuailzovat_ukol() měla vrátit hodnotu 1, ale vrátila: {result}"
    except:
        assert result == exp_result, "V průběhu testu nastala neočekávaná výjimka. Test neprošel"


# TEST: negativní test aktualizovat_ukol()
# funkce se pokusí aktualizovat neexistující úkol ID#99 - vrátí se ValueError
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("ukol_id,novy_stav,exp_result", [[99, "hotovo", ValueError]])
def test_aktualizovat_ukol_negative(ukol_id, novy_stav, exp_result, fixture_db):
    with pytest.raises(exp_result):
        fixture_db.aktualizovat_ukol(ukol_id, novy_stav)


# TEST: pozitivní test odstranit_ukol()
# funkce smaže úkol ID#1, který byl vytvořen v rámci fixture
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("ukol_id, exp_result", [[1, 1]])
def test_odstranit_ukol_positive(ukol_id, exp_result, fixture_db):
    result = -1
    try:
        result = fixture_db.odstranit_ukol(ukol_id)
        assert result == exp_result, "Funkce odstranit_ukol() měla vrátit hodnotu 1, ale vrátila: {result}"
    except:
        assert result == exp_result, "V průběhu testu nastala neočekávaná výjimka. Test neprošel"


# TEST: negativní test odstranit_ukol()
# funkce se pokusí odstranit neexistující úkol s ID#99 a vrátí se ValueError
# Prerekvizity:
# - ve fixture byla vytvořena tabulka a v ní jeden záznam s ID#1
@pytest.mark.parametrize("ukol_id, exp_result", [[99, ValueError]])
def test_odstranit_ukol_negative(ukol_id, exp_result, fixture_db):
    with pytest.raises(exp_result):
        fixture_db.odstranit_ukol(ukol_id)
