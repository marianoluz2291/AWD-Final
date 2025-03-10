from django.urls import path, include
from . import views
from rest_framework import routers
from .api import (  # Import the viewsets from api.py
    UserViewSet, ProfileViewSet, CourseViewSet, MaterialViewSet, 
    FeedbackViewSet, EnrollmentViewSet, NotificationViewSet, LiveChatViewSet
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="eLearning API",
      default_version='v1',
      description="eLearning API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Create a router and register the API viewsets
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'feedbacks', FeedbackViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'livechats', LiveChatViewSet)

urlpatterns = [
    path('', views.home, name='home'), #homepage
    path('register/', views.register_account, name='register'), #register acc page
    path('login/', views.user_login, name='login'), # login page
    path('logout/', views.user_logout, name='logout'), # logout -> home page
    path('teacher/home/', views.teacher_homepage, name='teacher_homepage'), # teacher homepage
    path('student/home/', views.student_homepage, name='student_homepage'), #student homepage
    path('course/<int:course_id>/', views.course_information, name='course_information'), # Route to view course information, identified by course_id
    path('course/create/', views.create_course, name='create_course'), # create a new course
    path('course/<int:course_id>/add-material/', views.add_material, name='add_material'), # add a lesson material to the course
    path('material/<int:material_id>/delete/', views.delete_material, name='delete_material'), # delete material from the course
    path('course/<int:course_id>/enroll/', views.enroll_in_course, name='enroll_in_course'), #students to enroll in a course
    path('notifications/<int:notification_id>/read/', views.notification_read, name='notification_read'), # Route to mark a notification as read, identified by notification_id
    path('people/', views.full_people, name='full_people'), #full list of the students enrolled and teachers
    path('student/<int:student_id>/', views.student_information, name='student_information'), # view the information of a specific student
    path('student/<int:student_id>/remove/', views.student_removed, name='student_removed'), # student being removed from the course
    path('student/<int:student_id>/block/', views.block_student, name='block_student'), # student get blocked to a course and will have no access to the materials
    path('feedback/<int:feedback_id>/', views.view_feedback, name='view_feedback'), # teacher to see feedback given by students
    path('feedback/<int:course_id>/send/', views.send_feedback, name='send_feedback'), # student give feedback to teacher
    path('status/', views.current_status, name='current_status'), #the current availability of the student and teacher
    path('student/teachers/', views.student_teacher_list, name='student_teacher_list'), # view the list of teachers and students for a student
    path('teacher/contact/', views.teacher_contact_student, name='teacher_contact_student'), #teacher to contact a student
    path('chat/<str:room_chat>/', views.chat_messages, name='chat_messages'), # view chat messages in a specific chat room, identified by room_chat
    path('chat/save_message/', views.save_message, name='save_message'), # Route to save a chat message
    path('people/all_students/', views.student_records, name='student_records'), # records of all students enrolled
    path('people/all_teachers/', views.teacher_records, name='teacher_records'), #records of all teachers
    path('api/', include(router.urls)), # Route to include API routes from the router
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]