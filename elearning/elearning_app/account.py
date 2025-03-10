from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Course, Material, Feedback

# User registration form
class UserRegisterAccount(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True)
    type_of_user = forms.ChoiceField(choices=Profile.USER_SELECTION, required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2', 'type_of_user'] 

    def save(self, commit=True):
        user_acc = super().save(commit=False)
        user_acc.first_name = self.cleaned_data['first_name']
        user_acc.last_name = self.cleaned_data['last_name']
        user_acc.email = self.cleaned_data['email']
        if commit:
            user_acc.save()
            # Create Profile for the user
            profile = Profile(user=user_acc, type_of_user=self.cleaned_data['type_of_user'])
            profile.save()

        return user_acc

# Course creation form
class CreateCourse(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['course_name', 'course_description']

# Material creation form
class MaterialModule(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['subject_title', 'file']

# Feedback form
class TeacherFeedback(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['feedback_title', 'description']
        widgets = {
            'feedback_title': forms.TextInput(attrs={'placeholder': 'Enter the feedback title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Enter your feedback'}),
        }

