# uruchomienie bazy w terminalu
uvicorn server.app:app --reload
uvicorn server.app:app --host 0.0.0.0 --port 8000 --reload
pip install -r requirements.txt

SERVER_IP = os.getenv("SHAMISEN_SERVER_IP", "127.0.0.1")
SERVER_URL = f"http://{SERVER_IP}:8000"

# automatyczna dokumentacja (Swagger UI) - klient do testowania
http://127.0.0.1:8000/docs

# Przydatne polecenia:
- git init – inicjuje repozytorium GIT w danym katalogu
- git add plik – dodaje zmiany w podanym pliku do commita
- podanie kropki (.) zamiast nazwy pliku sprawi, że do commita zostaną dodaje wszystkie zmienione pliki
- git add origin URL – ustawia podany adres zdalnego repozytorium jako główne repozytorium
- git commit -m treść – dodaje opis do commita
- git commit --append – zmienia opis ostatniego udostępnionego commita
- git push – wysyła zmiany do zdalnego branacha
- z parametrem -f – wysyła zmiany do zdalnego repozytorium ignorując konflikty (nadpisanie)
- z origin branch – wysyła nowego brancha do zdalnego repozytorium
- git pull – pobiera najnowsze zmiany z aktywnego brancha zdalnego
- git clone URL – klonuje zdalne repozytorium
- git stash – dodanie zmienionych plików do pamięci i usunięcie ich z aktywnego brancha
- git checkout branch – zmienia aktywny branch na inny
- z parametrem -b – tworzy nowego brancha i przełączenie się na niego
- git checkout plik – usuwa zmiany w pliku
- podanie kropki (.) zamiast nazwy pliku sprawi, zostaną usunięte zmiany we wszystkich plikach
- git merge branch – scalenie zawartości z zawartością znajdującą się na innym branchu
- git branch – wyświetla listę lokalnych branchy
- z parametrem -r – wyświetla listę zdalnych branchy
- git branch -d branch – usuwa lokalnego brancha (nie można usunąć aktualnego)
- git status – wyświetla listę zmienionych plików
- git diff plik – wyświetla informacje na temat zmian w pliku
- git reset HEAD – resetowanie nie wysłanych commitów, zmodyfikowane pliki można ponownie dodać
- z parametrem --hard – usuwa wszystkie zmiany z lokalnego brancha i przywraca zmiany z zdalnego brancha
- git reset HEAD~liczba – usuwa liczba liczba ostatnich commitów
- git rebase master – zaciąga zmiany z brancha głównego do brancha aktywnego
- git push origin :branch – usuwa zdalnego brancha
- git remote add origin URL – powiązanie za zdalnym repozytorium