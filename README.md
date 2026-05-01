# AI Studio - Платформа управления контекстами

## 📋 Описание

AI Studio - это современная платформа для управления образовательными контекстами, построенная на FastAPI и SQLAlchemy. Система предоставляет инструменты для создания иерархических структур образовательных учреждений, управления ролями пользователей и контроля доступа к различным контекстам.

## 🏗️ Архитектура

### Технологический стек
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - система миграций базы данных
- **MySQL** - реляционная база данных
- **JWT** - аутентификация и авторизация
- **Pydantic** - валидация данных и сериализация
- **Poetry** - управление зависимостями

### Архитектурные слои
```
┌─────────────────┐
│   Controllers   │ ← HTTP endpoints
├─────────────────┤
│    Services     │ ← Business logic
├─────────────────┤
│  Repositories   │ ← Data access
├─────────────────┤
│     Models      │ ← Database entities
└─────────────────┘
```

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.8+
- MySQL 8.0+
- Poetry

### Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/lumi/aiStudio.git
cd aiStudio
```

2. **Установите зависимости**
```bash
poetry install
```

3. **Настройте переменные окружения**
```bash
# .env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=aistudi_db

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

4. **Создайте базу данных**
```sql
CREATE DATABASE aistudi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Запустите миграции**
```bash
poetry run alembic upgrade head
```

6. **Заполните тестовыми данными**
```bash
# Создайте пользователей
python aistudio/seeders/user_seeder.py

# Создайте контекстные данные
python aistudio/seeders/context_seeder.py
```

7. **Запустите сервер**
```bash
poetry run uvicorn aistudio.main:app --reload --host 127.0.0.1 --port 8000
```

8. **Откройте Swagger UI**
```
http://127.0.0.1:8000/docs
```

## 📊 Модель данных

### Основные сущности

#### Пользователь (User)
- `id` - уникальный идентификатор
- `login` - email пользователя
- `name` - имя пользователя
- `password` - хешированный пароль
- `role` - роль (user/admin)
- `created_dt`, `updated_dt`, `deleted_dt` - временные метки

#### Тип субъекта (SubjectType)
- `id` - уникальный идентификатор
- `name` - наименование типа
- `slug` - короткое обозначение
- Временные метки

#### Субъект (Subject)
- `id` - уникальный идентификатор
- `name` - наименование субъекта
- `type_id` - ссылка на тип субъекта
- `parent_id` - ссылка на родительский субъект (иерархия)
- Временные метки

#### Роль (Role)
- `id` - уникальный идентификатор
- `name` - наименование роли
- `slug` - короткое обозначение
- Временные метки

#### Связь пользователь-субъект (UserSubject)
- `user_id` - ссылка на пользователя
- `subject_id` - ссылка на субъект
- `role_id` - ссылка на роль в данном контексте
- Временные метки

## 🔐 Аутентификация и авторизация

### JWT токены
- **Access Token** - для доступа к API (30 минут)
- **Refresh Token** - для обновления access token (7 дней)

### Роли пользователей
- **admin** - полный доступ ко всем функциям
- **user** - ограниченный доступ

### Роли в контекстах
- **owner** - владелец контекста
- **editor** - редактор контекста
- **viewer** - просмотр контекста

## 📡 API Endpoints

### Пользователи (`/api/v1/users/`)
- `POST /register` - регистрация пользователя
- `POST /login` - вход в систему
- `POST /refresh` - обновление токена
- `POST /logout` - выход из системы
- `GET /` - список всех пользователей (admin)
- `GET /{user_id}` - информация о пользователе
- `PUT /{user_id}/role` - изменение роли пользователя (admin)
- `DELETE /{user_id}` - мягкое удаление пользователя

### Типы субъектов (`/api/v1/subject-types/`)
- `POST /` - создание типа субъекта (admin)
- `GET /` - список всех типов субъектов (admin)
- `GET /{type_id}` - информация о типе субъекта (admin)
- `GET /slug/{slug}` - поиск по slug (admin)
- `PUT /{type_id}` - обновление типа субъекта (admin)
- `DELETE /{type_id}` - мягкое удаление (admin)
- `DELETE /{type_id}/hard` - жесткое удаление (admin)

### Субъекты (`/api/v1/subjects/`)
- `POST /` - создание субъекта (admin)
- `GET /` - список всех субъектов (admin)
- `GET /{subject_id}` - информация о субъекте (admin)
- `GET /type/{type_id}` - субъекты определенного типа (admin)
- `GET /root/all` - корневые субъекты (admin)
- `GET /{subject_id}/hierarchy` - иерархия субъекта (admin)
- `GET /{subject_id}/children-tree` - дерево дочерних элементов (admin)
- `GET /search/name/{name}` - поиск по названию (admin)
- `PUT /{subject_id}` - обновление субъекта (admin)
- `PUT /{subject_id}/move` - перемещение в иерархии (admin)
- `DELETE /{subject_id}` - мягкое удаление (admin)
- `DELETE /{subject_id}/hard` - жесткое удаление (admin)
- `POST /filter` - фильтрация субъектов (admin)

### Роли (`/api/v1/roles/`)
- `POST /` - создание роли (admin)
- `GET /` - список всех ролей (admin)
- `GET /{role_id}` - информация о роли (admin)
- `GET /slug/{slug}` - поиск по slug (admin)
- `GET /default/all` - стандартные роли (admin)
- `POST /default/create` - создание стандартных ролей (admin)
- `PUT /{role_id}` - обновление роли (admin)
- `DELETE /{role_id}` - мягкое удаление (admin)
- `DELETE /{role_id}/hard` - жесткое удаление (admin)

### Связи пользователь-субъект (`/api/v1/user-subjects/`)
- `POST /` - создание связи (admin)
- `GET /` - список всех связей (admin)
- `GET /user/{user_id}` - связи пользователя (admin)
- `GET /subject/{subject_id}` - связи субъекта (admin)
- `GET /user/{user_id}/subject/{subject_id}` - конкретная связь (admin)
- `PUT /user/{user_id}/subject/{subject_id}/role/{new_role_id}` - изменение роли (admin)
- `POST /assign` - назначение пользователя к субъекту (admin)
- `DELETE /user/{user_id}/subject/{subject_id}` - удаление связи (admin)
- `POST /filter` - фильтрация связей (admin)

## 🧪 Тестирование

### Запуск интеграционных тестов
```bash
python test_integration.py
```

### Тестовые данные
Система поставляется с готовыми тестовыми данными:
- 5 типов субъектов (школа, класс, предмет, урок, группа)
- 3 роли (владелец, редактор, посетитель)
- 10 субъектов с иерархической структурой
- 5 связей пользователь-субъект

### Тестовые пользователи
- **admin1@example.com** / admin123 (admin)
- **admin2@example.com** / admin456 (admin)
- **user1@example.com** / password1 (user)
- **user2@example.com** / password2 (user)
- **user3@example.com** / password3 (user)

## 🔧 Разработка

### Структура проекта
```
aiStudio/
├── aistudio/
│   ├── api/v1/           # HTTP контроллеры
│   ├── config/           # Конфигурация
│   ├── core/             # Основные компоненты
│   ├── dependencies/     # Зависимости FastAPI
│   ├── migration/        # Миграции базы данных
│   ├── models/           # SQLAlchemy модели
│   ├── repositories/     # Слой доступа к данным
│   ├── schemas/          # Pydantic схемы
│   ├── seeders/          # Тестовые данные
│   ├── services/         # Бизнес-логика
│   └── utils/            # Утилиты
├── alembic.ini          # Конфигурация Alembic
├── pyproject.toml       # Зависимости Poetry
└── README.md            # Документация
```

### Создание миграции
```bash
poetry run alembic revision --autogenerate -m "Description"
poetry run alembic upgrade head
```

### Добавление нового API endpoint
1. Создайте модель в `models/`
2. Создайте схемы в `schemas/`
3. Создайте репозиторий в `repositories/`
4. Создайте сервис в `services/`
5. Создайте контроллер в `api/v1/`
6. Добавьте роут в `main.py`

## 📈 Производительность

### Оптимизации
- Использование индексов в базе данных
- Ленивая загрузка связей SQLAlchemy
- Кэширование JWT токенов
- Пагинация для больших списков

### Мониторинг
- Логирование всех операций
- Метрики производительности
- Обработка ошибок

## 🔒 Безопасность

### Меры безопасности
- Хеширование паролей (bcrypt)
- JWT токены с ограниченным временем жизни
- Валидация входных данных (Pydantic)
- Защита от SQL-инъекций (SQLAlchemy)
- Авторизация на уровне ролей

### Рекомендации по безопасности
- Используйте HTTPS в продакшене
- Регулярно обновляйте зависимости
- Мониторьте логи на подозрительную активность
- Используйте сильные пароли
- Ограничивайте доступ к базе данных

## 🚀 Развертывание

### Продакшен
1. Настройте переменные окружения
2. Используйте production базу данных
3. Настройте HTTPS
4. Настройте мониторинг
5. Настройте бэкапы

### Docker (опционально)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install
CMD ["poetry", "run", "uvicorn", "aistudio.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📞 Поддержка

### Полезные команды
```bash
# Запуск сервера разработки
poetry run uvicorn aistudio.main:app --reload

# Создание миграции
poetry run alembic revision --autogenerate -m "Description"

# Применение миграций
poetry run alembic upgrade head

# Откат миграции
poetry run alembic downgrade -1

# Запуск тестов
python test_integration.py

# Создание тестовых данных
python aistudio/seeders/context_seeder.py
```

### Логи
- Логи приложения: `logs/app.log`
- Логи ошибок: `logs/error.log`
- Логи доступа: `logs/access.log`

## 📄 Лицензия

MIT License

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

---

**AI Studio** - современная платформа для управления образовательными контекстами 🎓
