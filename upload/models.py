from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from drf_yasg import openapi


class ResponseFailModelSerializer(serializers.Serializer):
    error = serializers.BooleanField(default=True)
    message = serializers.CharField(max_length=255)


class ResponseSuccessModelSerializer(serializers.Serializer):
    url = serializers.URLField()


class RequestSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=255)
    bucket_name = serializers.CharField(
        max_length=255, required=True)
    image = serializers.ImageField(required=True)

from inflection import humanize