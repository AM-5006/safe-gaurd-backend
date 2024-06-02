from django.http import StreamingHttpResponse, HttpResponse
from django.utils import timezone
from django.core.files.base import ContentFile

from django.db.models import Count
from django.db.models.functions import ExtractYear, ExtractMonth, ExtractHour, ExtractMinute

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status, generics
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import * 
from .serializers import *

import uuid
from datetime import timedelta
import calendar
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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
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
        try:
            serializer = self.serializer_class(self.get_queryset(), many=True)
        except Exception as e:
            return Response({'error':e}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployeeDetailView(generics.GenericAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    def get(self, request):
        try:
            serializer = self.serializer_class(self.get_queryset(), many=True)
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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'unit',
                openapi.IN_QUERY,
                description="Unit for time interval (hour,day etc.)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'query_type',
                openapi.IN_QUERY,
                description="type of query",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    def get(self, request):
        try:
            query_type = request.query_params.get('query_type', None)
            if query_type == 'IOT':
                return self.get_incidents_over_time(request)
            elif query_type == 'IDF':
                return self.get_identifications_record(request)
            elif query_type == 'RID':
                return self.get_recent_incidents(request)
            elif query_type == 'IBC':
                return self.get_incident_by_category(request)
            else:
                return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)
        
    def get_incidents_over_time(self, request):
        try:
            data = None
            unit = request.query_params.get('unit', 'hour')

            today = timezone.now().date()
            start_time = timezone.make_aware(timezone.datetime.combine(today, timezone.datetime.min.time()))  
            end_time = timezone.now()

            if unit == 'hour':
                hour_ago = end_time - timedelta(hours=1)
                incidents_last_hour = self.get_queryset().filter(timestamp__range=(hour_ago, end_time)).annotate(hour=ExtractHour('timestamp'), minute=ExtractMinute('timestamp')).values('hour', 'minute').annotate(count=Count('id'))
                data = [{'hour': incident['hour'], 'minute': incident['minute'], 'count': incident['count']} for incident in incidents_last_hour]
            elif unit == 'day':
                last_24_hours = end_time - timedelta(hours=24)
                incidents_last_24_hours = self.get_queryset().filter(timestamp__range=(last_24_hours, end_time)).values('timestamp__hour').annotate(count=Count('id'))
                data = [{'hour': incident['timestamp__hour'], 'count': incident['count']} for incident in incidents_last_24_hours]
            elif unit == 'week':
                last_week = end_time - timedelta(days=7)
                incidents_last_week = self.get_queryset().filter(timestamp__range=(last_week, end_time)).values('timestamp__date').annotate(count=Count('id'))
                data = [{'date': incident['timestamp__date'], 'count': incident['count']} for incident in incidents_last_week]
            elif unit == 'month':
                last_30_days = end_time - timedelta(days=30)
                incidents_last_30_days = self.get_queryset().filter(timestamp__range=(last_30_days, end_time)).values('timestamp__date').annotate(count=Count('id'))
                data = [{'date': incident['timestamp__date'], 'count': incident['count']} for incident in incidents_last_30_days]
            elif unit == 'year':
                current_year = today.year
                current_month = today.month
                start_time = today.replace(day=1) - timedelta(days=365)  
                end_time = today.replace(day=1) + timedelta(days=31)  
                incidents_last_n_months = self.get_queryset().filter(timestamp__range=(start_time, end_time)).annotate(year=ExtractYear('timestamp'), month=ExtractMonth('timestamp')).values('year', 'month').annotate(count=Count('id'))
                data = [{'month': calendar.month_name[incident['month']], 'year': incident['year'], 'count': incident['count']} for incident in incidents_last_n_months if (incident['year'] < current_year) or (incident['year'] == current_year and incident['month'] <= current_month)]
                
            return Response({'data': data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get_identifications_record(self, request):
        try:
            serializer = self.serializer_class(self.get_queryset(), many=True)
            unidentified_incidents, identified_incidents = 0, 0

            for incident in serializer.data:
                if not incident["employee"]:
                    unidentified_incidents += 1
                else:
                    identified_incidents += 1

            response_data = {
                "undentified_incidents": unidentified_incidents,
                "identified_incidents": identified_incidents,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)

    def get_recent_incidents(self, request):
        try:
            queryset = self.get_queryset().order_by('-timestamp')[:5]
            serializer = self.serializer_class(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)

    def get_incident_by_category(self, request):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            no_vest, no_helmet, restricted_area = 0, 0, 0 
            for incident in serializer.data:
                if 'No-Vest' in incident['incident']:
                    no_vest += 1
                if 'No-Helmet' in incident['incident']:
                    no_helmet += 1
                if 'Restricted area' in incident['incident']:
                    restricted_area += 1
            return Response({'No-Vest': no_vest, 'No-Helmet': no_helmet, 'Restricted area': restricted_area}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'data':'error'}, status=status.HTTP_400_BAD_REQUEST)