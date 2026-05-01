"""
Fix alembic version table by setting it to the last valid migration before our new ones.
"""
from sqlalchemy import create_engine, text
from aistudio.core.database import DATABASE_URL

def fix_alembic_version():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check current version
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current = result.fetchone()
        print(f"Current version: {current[0] if current else 'None'}")
        
        # Update to last valid migration before our additions
        conn.execute(text("DELETE FROM alembic_version"))
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('541be14d7255')"))
        conn.commit()
        
        # Verify
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        new_version = result.fetchone()
        print(f"New version: {new_version[0]}")
        print("Alembic version table fixed!")

if __name__ == "__main__":
    fix_alembic_version()
