"""
seeders/context_seeder.py

Seeder для заполнения базы данных тестовыми данными контекстного управления.
"""

from aistudio.core.database import SessionLocal
from aistudio.models.subject_type import SubjectType
from aistudio.models.role import Role
from aistudio.models.subject import Subject
from aistudio.models.user_subject import UserSubject
from aistudio.utils.security import hash_password
from aistudio.models.user import User

# Тестовые данные для типов субъектов
TEST_SUBJECT_TYPES = [
    {"name": "Школа", "slug": "school"},
    {"name": "Класс", "slug": "class"},
    {"name": "Предмет", "slug": "subject"},
    {"name": "Урок", "slug": "lesson"},
    {"name": "Группа", "slug": "group"},
]

# Тестовые данные для ролей
TEST_ROLES = [
    {"name": "Владелец", "slug": "owner"},
    {"name": "Редактор", "slug": "editor"},
    {"name": "Посетитель", "slug": "viewer"},
]

# Тестовые данные для субъектов
TEST_SUBJECTS = [
    {"name": "Московская школа №1", "type_slug": "school", "parent_name": None},
    {"name": "Московская школа №2", "type_slug": "school", "parent_name": None},
    {"name": "10А класс", "type_slug": "class", "parent_name": "Московская школа №1"},
    {"name": "10Б класс", "type_slug": "class", "parent_name": "Московская школа №1"},
    {"name": "11А класс", "type_slug": "class", "parent_name": "Московская школа №2"},
    {"name": "Математика", "type_slug": "subject", "parent_name": "10А класс"},
    {"name": "Физика", "type_slug": "subject", "parent_name": "10А класс"},
    {"name": "История", "type_slug": "subject", "parent_name": "10Б класс"},
    {"name": "Алгебра", "type_slug": "lesson", "parent_name": "Математика"},
    {"name": "Геометрия", "type_slug": "lesson", "parent_name": "Математика"},
]

# Тестовые данные для связей пользователь-субъект
TEST_USER_SUBJECTS = [
    {"user_login": "admin1@example.com", "subject_name": "Московская школа №1", "role_slug": "owner"},
    {"user_login": "admin2@example.com", "subject_name": "Московская школа №2", "role_slug": "owner"},
    {"user_login": "user1@example.com", "subject_name": "10А класс", "role_slug": "editor"},
    {"user_login": "user2@example.com", "subject_name": "10Б класс", "role_slug": "editor"},
    {"user_login": "user3@example.com", "subject_name": "Математика", "role_slug": "viewer"},
]


def seed_subject_types():
    """Заполняет таблицу типов субъектов."""
    db = SessionLocal()
    try:
        for type_data in TEST_SUBJECT_TYPES:
            exists = db.query(SubjectType).filter_by(slug=type_data["slug"]).first()
            if not exists:
                subject_type = SubjectType(
                    name=type_data["name"],
                    slug=type_data["slug"]
                )
                db.add(subject_type)
        
        db.commit()
        print("✅ Subject types seeded successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding subject types: {e}")
        return False
    finally:
        db.close()


def seed_roles():
    """Заполняет таблицу ролей."""
    db = SessionLocal()
    try:
        for role_data in TEST_ROLES:
            exists = db.query(Role).filter_by(slug=role_data["slug"]).first()
            if not exists:
                role = Role(
                    name=role_data["name"],
                    slug=role_data["slug"]
                )
                db.add(role)
        
        db.commit()
        print("✅ Roles seeded successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding roles: {e}")
        return False
    finally:
        db.close()


def seed_subjects():
    """Заполняет таблицу субъектов."""
    db = SessionLocal()
    try:
        # Сначала получаем все типы субъектов
        subject_types = {st.slug: st.id for st in db.query(SubjectType).all()}
        
        # Создаем словарь для отслеживания созданных субъектов
        created_subjects = {}
        
        for subject_data in TEST_SUBJECTS:
            exists = db.query(Subject).filter_by(name=subject_data["name"]).first()
            if not exists:
                # Получаем type_id
                type_id = subject_types.get(subject_data["type_slug"])
                if not type_id:
                    print(f"⚠️ Warning: Subject type '{subject_data['type_slug']}' not found")
                    continue
                
                # Получаем parent_id
                parent_id = None
                if subject_data["parent_name"]:
                    parent = db.query(Subject).filter_by(name=subject_data["parent_name"]).first()
                    if parent:
                        parent_id = parent.id
                    else:
                        print(f"⚠️ Warning: Parent subject '{subject_data['parent_name']}' not found")
                
                subject = Subject(
                    name=subject_data["name"],
                    type_id=type_id,
                    parent_id=parent_id
                )
                db.add(subject)
                db.flush()  # Получаем ID созданного субъекта
                created_subjects[subject.name] = subject.id
        
        db.commit()
        print("✅ Subjects seeded successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding subjects: {e}")
        return False
    finally:
        db.close()


def seed_user_subjects():
    """Заполняет таблицу связей пользователь-субъект."""
    db = SessionLocal()
    try:
        # Получаем все роли
        roles = {r.slug: r.id for r in db.query(Role).all()}
        
        for connection_data in TEST_USER_SUBJECTS:
            # Получаем пользователя
            user = db.query(User).filter_by(login=connection_data["user_login"]).first()
            if not user:
                print(f"⚠️ Warning: User '{connection_data['user_login']}' not found")
                continue
            
            # Получаем субъект
            subject = db.query(Subject).filter_by(name=connection_data["subject_name"]).first()
            if not subject:
                print(f"⚠️ Warning: Subject '{connection_data['subject_name']}' not found")
                continue
            
            # Получаем роль
            role_id = roles.get(connection_data["role_slug"])
            if not role_id:
                print(f"⚠️ Warning: Role '{connection_data['role_slug']}' not found")
                continue
            
            # Проверяем, существует ли уже связь
            exists = db.query(UserSubject).filter_by(
                user_id=user.id,
                subject_id=subject.id
            ).first()
            
            if not exists:
                user_subject = UserSubject(
                    user_id=user.id,
                    subject_id=subject.id,
                    role_id=role_id
                )
                db.add(user_subject)
        
        db.commit()
        print("✅ User subjects seeded successfully!")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding user subjects: {e}")
        return False
    finally:
        db.close()


def seed_all():
    """Заполняет все таблицы тестовыми данными."""
    print("🌱 Starting context seeder...")
    
    # Проверяем, что пользователи существуют
    db = SessionLocal()
    users = db.query(User).all()
    db.close()
    
    if not users:
        print("⚠️ Warning: No users found. Please run user_seeder.py first!")
        return False
    
    print(f"📊 Found {len(users)} users in database")
    
    # Заполняем таблицы в правильном порядке
    success = True
    
    if not seed_subject_types():
        success = False
    
    if not seed_roles():
        success = False
    
    if not seed_subjects():
        success = False
    
    if not seed_user_subjects():
        success = False
    
    if success:
        print("\n🎉 Context seeder completed successfully!")
        print("📋 Created test data:")
        print(f"  - {len(TEST_SUBJECT_TYPES)} subject types")
        print(f"  - {len(TEST_ROLES)} roles")
        print(f"  - {len(TEST_SUBJECTS)} subjects")
        print(f"  - {len(TEST_USER_SUBJECTS)} user-subject connections")
    else:
        print("\n❌ Context seeder failed!")
    
    return success


if __name__ == "__main__":
    seed_all() 