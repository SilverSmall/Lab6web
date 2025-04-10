 Система управління студентськими гуртожитками

Цей проект реалiзує REST API для управлiння студентськими гуртожитками за допомогою FastAPI.

Функцiонал

CRUD операцiї для кiмнат, студентiв, комунальних платежiв та iнвентарю.

Звiти про стан примiщень.

Бронювання кiмнат студентами.

Автоматично згенерована API-документацiя (Swagger UI).

Встановлення та запуск



1. Створення вiртуального середовища

python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate  # для Windows

2. Встановлення залежностей

pip install -r requirements.txt

3. Запуск сервера

uvicorn main:app --reload

📘 API-документацiя

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

✨ Приклад запиту (Додавання кiмнати)

POST /rooms/

{
  "id": 1,
  "name": "Кiмната 101",
  "capacity": 2,
  "occupied": false,
  "condition": "Гарний"
}

🔎 TODO

Додати базу даних (SQLAlchemy + PostgreSQL)

Реалiзувати аутентифiкацiю користувачiв

🚀 Готово до розширення!

