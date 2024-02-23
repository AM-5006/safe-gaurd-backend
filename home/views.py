from django.http import HttpResponse
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.paginator import Paginator,EmptyPage,InvalidPage

from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination,LimitOffsetPagination
from rest_framework.decorators import api_view, schema

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import * 
from .serializers import *

import uuid
from datetime import timedelta
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
        try:
            import cv2
            from .utils import cameraCheck
            cam_status, msg, frame = cameraCheck(request.data['source'])
        except Exception as e:
            cam_status, msg, frame = False, "", None

        data = {
            'name': request.data.get('name', ''),
            'location': request.data.get('location', ''),
            'description': request.data.get('description', ''),
            'source': request.data.get('source', ''),
            'rtsp_status': request.data.get('rtsp_status', cam_status),
            'rtsp_message': request.data.get('rtsp_message', msg),
            'helmet': request.data.get('helmet', False),
            'vest': request.data.get('vest', False),
            'polygons': request.data.get('polygons', ''),
            'email_alert': request.data.get('email_alert', ''),
        }

        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            filename = str(uuid.uuid4()) + '.jpg'
            content_file = ContentFile(buffer.tobytes(), name=filename)
            data['rtsp_frame'] = content_file

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
    pagination_class = PageNumberPagination
    def post(self, request):
        data = request.data
        if isinstance(data, list):
            responses = []
            for item in data:
                serializer = self.serializer_class(data=item)
                if serializer.is_valid():
                    serializer.save()
                    responses.append(serializer.data)
                else:
                    return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            return Response(responses, status=status.HTTP_201_CREATED)
        else:
            serializer = self.serializer_class(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        page = request.query_params.get('page', 1)
        paginator = Paginator(self.get_queryset(), 10)

        try:
            serializer = self.serializer_class(paginator.page(page), many=True)
        except (InvalidPage, EmptyPage) as e:
            return Response({'error':'No results found'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployeeDetailView(generics.GenericAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get(self, request, id):
        try:
            employee = self.get_queryset().filter(emp_id=id).first()
            if employee is None:
                return Response({"detail": "Employee not found for the given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(employee)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            employee = self.get_queryset().filter(emp_id=id).first()
            employee.delete()
            return Response({"detail": "deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        queryset = self.get_queryset().filter(emp_id=id).first()
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncidentView(generics.GenericAPIView):
    serializer_class = IncidentSerializer
    permission_classes = [AllowAny]
    queryset = Incident.objects.all()
    pagination_class = PageNumberPagination
    def get(self, request):
        page = request.query_params.get('page', 1)
        paginator = Paginator(self.get_queryset(), 10)
        try:
            serializer = self.serializer_class(paginator.page(page), many=True)
        except (InvalidPage, EmptyPage) as e:
            return Response({"error":"No results found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error':e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class IncidentDetailView(generics.GenericAPIView):
    serializer_class = IncidentSerializer
    permission_classes = [AllowAny]
    queryset = Incident.objects.all()

    def get(self, request, id):
        try:
            incident = self.get_queryset().filter(id=id).first()
            if incident is None:
                return Response({"detail": "Incident not found for the given ID"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.serializer_class(incident)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "An error occurred"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id):
        try:
            incident = self.get_queryset().filter(id=id).first()
            incident.delete()
            return Response({"detail": "deleted"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": "Incident not found"}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, id):
        queryset = self.get_queryset().filter(id=id).first()
        serializer = self.serializer_class(queryset, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IncidentAnalyticsView(generics.GenericAPIView):
    serializer_class = IncidentSerializer
    permission_classes = []
    queryset = Incident.objects.all()
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'value',
                openapi.IN_QUERY,
                description="Value for time interval",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'unit',
                openapi.IN_QUERY,
                description="Unit for time interval (minutes, hours, etc.)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ]
    )
    def get(self, request):
        value = request.query_params.get('value', 15)
        unit = request.query_params.get('unit', 'minutes')

        if unit.lower() == 'minutes':
            delta = timedelta(minutes=int(value))
        elif unit.lower() == 'hours':
            delta = timedelta(hours=int(value))
        elif unit.lower() == 'days':
            delta = timedelta(days=int(value))
        elif unit.lower() == 'weeks':
            delta = timedelta(weeks=int(value))
        elif unit.lower() == 'months':
            delta = timedelta(days=int(value) * 30)
        elif unit.lower() == 'years':
            delta = timedelta(days=int(value) * 365)
        else:
            return Response({"error":"Please enter proper value and unit"}, status=status.HTTP_400_BAD_REQUEST)

        threshold_time = timezone.now() - delta
        queryset = self.get_queryset().filter(timestamp__gte=threshold_time)

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)