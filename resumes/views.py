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
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Resume, Education, Experience, Project, Skill
from .forms import ResumeForm, EducationFormSet, ExperienceFormSet, ProjectFormSet


@login_required
def create_resume(request):

    # get existing resume (one per user)
    resume = Resume.objects.filter(user=request.user).first()

    if request.method == 'POST':

        # main form
        resume_form = ResumeForm(request.POST, instance=resume)

        # formsets with PREFIX (very important)
        edu_formset = EducationFormSet(request.POST or None, queryset=Education.objects.none(), prefix='edu')
        exp_formset = ExperienceFormSet(request.POST or None, queryset=Experience.objects.none(), prefix='exp')
        proj_formset = ProjectFormSet(request.POST or None, queryset=Project.objects.none(), prefix='proj')
        # validation
        if (
            resume_form.is_valid() and
            edu_formset.is_valid() and
            exp_formset.is_valid() and
            proj_formset.is_valid()
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

            # save skills (comma separated)
            skills = request.POST.get('skills', '').strip()
            if skills:
                skill_list = skills.split(',')

                for s in skill_list:
                    s = s.strip()
                    if s:
                        Skill.objects.create(resume=resume, name=s)

            # get where user came from
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

    return render(request, 'resumes/form.html', {
        'form': resume_form,
        'edu': edu_formset,
        'exp': exp_formset,
        'proj': proj_formset
    })


@login_required
def view_resume(request, template):

    resume = Resume.objects.filter(user=request.user).first()

    if not resume:
        return redirect('dashboard')

    template_map = {
        't1': 'resumes/t1.html',
        't2': 'resumes/t2.html',
        't3': 'resumes/t3.html'
    }

    template_name = template_map.get(template, 'resumes/t1.html')

    return render(request, 'resumes/view_wrapper.html', {
        'resume': resume,
        'template_name': template_name,
        'selected_template': template
    })


# download resume as PDF
@login_required
def download_pdf(request, template):

    resume = Resume.objects.filter(user=request.user).first()

    template_map = {
        't1': 'resumes/t1.html',
        't2': 'resumes/t2.html',
        't3': 'resumes/t3.html'
    }

    template_file = get_template(template_map.get(template, 'resumes/t1.html'))
    html = template_file.render({'resume': resume})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="resume.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response

