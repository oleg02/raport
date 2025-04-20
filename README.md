# Генератор рапортів

Цей застосунок — Flask веб-додаток для генерації рапортів із автоматичною та ручною інфлексією ПІБ, зручними підказками та сучасним темним дизайном.

## Як запустити на сервері

1. **Встановіть залежності:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Запустіть Flask-сервер:**
   ```bash
   flask run
   ```
   або
   ```bash
   python app.py
   ```

## Для продакшн-сервера (gunicorn + nginx)

1. Встановіть gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Запустіть застосунок через gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
3. (Опційно) Налаштуйте nginx для проксування на gunicorn.

## Структура проекту
- `app.py` — основний Flask-додаток
- `templates/index.html` — головний шаблон
- `requirements.txt` — залежності
- `README.md` — ця інструкція

## Деплой на хмару
Можна розгорнути на Heroku, Render, Railway, Fly.io або іншому Python-friendly хостингу.

---

**Питання?** Пишіть issue або звертайтесь до автора!
