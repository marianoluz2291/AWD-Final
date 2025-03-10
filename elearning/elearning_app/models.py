from django.db import models
from django.contrib.auth.models import User

# User profile model
class Profile(models.Model):
    # choices for user type
    USER_SELECTION = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )
    # choices for user availability status
    STATUS_SELECTION = (
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('unavailable', 'Unavailable'),
    )

    # one to one relationship with User model from Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # either teacher or student as the user
    type_of_user = models.CharField(max_length=7, choices=USER_SELECTION)
    status = models.CharField(max_length=12, choices=STATUS_SELECTION, default='available')

    def __str__(self):
        return self.user.username

# Course model
class Course(models.Model):
    #FK to user
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    course_name = models.CharField(max_length=255, null=True, blank=True)
    course_description = models.TextField()
    course_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.course_name

# Material model
class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    subject_title = models.CharField(max_length=255, default="Untitled")
    file = models.FileField(upload_to='materials/')
    material_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject_title} for {self.course.course_name}"

# Feedback model
class Feedback(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_title = models.CharField(max_length=255)
    description = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback for {self.course.course_name} - {self.feedback_title}"

# Enrollment model
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    blocked = models.BooleanField(default=False) # # Indicator if the enrollment is blocked

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.course_name}"

# Notification model
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"

# LiveChat model
class LiveChat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)  # Store base64 image data
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}'
