from django.urls import path

from .views import *

urlpatterns = [
    path('signup/', RegisterView.as_view(), name="signup"),
    path('signin/', SignInView.as_view(), name='signin'),
    
    path('employee/', EmployeeView.as_view(), name="employee"),
    path('employee/<str:id>/', EmployeeDetailView.as_view(), name="employee-detail"),
    
    path('camera/', CameraView.as_view(), name="camera"),
    path('camera/<str:id>/', CameraDetailView.as_view(), name='camera-detail'),
]
