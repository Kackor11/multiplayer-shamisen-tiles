# Importy z bibliotek
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, Session, select, desc
from pydantic import BaseModel
from datetime import timedelta
from jose import jwt, JWTError
from typing import List

# Importy z plikow
from server.database import engine, get_session
from server.models import User, Score, SystemLog
from server.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM

# --- MODELE DANYCH (Pydantic) ---
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ScoreCreate(BaseModel):
    score: int
    mode: str
    
class UserPasswordChange(BaseModel):
    old_password: str
    new_password: str

class UserDelete(BaseModel):
    password: str

class AdminPasswordReset(BaseModel):
    new_password: str

# Schemat auth
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- WEBSOCKET MANAGER ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """Wysyla wiadomosc do wszystkich podlaczonych klientow"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# --- LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    print("--- BAZA DANYCH ZAINICJOWANA ---")
    yield
    print("--- SERWER ZATRZYMANY ---")
    
app = FastAPI(title="Shamisen Tiles Server", lifespan=lifespan)

# --- FUNKCJE POMOCNICZE ---
def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None: raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError: raise HTTPException(status_code=401, detail="Invalid token")
        
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None: raise HTTPException(status_code=401, detail="User not found")
    return user

def get_current_admin_user(user: User = Depends(get_current_user)):
    """Sprawdza czy uzytkownik ma role 'admin'"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Wymagane uprawnienia administratora")
    return user

# --- ENDPOINT WEBSOCKET ---
@app.websocket("/ws/rankings")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    print(f"--- NOWE POLACZENIE WS: {websocket.client} ---")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"--- ROZLACZONO WS: {websocket.client} ---")

# --- ENDPOINTY ADMINA ---

@app.get("/admin/users")
def admin_get_users(user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """Pobiera liste wszystkich uzytkownikow"""
    return session.exec(select(User)).all()

@app.get("/admin/logs")
def admin_get_logs(user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """Pobiera 50 ostatnich logow systemowych"""
    return session.exec(select(SystemLog).order_by(desc(SystemLog.created_at)).limit(50)).all()

@app.put("/admin/users/{username}/password")
def admin_reset_password(username: str, pass_data: AdminPasswordReset, user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """Admin zmienia haslo uzytkownika"""
    target = session.exec(select(User).where(User.username == username)).first()
    if not target: raise HTTPException(status_code=404, detail="User not found")
    
    target.password_hash = get_password_hash(pass_data.new_password)
    session.add(target)
    session.add(SystemLog(event_type="ADMIN", message=f"Admin {user.username} zmienil haslo dla {username}"))
    session.commit()
    return {"message": "Haslo zresetowane"}

@app.delete("/admin/users/{username}")
def admin_delete_user(username: str, user: User = Depends(get_current_admin_user), session: Session = Depends(get_session)):
    """Admin usuwa uzytkownika"""
    target = session.exec(select(User).where(User.username == username)).first()
    if not target: raise HTTPException(status_code=404, detail="User not found")
    
    scores = session.exec(select(Score).where(Score.player_name == username)).all()
    for s in scores: session.delete(s)
    
    session.delete(target)
    session.add(SystemLog(event_type="ADMIN", message=f"Admin {user.username} usunal uzytkownika {username}"))
    session.commit()
    return {"message": "Uzytkownik usuniety"}

# --- POZOSTALE ENDPOINTY (AUTH, USERS, SCORES) ---
@app.post("/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing: raise HTTPException(status_code=400, detail="Nazwa zajeta")
    
    new_user = User(username=user_data.username, password_hash=get_password_hash(user_data.password))
    session.add(new_user)
    session.add(SystemLog(event_type="AUTH", message=f"Zarejestrowano: {new_user.username}"))
    session.commit()
    return {"message": "Utworzono konto"}

@app.post("/auth/login", response_model=Token)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == user_data.username)).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        session.add(SystemLog(event_type="WARNING", message=f"Blad logowania: {user_data.username}"))
        session.commit()
        raise HTTPException(status_code=400, detail="Bledne dane")
    
    token = create_access_token(data={"sub": user.username, "role": user.role})
    session.add(SystemLog(event_type="AUTH", message=f"Zalogowano: {user.username}"))
    session.commit()
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
def get_user_profile(user: User = Depends(get_current_user)):
    return {"username": user.username, "role": user.role, "created_at": user.created_at.strftime("%Y-%m-%d %H:%M")}

@app.put("/users/me/password")
def change_password(pass_data: UserPasswordChange, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if not verify_password(pass_data.old_password, user.password_hash): raise HTTPException(status_code=400, detail="Zle stare haslo")
    user.password_hash = get_password_hash(pass_data.new_password)
    session.add(user); session.commit()
    return {"message": "Haslo zmienione"}

@app.delete("/users/me")
def delete_account(del_data: UserDelete, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    if not verify_password(del_data.password, user.password_hash): raise HTTPException(status_code=400, detail="Zle haslo")
    username = user.username
    scores = session.exec(select(Score).where(Score.player_name == username)).all()
    for s in scores: session.delete(s)
    session.delete(user); session.commit()
    return {"message": "Konto usuniete"}

@app.post("/scores", status_code=201)
async def add_score(sc: ScoreCreate, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    session.add(Score(player_name=user.username, score=sc.score, mode=sc.mode))
    session.commit()
    
    msg = f"New Score! {user.username} scored {sc.score} in {sc.mode} mode!"
    await manager.broadcast(msg)
    
    return {"message": "Wynik zapisany"}

@app.get("/scores/top/{mode}")
def get_top_scores(mode: str, session: Session = Depends(get_session)):
    return session.exec(select(Score).where(Score.mode == mode).order_by(desc(Score.score)).limit(10)).all()

@app.get("/scores/me/{mode}")
def get_my_scores(mode: str, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Score).where(Score.mode == mode, Score.player_name == user.username).order_by(desc(Score.score)).limit(10)).all()

@app.get("/")
def read_root(): return {"status": "ok"}