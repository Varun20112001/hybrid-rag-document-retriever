from django.urls import path

from document.api.document_controller import DocumentStatusView, SearchView, UploadDocumentView

urlpatterns = [
    path("documents/upload", UploadDocumentView.as_view(), name="upload-document"),
    path("documents/<uuid:document_id>/status", DocumentStatusView.as_view(), name="document-status"),
    path("search", SearchView.as_view(), name="search"),
]
