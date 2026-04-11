from pathlib import Path

from django.conf import settings
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.application.dto import SearchInput, UploadDocumentInput
from core.infrastructure.services.container import (
    build_search_use_case,
    build_status_use_case,
    build_upload_use_case,
)
from document.api.serializers import SearchSerializer, UploadSerializer


class UploadDocumentView(APIView):
    def post(self, request):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        file_obj = serializer.validated_data["file"]
        upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        path = upload_dir / file_obj.name

        with path.open("wb+") as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)

        use_case = build_upload_use_case()
        result = use_case.execute(
            UploadDocumentInput(
                filename=file_obj.name,
                content_type=file_obj.content_type or "application/octet-stream",
                size=file_obj.size,
                storage_path=str(path),
            )
        )
        return Response({"document_id": str(result.document_id), "status": result.status}, status=status.HTTP_202_ACCEPTED)


class DocumentStatusView(APIView):
    def get(self, request, document_id: str):
        use_case = build_status_use_case()
        result = use_case.execute(document_id)
        if result is None:
            raise Http404("Document not found")
        return Response(
            {
                "document_id": str(result.document_id),
                "status": result.status,
                "error_message": result.error_message,
            }
        )


class SearchView(APIView):
    def post(self, request):
        serializer = SearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        use_case = build_search_use_case()
        result = use_case.execute(
            SearchInput(
                query=payload["query"],
                mode=payload.get("mode", "hybrid"),
                top_k=payload.get("top_k", 10),
                filters=payload.get("filters", {}),
            )
        )

        return Response(
            {
                "query": result.query,
                "mode": result.mode,
                "results": [
                    {
                        "chunk_id": str(item.chunk_id),
                        "document_id": str(item.document_id),
                        "text": item.text,
                        "metadata": item.metadata,
                        "scores": {
                            "bm25": item.bm25_score,
                            "vector": item.vector_score,
                            "rrf": item.rrf_score,
                            "rerank": item.rerank_score,
                        },
                    }
                    for item in result.results
                ],
            }
        )
