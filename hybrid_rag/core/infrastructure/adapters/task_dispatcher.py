from core.application.interfaces import TaskDispatcher


class CeleryTaskDispatcher(TaskDispatcher):
    def dispatch_document_processing(self, document_id):
        from document.tasks import process_document_task

        task = process_document_task.delay(str(document_id))
        return task.id
