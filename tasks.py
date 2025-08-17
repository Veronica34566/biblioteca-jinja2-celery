from celery_app import celery
from flask_mail import Message
from flask import render_template, current_app
from app import mail


@celery.task(bind=True, max_retries=3, default_retry_delay=10)
def send_book_email(self, action, title, author, year, recipient):
    """
    Envía un correo usando Flask-Mail dentro del contexto de Flask (gracias a ContextTask).
    action: 'added' | 'deleted'
    """
    try:
        if not recipient:
            current_app.logger.warning("send_book_email: recipient vacío, abortando.")
            return "no-recipient"

        human_action = "agregado" if action == "added" else "eliminado"
        subject = f"Libro {human_action}: {title}"
        body = render_template(
            "email/book_event.txt",
            action=human_action,
            title=title,
            author=author,
            year=year,
        )

        msg = Message(subject=subject, recipients=[recipient])
        msg.body = body
        mail.send(msg)
        current_app.logger.info("Correo enviado a %s", recipient)
        return "ok"
    except Exception as exc:
        current_app.logger.exception("Fallo enviando correo, reintentando...")
        raise self.retry(exc=exc)
