from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.forms import BaseModelFormSet, modelformset_factory

from .models import (
    Achievement,
    Certificate,
    Education,
    Experience,
    Hobby,
    Language,
    Project,
    Resume,
    Skill,
)

INPUT_CLASS = (
    'mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 '
    'text-sm text-slate-900 shadow-sm focus:border-indigo-500 focus:outline-none '
    'focus:ring-2 focus:ring-indigo-500/20 '
    'dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100'
)
TEXTAREA_CLASS = INPUT_CLASS + ' min-h-[88px]'
DATE_CLASS = INPUT_CLASS + ' max-w-xs'


class TailwindModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('class', TEXTAREA_CLASS)
            elif isinstance(widget, forms.DateInput):
                widget.attrs.setdefault('class', DATE_CLASS)
                widget.input_type = 'date'
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault('class', 'h-4 w-4 rounded border-slate-300 text-indigo-600')
            elif isinstance(widget, (forms.FileInput, forms.Select)):
                widget.attrs.setdefault('class', INPUT_CLASS)
            else:
                widget.attrs.setdefault('class', INPUT_CLASS)


class OptionalRowFormSet(BaseModelFormSet):
    """Ignore completely empty extra rows so save does not fail validation."""

    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            if not self._row_has_data(form):
                form.cleaned_data = {'DELETE': True}

    def _row_has_data(self, form):
        for field, value in form.cleaned_data.items():
            if field in ('DELETE', 'id', 'order'):
                continue
            if value not in (None, '', False):
                return True
        return False


class ResumeForm(TailwindModelForm):
    share_password_input = forms.CharField(
        required=False,
        label='Share password',
        help_text='Optional. Leave blank to keep current or remove protection.',
        widget=forms.PasswordInput(attrs={'class': INPUT_CLASS, 'autocomplete': 'new-password', 'placeholder': 'Set or change password'}),
    )

    class Meta:
        model = Resume
        fields = [
            'resume_name', 'full_name', 'title', 'email', 'phone', 'summary', 'photo',
            'github', 'linkedin', 'preferred_template', 'accent_color', 'font_family', 'is_public',
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3, 'id': 'id_summary', 'placeholder': 'Brief professional summary'}),
            'accent_color': forms.TextInput(attrs={'type': 'color'}),
            'photo': forms.ClearableFileInput(attrs={'class': INPUT_CLASS}),
            'is_public': forms.CheckboxInput(),
            'preferred_template': forms.Select(attrs={'class': INPUT_CLASS}),
            'github': forms.URLInput(attrs={'placeholder': 'https://github.com/username'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_template'].choices = [
            ('t1', 'Executive Navy — gold & navy classic'),
            ('t1s', 'Ocean Teal — mint minimal stack'),
            ('t2s', 'Plum Sidebar — purple panel layout'),
            ('t3s', 'Crimson Pro — red timeline columns'),
            ('t4s', 'Slate & Sky — dark header modern'),
        ]
        if self.instance and self.instance.pk and self.instance.share_password:
            self.fields['share_password_input'].help_text = 'Password is set. Enter a new one to change, or leave blank to keep it.'

    def clean_github(self):
        val = self.cleaned_data.get('github') or ''
        return val.strip()

    def clean_linkedin(self):
        val = self.cleaned_data.get('linkedin') or ''
        return val.strip()


class EducationForm(TailwindModelForm):
    class Meta:
        model = Education
        fields = ('degree', 'college', 'location', 'start_date', 'end_date', 'duration')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ('degree', 'college', 'location', 'duration'):
            self.fields[f].required = False


class ExperienceForm(TailwindModelForm):
    class Meta:
        model = Experience
        fields = ('job_title', 'company', 'start_date', 'end_date', 'duration', 'description')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False


class ProjectForm(TailwindModelForm):
    class Meta:
        model = Project
        fields = ('name', 'description', 'tech_stack')
        widgets = {'description': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields:
            self.fields[f].required = False


def _optional_formset(model, form, fields, prefix, extra=1):
    return modelformset_factory(
        model,
        fields=fields,
        form=form,
        formset=OptionalRowFormSet,
        extra=extra,
        can_delete=True,
    )


EducationFormSet = _optional_formset(Education, EducationForm, ('degree', 'college', 'location', 'start_date', 'end_date', 'duration'), 'edu')
ExperienceFormSet = _optional_formset(Experience, ExperienceForm, ('job_title', 'company', 'start_date', 'end_date', 'duration', 'description'), 'exp')
ProjectFormSet = _optional_formset(Project, ProjectForm, ('name', 'description', 'tech_stack'), 'proj')

def _make_optional_form(model, fields):
    meta = type('Meta', (), {'model': model, 'fields': fields})

    class OptionalForm(TailwindModelForm):
        class Meta(meta):
            pass

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for f in self.fields:
                self.fields[f].required = False

    return OptionalForm


SkillFormSet = modelformset_factory(
    Skill, form=_make_optional_form(Skill, ('name', 'level')),
    formset=OptionalRowFormSet, extra=2, can_delete=True,
)
CertificateFormSet = modelformset_factory(
    Certificate, form=_make_optional_form(Certificate, ('name',)),
    formset=OptionalRowFormSet, extra=1, can_delete=True,
)
AchievementFormSet = modelformset_factory(
    Achievement, form=_make_optional_form(Achievement, ('title',)),
    formset=OptionalRowFormSet, extra=1, can_delete=True,
)
LanguageFormSet = modelformset_factory(
    Language, form=_make_optional_form(Language, ('name', 'proficiency')),
    formset=OptionalRowFormSet, extra=1, can_delete=True,
)
HobbyFormSet = modelformset_factory(
    Hobby, form=_make_optional_form(Hobby, ('name',)),
    formset=OptionalRowFormSet, extra=1, can_delete=True,
)


class SimpleSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS}))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match')
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'email': forms.EmailInput(attrs={'class': INPUT_CLASS}),
            'first_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'last_name': forms.TextInput(attrs={'class': INPUT_CLASS}),
        }



class SharePasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': INPUT_CLASS}))


class TailwindPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = INPUT_CLASS
