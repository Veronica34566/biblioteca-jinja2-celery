from celery import Celery
from app import app  # importa la instancia Flask ya configurada


def make_celery(flask_app):
    broker_url = flask_app.config.get("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    backend_url = flask_app.config.get("CELERY_RESULT_BACKEND", None)

    celery = Celery(flask_app.import_name, broker=broker_url, backend=backend_url)
    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


# Celery app listo para usar en workers
celery = make_celery(app)
