import aiosqlite
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "bot_data.db"


async def init_db():
    """Инициализация базы данных с тестовыми данными"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Таблица пользователей
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                user_type TEXT,
                company_name TEXT,
                contact TEXT,
                created_at TEXT
            )
        """)
        
        # Таблица заявок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                title TEXT,
                description TEXT,
                salary TEXT,
                location TEXT,
                contact TEXT,
                created_at TEXT,
                FOREIGN KEY (company_id) REFERENCES users (user_id)
            )
        """)
        
        await db.commit()
        
        # Проверяем, есть ли уже тестовые данные
        cursor = await db.execute("SELECT COUNT(*) FROM vacancies")
        count = await cursor.fetchone()
        
        if count[0] == 0:
            # Добавляем тестовые заявки
            test_vacancies = [
                (999001, "Senior Python Developer", 
                 "Ищем опытного Python разработчика для работы над backend системами. "
                 "Требования: Python 3.9+, FastAPI/Django, PostgreSQL, Docker.",
                 "250,000 - 350,000 руб", "Москва (удаленно)", "@tech_company_hr", datetime.now().isoformat()),
                
                (999002, "Frontend React Developer",
                 "Разработка современных веб-приложений на React. "
                 "Требования: React 18+, TypeScript, Redux, опыт от 2 лет.",
                 "180,000 - 280,000 руб", "Санкт-Петербург", "@spb_tech_hr", datetime.now().isoformat()),
                
                (999003, "DevOps Engineer",
                 "Настройка и поддержка CI/CD, управление инфраструктурой. "
                 "Требования: Kubernetes, AWS/GCP, Terraform, Ansible.",
                 "200,000 - 300,000 руб", "Москва", "@devops_company", datetime.now().isoformat()),
                
                (999004, "Data Scientist",
                 "Анализ данных, построение ML моделей. "
                 "Требования: Python, pandas, scikit-learn, PyTorch/TensorFlow.",
                 "220,000 - 320,000 руб", "Удаленно", "@data_team_lead", datetime.now().isoformat()),
                
                (999005, "QA Automation Engineer",
                 "Автоматизация тестирования веб и мобильных приложений. "
                 "Требования: Python/Java, Selenium, Pytest, опыт от 1 года.",
                 "150,000 - 220,000 руб", "Казань", "@qa_manager", datetime.now().isoformat()),
            ]
            
            await db.executemany("""
                INSERT INTO vacancies (company_id, title, description, salary, location, contact, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, test_vacancies)
            
            await db.commit()
            logger.info("Тестовые данные успешно добавлены")


async def save_user(user_id: int, username: str, user_type: str, 
                   company_name: str = None, contact: str = None):
    """Сохранение/обновление пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO users (user_id, username, user_type, company_name, contact, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, user_type, company_name, contact, datetime.now().isoformat()))
        await db.commit()


async def get_user(user_id: int):
    """Получение пользователя"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        return await cursor.fetchone()


async def create_vacancy(company_id: int, title: str, description: str, 
                        salary: str, location: str, contact: str):
    """Создание заявки"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO vacancies (company_id, title, description, salary, location, contact, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (company_id, title, description, salary, location, contact, datetime.now().isoformat()))
        await db.commit()
        return cursor.lastrowid


async def get_vacancies(limit: int = 10, offset: int = 0):
    """Получение списка заявок с пагинацией"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT * FROM vacancies 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        return await cursor.fetchall()


async def get_vacancies_count():
    """Получение общего количества заявок"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM vacancies")
        result = await cursor.fetchone()
        return result[0]
