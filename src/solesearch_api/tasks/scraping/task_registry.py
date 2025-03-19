from functools import wraps

from solesearch_api.tasks import app


def register_scraping_task(task_class, name=None):
    """
    Register a scraping task with Celery using the decorator pattern.

    Args:
        task_class: The scraping task class to register
        name: Optional name for the task. If not provided, will use task_class.name

    Returns:
        A Celery task function that wraps the scraping task
    """
    task_instance = task_class()
    # Use the name attribute from the class if available, otherwise use the class name
    task_name = name or f"solesearch_api.tasks.scraping.{task_class.__name__}"

    @app.task(name=task_name, bind=True)
    @wraps(task_instance.run)
    def task_wrapper(self, *args, **kwargs):
        return task_instance.run(*args, **kwargs)

    task_wrapper.task_instance = task_instance
    return task_wrapper
