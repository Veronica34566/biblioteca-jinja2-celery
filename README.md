 Biblioteca + Jinja2 + Celery (KeyDB/Redis)

Extiende la app de biblioteca para **enviar correos** cuando se **agrega** o **elimina** un libro, usando **tareas asíncronas con Celery** y **KeyDB** (interfaz Redis).

## Requisitos
- Python 3.10+
- KeyDB o Redis accesible (KeyDB recomendado)
- Servidor SMTP (o Gmail/Sendgrid, etc.)

## Instalación
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # edita valores SMTP y NOTIFY_EMAIL
```

### Levantar KeyDB rápidamente (Docker)
```bash
docker run --name keydb -p 6379:6379 -d eqalpha/keydb keydb-server --save "" --appendonly no
```

## Inicializar BD y ejecutar
```bash
flask --app app.py init-db
flask --app app.py run
```
Abre: http://127.0.0.1:5000

## Ejecutar el worker de Celery
En otra terminal (con venv activado):
```bash
celery -A celery_app.celery worker --loglevel=info
```
> El broker/resultado se leen de `.env` (variables `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`).

## ¿Qué correos se envían?
- **Agregar libro** → asunto `Libro agregado: <Título>`
- **Eliminar libro** → asunto `Libro eliminado: <Título>`
- Cuerpo dinámico renderizado con Jinja2: `templates/email/book_event.txt`.

## Producción (Gunicorn + Nginx)
- App WSGI:
  ```bash
  gunicorn -w 4 -b 0.0.0.0:8000 'app:app'
  ```
- Worker Celery (systemd/pm2/supervisor):
  ```bash
  celery -A celery_app.celery worker --loglevel=info
  ```
- Asegúrate de exponer KeyDB y variables de entorno en el servicio.

## Estructura
```
app.py
celery_app.py
tasks.py
requirements.txt
.env.example
static/css/styles.css
templates/
  base.html
  _messages.html
  books/
    list.html
    form.html
    confirm_delete.html
  email/
    book_event.txt
```

## Manejo de errores
- Tarea `send_book_email` reintenta hasta 3 veces (delay 10s).
- Si `NOTIFY_EMAIL` no está definido, la app registra advertencia y no envía.
- Errores SMTP quedan en logs del worker Celery.
