from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Profile, Course, Material, Feedback, Enrollment, Notification, LiveChat
from .serializers import UserSerializer, ProfileSerializer, CourseSerializer, MaterialSerializer, FeedbackSerializer, EnrollmentSerializer, NotificationSerializer, LiveChatSerializer

class UserViewSet(viewsets.ModelViewSet): 
    # Define the query set for the user, which will return all user (similar to other query set)
    queryset = User.objects.all()
    # Specify the serializer class to use for the User model (similar to the other viewset)
    serializer_class = UserSerializer 

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

class LiveChatViewSet(viewsets.ModelViewSet):
    queryset = LiveChat.objects.all()
    serializer_class = LiveChatSerializer
