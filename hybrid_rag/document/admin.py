from django.contrib import admin

from .models import DocumentChunkModel, DocumentModel, ProcessingRunModel

admin.site.register(DocumentModel)
admin.site.register(DocumentChunkModel)
admin.site.register(ProcessingRunModel)
