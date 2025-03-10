from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Profile, Course, Material, Enrollment, Notification, Feedback, LiveChat
from django.core.files.uploadedfile import SimpleUploadedFile


class ViewsTestCase(TestCase):

    def setUp(self):
        # Set up test client
        self.client = Client()

        # Create users
        self.teacher = User.objects.create_user(username='teacher1', password='testpass123')
        self.student = User.objects.create_user(username='student1', password='testpass123')

        # Create teacher and student profiles
        self.teacher_profile = Profile.objects.create(user=self.teacher, type_of_user='teacher')
        self.student_profile = Profile.objects.create(user=self.student, type_of_user='student')

        # Create a course by the teacher
        self.course = Course.objects.create(teacher=self.teacher, course_name='Test Course', course_description='Test Description')

        # Enroll the student in the course
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    # Test registration view
    def test_register_account(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'type_of_user': 'student',  # Assuming 'student' or 'teacher' is a valid option
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect after success


    # Test login view for teacher
    def test_login_teacher(self):
        response = self.client.post(reverse('login'), {
            'username': 'teacher1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse('teacher_homepage'))

    # Test login view for student
    def test_login_student(self):
        response = self.client.post(reverse('login'), {
            'username': 'student1',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse('student_homepage'))

    # Test home redirection based on user type
    def test_home_redirection(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('teacher_homepage'))

        self.client.logout()
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('student_homepage'))

    # Test logout
    def test_logout(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    # Test teacher homepage
    def test_teacher_homepage(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.get(reverse('teacher_homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elearning_app/teacher_homepage.html')
        self.assertIn(self.course, response.context['courses'])  # Ensure course is passed to template

    # Test student homepage
    def test_student_homepage(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('student_homepage'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'elearning_app/student_homepage.html')
        self.assertIn(self.course, response.context['courses'])

    # Test course creation by teacher
    def test_create_course(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.post(reverse('create_course'), {
            'course_name': 'New Course',
            'course_description': 'A new course description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Course.objects.count(), 2)  # Ensure new course created

    # Test enroll in course by student
    def test_enroll_in_course(self):
        self.client.login(username='student1', password='testpass123')
        new_course = Course.objects.create(teacher=self.teacher, course_name='New Test Course', course_description='Test desc')
        response = self.client.post(reverse('enroll_in_course', kwargs={'course_id': new_course.id}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Enrollment.objects.filter(student=self.student, course=new_course).count(), 1)

    # Test adding material to course (by teacher)
    def test_add_material(self):
        self.client.login(username='teacher1', password='testpass123')
        file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
        response = self.client.post(reverse('add_material', kwargs={'course_id': self.course.id}), {
            'subject_title': 'Test Material',
            'file': file
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful material addition
        self.assertEqual(Material.objects.count(), 1)

    # Test feedback submission by student
    def test_send_feedback(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.post(reverse('send_feedback', kwargs={'course_id': self.course.id}), {
            'feedback_title': 'Great Course',
            'description': 'The course was really informative.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Feedback.objects.count(), 1)

    # Test notification for new material for student
    def test_notification_for_new_material(self):
        self.client.login(username='teacher1', password='testpass123')
        file = SimpleUploadedFile("test_file.txt", b"file_content", content_type="text/plain")
        response = self.client.post(reverse('add_material', kwargs={'course_id': self.course.id}), {
            'subject_title': 'New Material',
            'file': file
        })
        self.assertEqual(Notification.objects.filter(user=self.student, course=self.course).count(), 1)

    # Test chat between teacher and student
    def test_chat_messages(self):
        LiveChat.objects.create(sender=self.student, receiver=self.teacher, message='Hello teacher')
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('chat_messages', kwargs={'room_chat': 'teacher1'}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello teacher', response.content.decode())

    # Test blocking a student
    def test_block_student(self):
        self.client.login(username='teacher1', password='testpass123')
        response = self.client.post(reverse('block_student', kwargs={'student_id': self.student.id}))
        self.enrollment.refresh_from_db()
        self.assertTrue(self.enrollment.blocked)
        self.assertEqual(response.status_code, 302)

    # Test notification read 
    def test_notification_read(self):
        notification = Notification.objects.create(user=self.student, course=self.course, message='New lesson added')
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('notification_read', kwargs={'notification_id': notification.id}))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

