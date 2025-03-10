from django.contrib import admin
from django.contrib.auth.models import User
from .models import Profile, Course, Material, Feedback, Enrollment, Notification, LiveChat

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    # Define which fields to display in the list view of Course model (other admin are similar)
    list_display = ('course_name', 'course_description', 'course_created')
    # Define which fields to enable searching for in the Course model (other admin are similar)
    search_fields = ('course_name',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_of_user', 'status')
    search_fields = ('user__username', 'type_of_user')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('subject_title', 'course', 'material_created')
    search_fields = ('subject_title', 'course__course_name')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_title', 'course', 'date_submitted', 'is_read')
    search_fields = ('feedback_title', 'course__course_name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrollment_date', 'blocked')
    search_fields = ('student__username', 'course__course_name')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'message', 'created_at', 'is_read')
    search_fields = ('user__username', 'course__course_name', 'message')

@admin.register(LiveChat)
class LiveChatAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message', 'timestamp', 'is_read')
    search_fields = ('sender__username', 'receiver__username', 'message')
