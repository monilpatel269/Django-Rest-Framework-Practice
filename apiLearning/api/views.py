from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from api.models import Subject, Student, Teacher, User
from api.serializers import SubjectSerializer, StudentSerializer, TeacherSerializer, UserSerializer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import login, authenticate, logout, get_user_model

# Get the custom user model
CustomUser = get_user_model()

# Create your views here.
def index(request):
    return render(request, "api/index.html")


class UserAPIView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                user = CustomUser.objects.filter(id=id)
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = UserSerializer(user)
        else:
            users = CustomUser.objects.filter()
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = None
            user = CustomUser.objects.create_user(**serializer.validated_data)
            response_data = UserSerializer(user).data

            if user:
                token_data = get_tokens_for_user(user)
                response_data["refresh_token"] = token_data["refresh"]
                response_data["access_token"] = token_data["access"]

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id=None):
        if id:
            try:
                subject = Subject.objects.get(id=id)
            except Subject.DoesNotExist:
                return Response(
                    {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = SubjectSerializer(subject)
        else:
            subjects = Subject.objects.filter()
            serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SubjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            subject = Subject.objects.get(id=id)
        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = SubjectSerializer(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            subject = Subject.objects.get(id=id)
        except Subject.DoesNotExist:
            return Response(
                {"error": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )

        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentAPIView(APIView):
    def get(self, request, id=None):
        if id:
            try:
                student = Student.objects.prefetch_related('subjects__teachers').get(id=id)
            except Student.DoesNotExist:
                return Response(
                    {"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = StudentSerializer(student)
        else:
            students = Student.objects.prefetch_related('subjects__teachers').all()
            serializer = StudentSerializer(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            student = Student.objects.get(id=id)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(student, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            student = Student.objects.get(id=id)
        except Student.DoesNotExist:
            return Response(
                {"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND
            )
        student.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherAPIView(APIView):
    def get(self, request, id=None):
        if id:
            # Retrieve a single teacher
            try:
                teacher = Teacher.objects.prefetch_related('subjects__students').get(id=id)
            except Teacher.DoesNotExist:
                return Response(
                    {"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND
                )
            serializer = TeacherSerializer(teacher)
        else:
            # Retrieve all teachers
            teachers = Teacher.objects.prefetch_related('subjects__students').all()
            serializer = TeacherSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = TeacherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        try:
            teacher = Teacher.objects.get(id=id)
        except Teacher.DoesNotExist:
            return Response(
                {"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeacherSerializer(teacher, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            teacher = Teacher.objects.get(id=id)
        except Teacher.DoesNotExist:
            return Response(
                {"error": "Teacher not found"}, status=status.HTTP_404_NOT_FOUND
            )

        teacher.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
