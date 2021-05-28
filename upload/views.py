import logging

from rest_framework import views
from upload.models import ResponseFailModelSerializer, ResponseSuccessModelSerializer, RequestSerializer
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
import boto3
import os
from core.utils import convertToWebp
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import FileUploadParser, FormParser, MultiPartParser
from rest_framework.decorators import parser_classes

access_key_src = os.environ.get("AWS_ACCESS_KEY_ID")
secret_key_src = os.environ.get("AWS_SECRET_ACCESS_KEY")
region_name = os.environ.get("AWS_REGION_NAME")
bucket_name = os.environ.get("AWS_MEDIA_BUCKET_NAME")

logger = logging.Logger(__name__)

print(access_key_src)
class CustomResponse(Response):
    def __init__(self, webpName: str, direction: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fileName = webpName
        self.direction = direction

    def remove_file(self):
        os.remove(self.fileName)
        if self.direction:
            os.rmdir(self.direction)

    def close(self):
        super().close()
        self.remove_file()


class ImageUploadView(views.APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(operation_description="Upload other image to web image in s3",
                         responses={400: ResponseFailModelSerializer,
                                    200: ResponseSuccessModelSerializer},
                         request_body=RequestSerializer, operation_id="upload_image")
    def post(self, requests):
        headers = {
            "Access-Control-Allow-Origin": "*"
        }

        prefix = requests.POST.get('prefix')

        s3 = boto3.resource('s3', region_name=region_name,
                            aws_access_key_id=access_key_src,
                            aws_secret_access_key=secret_key_src)
        try:
            bucket_name = requests.POST.get("bucket_name")
            bucket = s3.Bucket(bucket_name)
        except Exception as e:
            logger.error(e)
            response = ResponseFailModelSerializer(
                {"message": "Bucket name is not valid"})
            return Response(response.data, status=400, headers=headers)

        try:
            direction = ""
            prefix = requests.POST.get('prefix')
            if prefix:
                direction = str(requests.data["prefix"]) + "/"

            if direction and not os.path.exists(direction):
                os.makedirs(direction)

            data = requests.data["image"]
            file_name = data.name
            webpName = convertToWebp(data, direction+file_name)

            # upload to webp
            bucket.upload_file(webpName, webpName,
                               ExtraArgs={"ContentType": "image/webp",
                                          'ACL': 'public-read'})
            data = {
                "url": "https://" + bucket_name + ".s3.amazonaws.com/" + webpName
            }
            response = ResponseSuccessModelSerializer(data)

            return CustomResponse(webpName=webpName, direction=direction, data=response.data, status=200, headers=headers)

        except Exception as ex:
            logger.error(ex)
            response = ResponseFailModelSerializer(
                {"message": "Upload was fail."})
            return Response(response.data, status=400, headers=headers)
