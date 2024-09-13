from django.urls import path
from api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("", views.index, name="index"),
    path("users/", views.UserAPIView.as_view()),
    path("users/<int:id>/", views.UserAPIView.as_view()),

    path("subjects/", views.SubjectAPIView.as_view()),
    path("subjects/<int:id>/", views.SubjectAPIView.as_view()),
    
    path("students/", views.StudentAPIView.as_view()),
    path("students/<int:id>/", views.StudentAPIView.as_view()),
    
    path("teachers/", views.TeacherAPIView.as_view()),
    path("teachers/<int:id>/", views.TeacherAPIView.as_view()),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
