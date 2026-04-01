from typing import Optional
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone

# Tabela Użytkowników
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    role: str = Field(default="user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Tabela Wyników
class Score(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    player_name: str
    score: int
    mode: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
# Tabela Logów Systemowych
class SystemLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))