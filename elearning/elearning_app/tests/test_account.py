from django.test import TestCase
from django.contrib.auth.models import User
from elearning_app.account import UserRegisterAccount, CreateCourse, MaterialModule, TeacherFeedback
from elearning_app.models import Profile, Course, Material, Feedback
from django.core.files.uploadedfile import SimpleUploadedFile


class UserRegisterAccountTest(TestCase):

    def test_registration_form_valid(self):
        form_data = {
            'first_name': 'admin',
            'last_name': 'user',
            'username': 'testuseradmin',
            'email': 'testuseradmin@example.com', 
            'password1': 'useraccount123',
            'password2': 'useraccount123',
            'type_of_user': 'teacher',
        }
        form = UserRegisterAccount(data=form_data)
        self.assertTrue(form.is_valid())

        user = form.save()
        profile = Profile.objects.get(user=user)

        self.assertEqual(user.first_name, 'admin')
        self.assertEqual(user.last_name, 'user')
        self.assertEqual(user.username, 'testuseradmin')
        self.assertEqual(user.email, 'testuseradmin@example.com')
        self.assertEqual(profile.type_of_user, 'teacher')

    def test_registration_form_notvalid(self):
        form_data = {
            'first_name': 'admin',
            'last_name': 'user',
            'username': 'testuseradmin',
            'email': 'invalid-email',  # Invalid email format
            'password1': 'useraccount123',
            'password2': 'useraccount123',
            'type_of_user': 'teacher',
        }
        form = UserRegisterAccount(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class CreateCourseFormTest(TestCase):

    def test_create_course_successful(self):
        form_data = {
            'course_name': 'Advance Web Development',
            'course_description': 'Understanding AWD.',
        }
        form = CreateCourse(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_course_unsuccessful(self):
        form_data = {
            'course_name': 'Advance Web Development',  # Providing a valid course name
            'course_description': '',  # Empty field
        }
        form = CreateCourse(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('course_description', form.errors)  # Adjusted to check for 'course_description'


class MaterialModuleFormTest(TestCase):

    def test_valid_material(self):
        course = Course.objects.create(
            teacher=User.objects.create_user(username='teacher', password='pass'),
            course_name='cm3035 AWD',
            course_description='Python migration.'
        )
        test_file = SimpleUploadedFile("file.txt", b"file_content")
        form_data = {
            'subject_title': 'lesson 1',
            'file': test_file,
        }
        form = MaterialModule(data=form_data, files={'file': test_file})
        self.assertTrue(form.is_valid())

        material = form.save(commit=False)
        material.course = course
        material.save()

        self.assertEqual(material.subject_title, 'lesson 1')

    def test_invalid_material(self):
        form_data = {
            'subject_title': '',  # Missing title
            'file': None,  # Missing file
        }
        form = MaterialModule(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject_title', form.errors)
        self.assertIn('file', form.errors)


class TeacherFeedbackFormTest(TestCase):

    def test_valid_feedback(self):
        form_data = {
            'feedback_title': 'AWD Feedback on the overall course',
            'description': 'The lesson learnt is very informative.',
        }
        form = TeacherFeedback(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_feedback(self):
        form_data = {
            'feedback_title': '',  # Missing title
            'description': '',  # Missing description
        }
        form = TeacherFeedback(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('feedback_title', form.errors)
        self.assertIn('description', form.errors)
