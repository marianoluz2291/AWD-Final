from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Course, Material, Feedback, Enrollment, Notification, LiveChat

class UserSerializer(serializers.ModelSerializer):
    # Serializer for the User model (other serializers are similar)
    profile = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = User
         # Define fields to be serialized (same as other serializers)
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'profile']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'type_of_user', 'status']

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'teacher', 'course_name', 'course_description', 'course_created']

class MaterialSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Material
        fields = ['id', 'course', 'subject_title', 'file', 'material_created']

class FeedbackSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Feedback
        fields = ['id', 'course', 'feedback_title', 'description', 'date_submitted', 'is_read']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrollment_date', 'blocked']

class NotificationSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    class Meta:
        model = Notification
        fields = ['id', 'user', 'course', 'message', 'created_at', 'is_read']

class LiveChatSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)
    class Meta:
        model = LiveChat
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'is_read', 'image']
