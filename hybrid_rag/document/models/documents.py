from django.db import models
import uuid

class DocumentModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, 
        editable=False,
        db_comment="Unique identifier for the document"
    )

    filename = models.CharField(
        max_length=512, db_comment="Name of the document file",
        db_column="filename"
    )

    content_type = models.CharField(
        max_length=128, db_comment="Type of the document content", 
        db_column="content_type"
    )

    size = models.BigIntegerField(
        db_comment="Size of the document in bytes", 
        db_column="size"
    )

    status = models.CharField(
        max_length=16, db_index=True, db_comment="Status of the document", 
        db_column="status"
    )

    storage_path = models.CharField(
        max_length=1024, db_comment="Path where the document is stored", 
        db_column="storage_path"
    )

    error_message = models.TextField(
        blank=True, null=True, db_comment="Error message if the document processing failed", 
        db_column="error_message"
    )

    created_at = models.DateTimeField(
        auto_now_add=True, db_comment="Timestamp when the document was created", 
        db_column="created_at"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, db_comment="Timestamp when the document was last updated", 
        db_column="updated_at"
    )
    

    def __str__(self):
        return self.filename
    
    
    class Meta:
        db_table = "documents"
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ["-created_at"]