from rest_framework import serializers
from api.models import Subject, Student, Teacher, User


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    is_active = serializers.BooleanField(default=True)
    is_admin = serializers.BooleanField(default=False)
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    created_on = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.is_staff = validated_data.get("is_staff", instance.is_staff)
        instance.is_superuser = validated_data.get(
            "is_superuser", instance.is_superuser
        )

        return instance
    
    def validate(self, attrs):
        if attrs['email']:
            user_obj = User.objects.filter(email=attrs['email'], is_active=True).first()
            if user_obj is not None:
                raise serializers.ValidationError("User already exist.")
        return attrs


class SubjectSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    created_on = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        sub_obj, _ = Subject.objects.get_or_create(**validated_data)
        return sub_obj

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.save()
        return instance


class StudentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    roll = serializers.IntegerField(default=0)
    subjects = SubjectSerializer(many=True, required=False)
    teachers = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)

    def get_teachers(self, student):
        # Get all subjects the student is related to
        subjects = student.subjects.all()
        teachers_set = set()

        # Loop through each subject and get the students related to it
        for subject in subjects:
            teachers_set.update(subject.teachers.all())  # Add students to the set (avoiding duplicates)

        # Serialize the students data using the StudentSerializer
        teachers = TeacherSerializer(teachers_set, many=True)
        return teachers.data

    def create(self, validated_data):
        subjects_data = validated_data.pop("subjects", [])
        student, _ = Student.objects.get_or_create(**validated_data)

        for subject_data in subjects_data:
            subject, _ = Subject.objects.get_or_create(**subject_data)
            student.subjects.add(subject)

        return student

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.roll = validated_data.get("roll", instance.roll)

        subjects_data = validated_data.get("subjects", [])
        if subjects_data:
            instance.subjects.clear()
        for subject_data in subjects_data:
            subject, _ = Subject.objects.get_or_create(**subject_data)
            instance.subjects.add(subject)

        instance.save()
        return instance


class TeacherSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    subjects = SubjectSerializer(many=True, required=False)
    # students = serializers.SerializerMethodField()
    created_on = serializers.DateTimeField(read_only=True)

    def get_students(self, teacher):
        # Get all subjects the teacher is related to
        subjects = teacher.subjects.all()
        students_set = set()

        # Loop through each subject and get the students related to it
        for subject in subjects:
            students_set.update(subject.students.all())  # Add students to the set (avoiding duplicates)

        # Serialize the students data using the StudentSerializer
        students = StudentSerializer(students_set, many=True)
        return students.data

    def create(self, validated_data):
        subjects_data = validated_data.pop("subjects", [])
        teacher, _ = Teacher.objects.get_or_create(**validated_data)

        for subject_data in subjects_data:
            subject, _ = Subject.objects.get_or_create(**subject_data)
            teacher.subjects.add(subject)

        return teacher

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)

        subjects_data = validated_data.get("subjects", [])
        if subjects_data:
            instance.subjects.clear()
        for subject_data in subjects_data:
            subject, _ = Subject.objects.get_or_create(**subject_data)
            instance.subjects.add(subject)

        instance.save()
        return instance
