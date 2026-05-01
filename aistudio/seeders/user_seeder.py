from aistudio.core.database import SessionLocal
from aistudio.models.user import User
from aistudio.models.jwt_token import JWTToken
from aistudio.utils.security import hash_password

TEST_USERS = [
    {"login": "331946", "name": "Regular User 1", "password": "password1", "role": "user"},
    {"login": "user2@example.com", "name": "Regular User 2", "password": "password2", "role": "user"},
    {"login": "user3@example.com", "name": "Regular User 3", "password": "password3", "role": "user"},
    {"login": "admin1@example.com", "name": "Admin User 1", "password": "admin123", "role": "admin"},
    {"login": "admin2@example.com", "name": "Admin User 2", "password": "admin456", "role": "admin"},
]

def seed_users():
    db = SessionLocal()
    for user_data in TEST_USERS:
        exists = db.query(User).filter_by(login=user_data["login"]).first()
        if not exists:
            user = User(
                login=user_data["login"],
                name=user_data["name"],
                password=hash_password(user_data["password"]),
                role=user_data["role"],
                is_active=True
            )
            db.add(user)
    db.commit()
    db.close()
    print("Test users seeded!")
    print("Created users:")
    for user_data in TEST_USERS:
        print(f"  - {user_data['login']} (role: {user_data['role']})")

if __name__ == "__main__":
    seed_users() 