from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Profile, Course, Material, Feedback, Enrollment, Notification, LiveChat


class ModelsTestCase(TestCase):

    def setUp(self):
        # Create users
        self.teacher = User.objects.create_user(username='teacher1', password='test0123')
        self.student = User.objects.create_user(username='student1', password='test0123')

        # Create profiles
        self.teacher_profile = Profile.objects.create(user=self.teacher, type_of_user='teacher')
        self.student_profile = Profile.objects.create(user=self.student, type_of_user='student')

        # Create course
        self.course = Course.objects.create(teacher=self.teacher, course_name='Test Course', course_description='Test Description')

        # Create material
        self.material = Material.objects.create(course=self.course, subject_title='Test Material', file='path/to/testfile')

        # Create feedback
        self.feedback = Feedback.objects.create(course=self.course, feedback_title='Test Feedback', description='Good course modules')

        # Enroll the student in the course
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

        # Create notification
        self.notification = Notification.objects.create(user=self.student, course=self.course, message='New lesson has been added')

        # Create live chat message
        self.live_chat = LiveChat.objects.create(sender=self.student, receiver=self.teacher, message='Hello teacher!')

    # Test Profile creation
    def test_create_profile(self):
        self.assertEqual(self.teacher_profile.user.username, 'teacher1')
        self.assertEqual(self.teacher_profile.type_of_user, 'teacher')
        self.assertEqual(self.teacher_profile.status, 'available')

        # Test the student profile
        self.assertEqual(self.student_profile.user.username, 'student1')
        self.assertEqual(self.student_profile.type_of_user, 'student')
        self.assertEqual(self.student_profile.status, 'available')

    # Test Course creation
    def test_create_course(self):
        self.assertEqual(self.course.course_name, 'Test Course')
        self.assertEqual(self.course.teacher, self.teacher)

    # Test Material creation
    def test_create_material(self):
        self.assertEqual(self.material.subject_title, 'Test Material')
        self.assertEqual(self.material.course, self.course)

    # Test Feedback creation
    def test_create_feedback(self):
        self.assertEqual(self.feedback.feedback_title, 'Test Feedback')
        self.assertEqual(self.feedback.course, self.course)
        self.assertFalse(self.feedback.is_read)

    # Test Enrollment creation
    def test_create_enrollment(self):
        self.assertEqual(self.enrollment.student, self.student)
        self.assertEqual(self.enrollment.course, self.course)
        self.assertFalse(self.enrollment.blocked)

    def test_create_notifications(self):
        # Notification for the teacher when a student enrolls in the course
        teacher_notification = Notification.objects.create(
            user=self.teacher, 
            course=self.course, 
            message='A student has enrolled in your course'
        )

        # Assert teacher's notification
        self.assertEqual(teacher_notification.message, 'A student has enrolled in your course')
        self.assertEqual(teacher_notification.user, self.teacher)
        self.assertFalse(teacher_notification.is_read)

        # Notification for the student when a new lesson is added
        student_notification = Notification.objects.create(
            user=self.student,
            course=self.course,
            message='A new lesson has been added'
        )

        # Assert student's notification
        self.assertEqual(student_notification.message, 'A new lesson has been added')
        self.assertEqual(student_notification.user, self.student)
        self.assertFalse(student_notification.is_read)

    # Test LiveChat creation
    def test_live_chat(self):
        # Student sends a message to the teacher
        student_to_teacher_chat = LiveChat.objects.create(
            sender=self.student,
            receiver=self.teacher,
            message='Hello teacher!',
            is_read=False,
            image=None
        )

        # Assert the message from student to teacher
        self.assertEqual(student_to_teacher_chat.message, 'Hello teacher!')
        self.assertEqual(student_to_teacher_chat.sender, self.student)
        self.assertEqual(student_to_teacher_chat.receiver, self.teacher)
        self.assertFalse(student_to_teacher_chat.is_read)
        self.assertIsNone(student_to_teacher_chat.image)

        # Teacher sends a message to the student
        teacher_to_student_chat = LiveChat.objects.create(
            sender=self.teacher,
            receiver=self.student,
            message='Hello student!',
            is_read=False,
            image=None
        )

        # Assert the message from teacher to student
        self.assertEqual(teacher_to_student_chat.message, 'Hello student!')
        self.assertEqual(teacher_to_student_chat.sender, self.teacher)
        self.assertEqual(teacher_to_student_chat.receiver, self.student)
        self.assertFalse(teacher_to_student_chat.is_read)
        self.assertIsNone(teacher_to_student_chat.image)


    # Test blocking functionality in Enrollment
    def test_block_student_enrollment(self):
        self.enrollment.blocked = True
        self.enrollment.save()
        self.assertTrue(self.enrollment.blocked)

    # Test marking feedback as read
    def test_feedback_read(self):
        self.feedback.is_read = True
        self.feedback.save()
        self.assertTrue(self.feedback.is_read)

    # Test marking notification as read
    def test_notification_read(self):
        self.notification.is_read = True
        self.notification.save()
        self.assertTrue(self.notification.is_read)

    # Test sending an image in LiveChat
    def test_send_image_chat(self):
        image_data = 'base64encodedstring'
        self.live_chat.image = image_data
        self.live_chat.save()
        self.assertEqual(self.live_chat.image, image_data)
