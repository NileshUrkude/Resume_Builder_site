from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import SimpleSignupForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Resume, Education ,Experience, Project, Skill
from .forms import ResumeForm, EducationFormSet, ExperienceFormSet, ProjectFormSet


# home page
def home(request):
    return render(request, 'resumes/home.html')


# signup page
def signup(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SimpleSignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # set password properly (important)
            user.set_password(form.cleaned_data['password'])
            user.save()

            login(request, user)
            return redirect('dashboard')
    else:
        form = SimpleSignupForm()

    return render(request, 'registration/signup.html', {'form': form})

# logout
def user_logout(request):
    logout(request)
    return redirect('home')


# dashboard
@login_required
def dashboard(request):
    resume = Resume.objects.filter(user=request.user).first()
    return render(request, 'resumes/dashboard.html', {'resume': resume})


# create + update resume (same view)
@login_required
def create_resume(request):

    # check if resume already exists
    resume_instance = Resume.objects.filter(user=request.user).first()

    if request.method == 'POST':
        resume_form = ResumeForm(request.POST, instance=resume_instance)

        edu_formset = EducationFormSet(request.POST, prefix='edu')
        exp_formset = ExperienceFormSet(request.POST, prefix='exp')
        proj_formset = ProjectFormSet(request.POST, prefix='proj')

        if (
            resume_form.is_valid() and
            edu_formset.is_valid() and
            exp_formset.is_valid() and
            proj_formset.is_valid()
        ):

            resume = resume_form.save(commit=False)
            resume.user = request.user
            resume.save()

            # clear old data (for update case)
            resume.educations.all().delete()
            resume.experiences.all().delete()
            resume.projects.all().delete()
            resume.skills.all().delete()

            # save education
            for form in edu_formset:
                if form.cleaned_data:
                    obj = form.save(commit=False)
                    obj.resume = resume
                    obj.save()

            # save experience
            for form in exp_formset:
                if form.cleaned_data:
                    obj = form.save(commit=False)
                    obj.resume = resume
                    obj.save()

            # save projects
            for form in proj_formset:
                if form.cleaned_data:
                    obj = form.save(commit=False)
                    obj.resume = resume
                    obj.save()

            # save skills
            skill_data = request.POST.get('skills')
            if skill_data:
                for s in skill_data.split(','):
                    Skill.objects.create(resume=resume, name=s.strip())

            return redirect('dashboard')

    else:
        resume_form = ResumeForm(instance=resume_instance)

        edu_formset = EducationFormSet(prefix='edu')
        exp_formset = ExperienceFormSet(prefix='exp')
        proj_formset = ProjectFormSet(prefix='proj')

    return render(request, 'resumes/form.html', {
        'form': resume_form,
        'edu_formset': edu_formset,
        'exp_formset': exp_formset,
        'proj_formset': proj_formset,
    })

@login_required
def view_resume(request):
    resume = Resume.objects.filter(user=request.user).first()
    return render(request, 'resumes/resume.html', {'resume': resume})


# download resume as PDF
@login_required
def download_pdf(request):
    resume = Resume.objects.filter(user=request.user).first()

    template = get_template('resumes/resume.html')
    html = template.render({'resume': resume})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response

