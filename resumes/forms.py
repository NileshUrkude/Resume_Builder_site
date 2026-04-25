from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import Resume, Education, Experience, Project

# form for main resume data
class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        # fields in form
        fields = ['title', 'full_name', 'email', 'phone', 'summary']

# formset for multiple education entries,this allows user to add many education rows
EducationFormSet = modelformset_factory(
    Education,
    fields=('degree', 'college', 'year'),
    extra=1,            # show one empty form by default
)

ExperienceFormSet = modelformset_factory(
    Experience,
    fields=('job_title', 'company', 'duration', 'description'),
    extra=1,
)

ProjectFormSet = modelformset_factory(
    Project,
    fields=('name', 'description', 'tech_stack'),
    extra=1,
)

# simple signup form
class SimpleSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    # check both passwords match
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data