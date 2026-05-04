from urllib import request
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from urllib3 import request
from .forms import AchievementFormSet, CertificateFormSet, SimpleSignupForm
from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
# from weasyprint import HTML
from xhtml2pdf import pisa
from .models import Achievement, Achievement, Certificate, Resume, Education ,Experience, Project, Skill
from .forms import ResumeForm, EducationFormSet, ExperienceFormSet, ProjectFormSet
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Resume, Education, Experience, Project, Skill
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

    # get existing resume (one per user)
    resume = Resume.objects.filter(user=request.user).first()
    skills = ""   

    if request.method == 'POST':

        # main form
        resume_form = ResumeForm(request.POST, instance=resume)

        # formsets with PREFIX (very important)
        edu_formset = EducationFormSet(request.POST or None, queryset=Education.objects.none(), prefix='edu')
        exp_formset = ExperienceFormSet(request.POST or None, queryset=Experience.objects.none(), prefix='exp')
        proj_formset = ProjectFormSet(request.POST or None, queryset=Project.objects.none(), prefix='proj')
        cert_formset = CertificateFormSet(request.POST or None, queryset=Certificate.objects.none(), prefix='cert')
        ach_formset = AchievementFormSet(request.POST or None, queryset=Achievement.objects.none(), prefix='ach')
        
        # validation
        if (
            resume_form.is_valid() and
            edu_formset.is_valid() and
            exp_formset.is_valid() and
            proj_formset.is_valid() and
            cert_formset.is_valid() and
            ach_formset.is_valid()
        ):

            # save resume
            resume = resume_form.save(commit=False)
            resume.user = request.user
            resume.save()

            # delete old data (simple and safe approach)
            resume.educations.all().delete()
            resume.experiences.all().delete()
            resume.projects.all().delete()
            resume.skills.all().delete()
            resume.certificates.all().delete()
            resume.achievements.all().delete()

            # save education
            for form in edu_formset:
                if form.cleaned_data:
                    edu = form.save(commit=False)
                    edu.resume = resume
                    edu.save()

            # save experience
            for form in exp_formset:
                if form.cleaned_data:
                    exp = form.save(commit=False)
                    exp.resume = resume
                    exp.save()

            # save projects
            for form in proj_formset:
                if form.cleaned_data:
                    proj = form.save(commit=False)
                    proj.resume = resume
                    proj.save()


            for form in cert_formset:
                if form.cleaned_data:
                    cert = form.save(commit=False)
                    cert.resume = resume
                    cert.save()

            for form in ach_formset:
                if form.cleaned_data:
                    ach = form.save(commit=False)
                    ach.resume = resume
                    ach.save()

            # save skills (comma separated)
            skills = request.POST.get('skills', '')

            for s in skills.split(','):
                if s.strip():
                    Skill.objects.create(resume=resume, name=s.strip())

            # get where user came from
            next_page = request.GET.get('next') or request.POST.get('next')

            if next_page in ['t1', 't2', 't3']:
                return redirect('view_resume', template=next_page)

            elif next_page == 'dashboard':
                return redirect('dashboard')

            return redirect('dashboard')  # default
        
        else:
            # keep entered skills on error
            skills = request.POST.get('skills', '')

            next_page = request.GET.get('next') or request.POST.get('next')

            if next_page in ['t1', 't2', 't3']:
                return redirect('view_resume', template=next_page)

            elif next_page == 'dashboard':
                return redirect('dashboard')

            return redirect('dashboard')  # default

    else:
        # GET request

        resume_form = ResumeForm(instance=resume)

        # IMPORTANT: prefix must match form.html
        edu_formset = EducationFormSet(prefix='edu')
        exp_formset = ExperienceFormSet(prefix='exp')
        proj_formset = ProjectFormSet(prefix='proj')
        cert_formset = CertificateFormSet(prefix='cert')
        ach_formset = AchievementFormSet(prefix='ach')

        if resume:
            skills = ", ".join([s.name for s in resume.skills.all()])

    return render(request, 'resumes/form.html', {
        'skills': skills,
        'form': resume_form,
        'edu': edu_formset,
        'exp': exp_formset,
        'proj': proj_formset,
        'cert': cert_formset,
        'ach': ach_formset
    })


@login_required
def view_resume(request, template):

    resume = Resume.objects.filter(user=request.user).first()

    template_map = {
        't1': 'resumes/t1.html',
        't2': 'resumes/t2.html',
        't3': 'resumes/t3.html',
        't4': 'resumes/t4.html',
        't5': 'resumes/t5.html',
        't6': 'resumes/t6.html',


    }

    return render(request, 'resumes/view_wrapper.html', {
        'resume': resume,
        'template_name': template_map.get(template),
        'selected_template': template
    })


# download resume as PDF
@login_required
def download_pdf(request, template):

    resume = Resume.objects.filter(user=request.user).first()

    template_map = {
        't1': 'resumes/t1.html',
        't2': 'resumes/t2.html',
        't3': 'resumes/t3.html',
        't4': 'resumes/t4.html',
        't5': 'resumes/t5.html',
        't6': 'resumes/t6.html',
    }

    template_file = get_template(template_map.get(template, 'resumes/t1.html'))
    html = template_file.render({'resume': resume})
    # html_string = render_to_string(template_map[template], {'resume': resume})

    # html = HTML(string=html_string)
    # result = html.write_pdf()


    response = HttpResponse( content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response

