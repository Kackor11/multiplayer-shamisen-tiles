from sqlmodel import SQLModel, create_engine, Session

# Nazwa pliku bazy danych
sqlite_file_name = "shamisen.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Tworzenie silnika
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Funkcja pomocnicza do pobierania sesji
def get_session():
    with Session(engine) as session:
        yield session