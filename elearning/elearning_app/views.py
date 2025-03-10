from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from .account import UserRegisterAccount, CreateCourse, MaterialModule, TeacherFeedback
from .models import Course, Material, Enrollment, Notification, User, Feedback, Profile, LiveChat
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json
from .account import UserRegisterAccount

def register_account(request):
    # Check if the request form was submitted
    if request.method == 'POST':
        account_form = UserRegisterAccount(request.POST)
        #checking if the form is valid
        if account_form.is_valid():
            # Create new account
            user = account_form.save()
            login(request, user)
            # Redirect based on the user type
            if user.profile.type_of_user == 'teacher':
                return redirect('teacher_homepage')
            else:
                return redirect('student_homepage')
        else:
            # If form is not valid, re-render the form with errors
            return render(request, 'elearning_app/register.html', {'form': account_form})
    else:
        account_form = UserRegisterAccount()
    return render(request, 'elearning_app/register.html', {'form': account_form})

# User login view
def user_login(request):
    # Check if the request login form submitted)
    if request.method == 'POST':
        account_form = AuthenticationForm(data=request.POST)
        if account_form.is_valid():
            user = account_form.get_user()
            login(request, user)
            if user.profile.type_of_user == 'teacher':
                return redirect('teacher_homepage')
            else:
                return redirect('student_homepage')
    else:
        account_form = AuthenticationForm()
    return render(request, 'elearning_app/login.html', {'form': account_form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

# -------------------------home--------------------------------

# Home view with redirection based on user type
def home(request):
    if request.user.is_authenticated:
        # based on the type of user, it will redirect to that specific page
        if request.user.profile.type_of_user == 'teacher':
            return redirect('teacher_homepage')
        elif request.user.profile.type_of_user == 'student':
            return redirect('student_homepage')
    return render(request, 'elearning_app/home.html')  # show this page if not logged in

# Teacher's home view
@login_required
def teacher_homepage(request):
    #check if the user is a teacher
    if request.user.profile.type_of_user == 'teacher':
        #get courses that this teacher is teaching
        courses = request.user.courses.all()
        notifications = request.user.notifications.filter(is_read=False) # receive unread notification
        # get feedback - teachers courses
        feedbacks = Feedback.objects.filter(course__in=courses).order_by('-date_submitted')
        return render(request, 'elearning_app/teacher_homepage.html', {
            'courses': courses, #list of courses of the teacher
            'notifications': notifications, #unread notification
            'feedbacks': feedbacks, # feedback received relating to the course
            'full_name': request.user.get_full_name(), # the full name of the teacher
        })
    else:
        return redirect('home')

# Student's home view
@login_required
def student_homepage(request):
    #check if user is a student
    if request.user.profile.type_of_user == 'student':
        # retrieve all the courses that the student is currently enrolled in
        courses = Course.objects.all()
        #course id of the subjects that the student enrolled in
        enroll_course = request.user.enrollments.values_list('course_id', flat=True)
        # get the notifications
        notifications = request.user.notifications.filter(is_read=False)
        return render(request, 'elearning_app/student_homepage.html', {
            'courses': courses,
            'enroll_course': enroll_course,
            'notifications': notifications,
            'full_name': request.user.get_full_name(),
        })
    else:
        return redirect('home')

# --------------------course related-----------------------------

# Course creation view, for teacher
@login_required
def create_course(request):
    if request.user.profile.type_of_user == 'teacher':
        if request.method == 'POST':
            account_form = CreateCourse(request.POST)
            if account_form.is_valid():
                #Save the form data but don't commit to the database yet
                course_create = account_form.save(commit=False)
                course_create.teacher = request.user
                # save it to the database
                course_create.save()
                return redirect('teacher_homepage')
        else:
            account_form = CreateCourse()
        return render(request, 'elearning_app/create_course.html', {'form': account_form})
    else:
        return redirect('home')

# Add material to a course
@login_required
def add_material(request, course_id):
    course = get_object_or_404(Course, id=course_id, teacher=request.user)
    if request.method == 'POST':
        #Create a form instance with the submitted data and files
        account_form = MaterialModule(request.POST, request.FILES)
        if account_form.is_valid():
            material = account_form.save(commit=False)
            material.course = course
            material.save()

            # Notify the enrolled students of that specific course
            student_enrolled = Enrollment.objects.filter(course=course).values_list('student', flat=True)
            notifications = [
                Notification(user_id=student_id, course=course, message=f"New material added to {course.course_name}")
                for student_id in student_enrolled
            ]
            # Notification created in bulk so the all the student enrolled will receive
            Notification.objects.bulk_create(notifications)

            return redirect('course_information', course_id=course.id)
    else:
        account_form = MaterialModule()
    return render(request, 'elearning_app/add_material.html', {'form': account_form, 'course': course})

# Delete material from a course
@login_required
def delete_material(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    # check if the user is a teacher that taught this course materials
    if request.user == material.course.teacher:
        # delete the lesson material from the database
        material.delete()
        return redirect('course_information', course_id=material.course.id)
    else:
        return redirect('home')  # Redirect if the user is not authorized

# Course View
@login_required
def course_information(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    if enrollment and enrollment.blocked:
        return redirect('teacher_homepage')  # Redirect to home or an error page if blocked
    materials = course.materials.all()
    # Mark related notifications as read
    notifications = request.user.notifications.filter(course=course, is_read=False)
    notifications.update(is_read=True)
    # check if the user is a teacher
    a_teacher = request.user.profile.type_of_user == 'teacher'
    no_students_enrolled = course.enrollments.all() if a_teacher else None #the list of the students enrolled
    feedbacks_from_student = course.feedbacks.all()  # Retrieve all feedback for the course
    unread_feedback_no = course.feedbacks.filter(is_read=False).count()  # Count unread feedback
    return render(request, 'elearning_app/course_information.html', {
        'course': course,
        'materials': materials,
        'a_teacher': a_teacher,
        'no_students_enrolled': no_students_enrolled,
        'feedbacks_from_student': feedbacks_from_student,  # Pass feedbacks to the template
        'unread_feedback_no': unread_feedback_no,  # Pass unread count to template
    })

# enroll (for students)
@login_required
def enroll_in_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # check if the user is a student
    if request.user.profile.type_of_user == 'student':
        #Obtain or make the student's enrollment entry in the designated course.
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        if created:
            # Notify the teacher that a new student has enrolled
            Notification.objects.create(
                user=course.teacher,
                course=course,
                message=f"{request.user.username} has enrolled in your course {course.course_name}."
            )
        return redirect('student_homepage')
    else:
        return redirect('home')

@login_required
def notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    # mark it as read
    notification.is_read = True
    # save and update the notification to the database
    notification.save()
    return redirect('course_information', course_id=notification.course.id)

#---------------------------------contacts------------------------

# teachers

# Full list of the students enrolled and other teachers
@login_required
def full_people(request):
    # make sure the user is a teacher
    if request.user.profile.type_of_user == 'teacher':
        students = User.objects.filter(enrollments__course__teacher=request.user).distinct()
        #get all the names of the people who are teachers
        teachers = User.objects.filter(profile__type_of_user='teacher')
        return render(request, 'elearning_app/full_people.html', {'students': students, 'teachers': teachers})
    else:
        return redirect('teacher_homepage')

# to get the info of all students that enrolled in that specific teachers course from full people page
@login_required
def student_records(request):
    if request.user.profile.type_of_user == 'teacher':
        query = request.GET.get('q')
        #If a query is given, sort the students according to the first or last name that includes the query.
        if query:
            students = User.objects.filter(
                Q(first_name__icontains=query) | Q(last_name__icontains=query),
                enrollments__course__teacher=request.user
            ).distinct()
        else:
            students = User.objects.filter(enrollments__course__teacher=request.user).distinct()

        # Check if the request is an AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('elearning_app/partials/student_list.html', {'students': students})
            return JsonResponse({'html': html})

        return render(request, 'elearning_app/student_records.html', {'students': students})
    else:
        return redirect('teacher_homepage')

# to get the info of all teachers from full people page
@login_required
def teacher_records(request):
    if request.user.profile.type_of_user == 'teacher':
        query = request.GET.get('q')
        if query:
            teachers = User.objects.filter(Q(username__icontains=query) & Q(profile__type_of_user='teacher'))
        else:
            teachers = User.objects.filter(profile__type_of_user='teacher')
        # Check if the request is an AJAX request
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            html = render_to_string('elearning_app/partials/teacher_list.html', {'teachers': teachers})
            return JsonResponse({'html': html})

        return render(request, 'elearning_app/teacher_records.html', {'teachers': teachers})
    else:
        return redirect('teacher_homepage')

# getting the details of the student for blocking
@login_required
def student_information(request, student_id):
    # Retrieve the student object, 404 if not found
    student = get_object_or_404(User, id=student_id)
    enrollments = Enrollment.objects.filter(student=student, course__teacher=request.user)
    blocked = enrollments.filter(blocked=True).exists()  # Check if any enrollment is blocked
    #Render the 'student_information.html' template with student details, enrollments, and block status
    return render(request, 'elearning_app/student_information.html', {
        'student': student,
        'enrollments': enrollments,
        'blocked': blocked,
    })

# -----------------student removal from teacher's page------------

@login_required
def student_removed(request, student_id):
    student = get_object_or_404(User, id=student_id)
    if request.user.profile.type_of_user == 'teacher':
        # Remove the student from the course
        Enrollment.objects.filter(student=student, course__teacher=request.user).delete()
    return redirect('student_records')

@login_required
def block_student(request, student_id):
    student = get_object_or_404(User, id=student_id)
    if request.user.profile.type_of_user == 'teacher':
        enrollment = Enrollment.objects.get(student=student, course__teacher=request.user)
        # Toggle the blocked status of the enrollment
        enrollment.blocked = not enrollment.blocked
        # saved into the database
        enrollment.save()
    return redirect('student_information', student_id=student.id)

#--------------------feedback--------------

# student submit feedback
@login_required
def send_feedback(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = TeacherFeedback(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.course = course
            feedback.save()
            # Notify the teacher that feedback has been submitted
            Notification.objects.create(
                user=course.teacher,
                course=course,
                message=f"A student has submitted feedback for {course.course_name}"
            )
            return redirect('student_homepage')  # Redirect after submission
    else:
        form = TeacherFeedback()
    return render(request, 'elearning_app/send_feedback.html', {'form': form, 'course': course})


# for teacher to view the feedback
@login_required
def view_feedback(request, feedback_id):
    # Get the feedback object using feedback_id
    feedback = get_object_or_404(Feedback, id=feedback_id)
    # Get the related course from the feedback object
    course = feedback.course
    # Mark the feedback as read
    if not feedback.is_read:
        feedback.is_read = True
        feedback.save()
    # Render the template with feedback and course information
    return render(request, 'elearning_app/view_feedback.html', {'feedback': feedback, 'course': course})

# -------- status------------

@login_required
def current_status(request):
    if request.method == 'POST':
        current_status = request.POST.get('status')
        profile = request.user.profile
        profile.status = current_status
        profile.save()
        # Redirect based on user role
        if profile.type_of_user == 'teacher':
            return redirect('teacher_homepage')
        else:
            return redirect('student_homepage')
    return render(request, 'elearning_app/current_status.html')

# -------- student page ----------

# teachers information in student's page
@login_required
def student_teacher_list(request):
    # Get all the courses the student is enrolled in
    enrollments = Enrollment.objects.filter(student=request.user)
    # Get the unique teachers from those courses
    teachers = {enrollment.course.teacher for enrollment in enrollments}
    return render(request, 'elearning_app/student_teacher_list.html', {'teachers': teachers})

# teacher can contact the student
@login_required
def teacher_contact_student(request):
    user = request.user
    students = []
    # Get all students enrolled in the teacher's courses
    for course in user.courses.all():
        for enrollment in course.enrollments.all():
            student = enrollment.student
            student.has_unread_messages = student.received_messages.filter(is_read=False, sender=user).exists()
            students.append(student)
    return render(request, 'elearning_app/teacher_contact_student.html', {
        'students': students,
    })

# ----------------- chat messages ----------

@login_required
def chat_messages(request, room_chat):
    user = request.user
    user2 = get_object_or_404(User, username=room_chat)
    # Mark all received messages as read
    LiveChat.objects.filter(sender=user2, receiver=user, is_read=False).update(is_read=True)
    messages = LiveChat.objects.filter(
        Q(sender=user) & Q(receiver=user2) |
        Q(sender=user2) & Q(receiver=user)
    ).order_by('timestamp')
    return render(request, 'elearning_app/chat_messages.html', {
        'room_chat': room_chat,
        'messages': messages,
    })

@csrf_exempt
@login_required
def save_message(request):
    if request.method == 'POST':
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        receiver = get_object_or_404(User, username=data['receiver'])
        message = data.get('message', '')
        # Extract the message and image from the request data
        image = data.get('image', None)
        # Check if either a message or an image is provided
        if message or image:
            LiveChat.objects.create(
                sender=request.user,
                receiver=receiver,
                message=message,
                image=image,
            )
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'no content'}, status=400)
    return JsonResponse({'status': 'fail'}, status=400)

