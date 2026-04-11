from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class SearchSerializer(serializers.Serializer):
    query = serializers.CharField()
    mode = serializers.ChoiceField(choices=["keyword", "semantic", "hybrid"], default="hybrid")
    top_k = serializers.IntegerField(min_value=1, max_value=50, default=10)
    filters = serializers.DictField(required=False, default=dict)
