from django.http import HttpResponse
from django.core.files.base import ContentFile

from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status, generics
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny

from .models import * 
from .serializers import *

# from .utils import *

import uuid
# Create your views here.

def home(request):
    permission_classes = []
    return HttpResponse("""<!DOCTYPE html>
            <html>
            <head>
            <style>
            .center-container {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh; /* This ensures vertical centering */
            }

            .center-div {
                text-align: center;
            }
            </style>
            </head>
            <body>
            <div class="center-container">
            <div class="center-div">
                <h1 style="display: inline; color: purple;">SafeGaurd</h1>
                <h3>Please <a href="/swagger">click here</a> to go to the swagger page.</h3>
            </div>
            </div>
            </body>
            </html>""")

            
class RegisterView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data
            return Response(user_data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class SignInView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairSerializer

class CameraView(generics.GenericAPIView):
    serializer_class = CameraSerializer
    queryset = Camera.objects.all()

    def post(self, request):
        # cam_status, msg, frame = cameraCheck(request.data['source'])
        cam_status, msg, frame = False, "", None

        data = {
            'name': request.data.get('name', ''),
            'location': request.data.get('location', ''),
            'description': request.data.get('description', ''),
            'source': request.data.get('source', ''),
            'rtsp_status': request.data.get('rtsp_status', cam_status),
            'rtsp_message': request.data.get('rtsp_message', msg),
            'rtsp_frame': request.data.get('rtsp_frame', None),
            'helmet': request.data.get('helmet', False),
            'vest': request.data.get('vest', False),
            'polygons': request.data.get('polygons', ''),
            'email_alert': request.data.get('email_alert', ''),
        }

        # if frame is not None:
        #     _, buffer = cv2.imencode('.jpg', frame)
        #     filename = str(uuid.uuid4()) + '.jpg'
        #     content_file = ContentFile(buffer.tobytes(), name=filename)
        #     data['rtsp_frame'] = content_file

        serializer = self.serializer_class(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CameraDetailView(generics.GenericAPIView):
    serializer_class = CameraSerializer
    queryset = Camera.objects.all()

    def get(self, request, id):
        try:
            camera_instance = self.get_queryset().filter(id=id).first()
            if camera_instance is None:
                return Response({"detail": "Camera not found for the given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(camera_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            camera = self.get_queryset().filter(id=id).first()
            camera.delete()
            return Response({"detail": "deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Camera not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        queryset = self.get_queryset().filter(id=id).first()
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeView(generics.GenericAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployeeDetailView(generics.GenericAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get(self, request, id):
        try:
            employee = self.get_queryset().filter(id=id).first()
            if employee is None:
                return Response({"detail": "Employee not found for the given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            employee = self.get_queryset().filter(id=id).first()
            employee.delete()
            return Response({"detail": "deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        queryset = self.get_queryset().filter(id=id).first()
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)