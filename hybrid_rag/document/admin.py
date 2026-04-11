from django.contrib import admin

from .models import DocumentChunkModel, DocumentModel, ProcessingRunModel

@admin.register(DocumentModel)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'filename', 'created_at')
    search_fields = ('filename',)

@admin.register(DocumentChunkModel)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'chunk_index', 'created_at')
    search_fields = ('document__filename', 'chunk_index')


admin.site.register(ProcessingRunModel)
