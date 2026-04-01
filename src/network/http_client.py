import requests
from src.core.config import SERVER_URL

class HTTPClient:
    def __init__(self):
        self.base_url = SERVER_URL
        self.token = None
        self.username = None
    
    # --- AUTH ---
    def register(self, username, password):
        try:
            res = requests.post(f"{self.base_url}/auth/register", json={"username": username, "password": password}, timeout=5)
            return (True, "OK") if res.status_code == 201 else (False, f"Error {res.status_code}")
        except: return False, "Server error"

    def login(self, username, password):
        try:
            res = requests.post(f"{self.base_url}/auth/login", json={"username": username, "password": password}, timeout=5)
            if res.status_code == 200:
                data = res.json()
                self.token = data.get("access_token")
                self.username = username
                return True, "Zalogowano!"
            return False, "Bledne dane"
        except: return False, "Server error"

    # --- USER ---
    def get_profile_data(self):
        if not self.token: return None
        try:
            res = requests.get(f"{self.base_url}/users/me", headers={"Authorization": f"Bearer {self.token}"}, timeout=3)
            return res.json() if res.status_code == 200 else None
        except: return None

    def change_password(self, old, new):
        if not self.token: return False, "No token"
        try:
            res = requests.put(f"{self.base_url}/users/me/password", json={"old_password": old, "new_password": new}, headers={"Authorization": f"Bearer {self.token}"})
            return (True, "OK") if res.status_code == 200 else (False, "Error")
        except: return False, "Error"

    def delete_account(self, password):
        if not self.token: return False, "No token"
        try:
            res = requests.request("DELETE", f"{self.base_url}/users/me", json={"password": password}, headers={"Authorization": f"Bearer {self.token}"})
            if res.status_code == 200:
                self.token = None
                return True, "Deleted"
            return False, "Error"
        except: return False, "Error"

    # --- SCORES ---
    def send_score(self, score, mode):
        if not self.token: return
        try: requests.post(f"{self.base_url}/scores", json={"score": score, "mode": mode}, headers={"Authorization": f"Bearer {self.token}"}, timeout=2)
        except: pass

    def get_ranking(self, mode, type="global"):
        url = f"{self.base_url}/scores/top/{mode}" if type == "global" else f"{self.base_url}/scores/me/{mode}"
        headers = {"Authorization": f"Bearer {self.token}"} if type != "global" else {}
        try:
            res = requests.get(url, headers=headers, timeout=3)
            return res.json() if res.status_code == 200 else []
        except: return []

    # --- ADMIN ---
    def admin_get_users(self):
        if not self.token: return []
        try:
            res = requests.get(f"{self.base_url}/admin/users", headers={"Authorization": f"Bearer {self.token}"}, timeout=3)
            return res.json() if res.status_code == 200 else []
        except: return []

    def admin_get_logs(self):
        if not self.token: return []
        try:
            res = requests.get(f"{self.base_url}/admin/logs", headers={"Authorization": f"Bearer {self.token}"}, timeout=3)
            return res.json() if res.status_code == 200 else []
        except: return []

    def admin_delete_user(self, username):
        if not self.token: return False
        try:
            res = requests.delete(f"{self.base_url}/admin/users/{username}", headers={"Authorization": f"Bearer {self.token}"})
            return res.status_code == 200
        except: return False

    def admin_reset_password(self, username, new_pass):
        if not self.token: return False
        try:
            res = requests.put(f"{self.base_url}/admin/users/{username}/password", json={"new_password": new_pass}, headers={"Authorization": f"Bearer {self.token}"})
            return res.status_code == 200
        except: return False

api_client = HTTPClient()