import json

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .forms import (
    AchievementFormSet,
    CertificateFormSet,
    EducationFormSet,
    ExperienceFormSet,
    HobbyFormSet,
    JobDescriptionForm,
    LanguageFormSet,
    ProfileForm,
    ProjectFormSet,
    ResumeForm,
    SharePasswordForm,
    SimpleSignupForm,
    SkillFormSet,
    TailwindPasswordChangeForm,
)
from .models import (
    Achievement,
    Certificate,
    Education,
    Experience,
    Hobby,
    Language,
    Project,
    Resume,
    ResumeEvent,
    Skill,
)
from .utils import (
    TEMPLATE_MAP,
    VALID_TEMPLATES,
    check_share_password,
    compute_ats_score,
    duplicate_resume,
    export_docx,
    generate_summary,
    get_user_resume,
    match_job_description,
    pdf_response,
    qr_png_response,
    render_resume_html,
    save_ordered_formset,
    set_active_resume,
    set_share_password,
    track_event,
)


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'resumes/home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = SimpleSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = SimpleSignupForm()
    return render(request, 'registration/signup.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')


def _build_all_formsets(request, resume=None):
    def qs(model, rel):
        return getattr(resume, rel).all() if resume else model.objects.none()

    prefixes = {
        'edu': (EducationFormSet, Education, 'educations'),
        'exp': (ExperienceFormSet, Experience, 'experiences'),
        'proj': (ProjectFormSet, Project, 'projects'),
        'skill': (SkillFormSet, Skill, 'skills'),
        'cert': (CertificateFormSet, Certificate, 'certificates'),
        'ach': (AchievementFormSet, Achievement, 'achievements'),
        'lang': (LanguageFormSet, Language, 'languages'),
        'hobby': (HobbyFormSet, Hobby, 'hobbies'),
    }
    result = {}
    for prefix, (FormSet, model, rel) in prefixes.items():
        if request.method == 'POST':
            result[prefix] = FormSet(request.POST, queryset=model.objects.none(), prefix=prefix)
        else:
            result[prefix] = FormSet(queryset=qs(model, rel), prefix=prefix)
    return result


def _save_all_formsets(resume, formsets):
    save_ordered_formset(formsets['edu'], resume, 'educations', 'edu')
    save_ordered_formset(formsets['exp'], resume, 'experiences', 'exp')
    save_ordered_formset(formsets['proj'], resume, 'projects', 'proj')
    save_ordered_formset(formsets['skill'], resume, 'skills', 'skill')
    save_ordered_formset(formsets['cert'], resume, 'certificates', 'cert')
    save_ordered_formset(formsets['ach'], resume, 'achievements', 'ach')
    save_ordered_formset(formsets['lang'], resume, 'languages', 'lang')
    save_ordered_formset(formsets['hobby'], resume, 'hobbies', 'hobby')


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    resume = get_user_resume(request)
    stats = {}
    if resume:
        stats = {
            'views': resume.events.filter(event_type='view').count(),
            'pdfs': resume.events.filter(event_type='pdf').count(),
            'docx': resume.events.filter(event_type='docx').count(),
            'shares': resume.events.filter(event_type='share').count(),
        }
    preview_tpl = TEMPLATE_MAP.get(resume.preferred_template, TEMPLATE_MAP['t1']) if resume else None
    share_url = ''
    if resume and resume.is_public:
        share_url = request.build_absolute_uri(reverse('public_resume', kwargs={'slug': resume.slug}))
    return render(request, 'resumes/dashboard.html', {
        'resume': resume,
        'resumes': resumes,
        'stats': stats,
        'preview_template': preview_tpl,
        'accent_color': resume.accent_color if resume else '#4f46e5',
        'font_family': resume.font_family if resume else 'Arial',
        'share_url': share_url,
    })


@login_required
def template_gallery(request):
    resume = get_user_resume(request)
    templates = [
        ('t1', 'Classic', 'Elegant serif · photo · skill pills', '#4f46e5'),
        ('t2', 'Modern', 'Gradient bar · labeled sections', '#2563eb'),
        ('t3', 'Minimal', 'Centered · light & spacious', '#0f172a'),
        ('t4', 'Sidebar', 'Dark sidebar · skills panel', '#4f46e5'),
        ('t5', 'Timeline', 'Career timeline · dots', '#0d9488'),
        ('t6', 'Compact', 'Two-column · one page', '#4f46e5'),
        ('t7', 'Academic', 'Formal · education first', '#1e3a5f'),
        ('t8', 'Creative', 'Gradient hero · cards', '#e11d48'),
    ]
    return render(request, 'resumes/template_gallery.html', {'resume': resume, 'templates': templates})


@login_required
def select_resume(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    set_active_resume(request, resume)
    messages.success(request, f'Active resume: {resume.resume_name}')
    return redirect(request.GET.get('next', 'dashboard'))


@login_required
def new_resume(request):
    if request.method == 'POST':
        resume = Resume.objects.create(
            user=request.user,
            resume_name=request.POST.get('resume_name', 'New Resume'),
            title='Your Title',
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email or 'email@example.com',
            phone='',
            summary='',
        )
        set_active_resume(request, resume)
        return redirect('create_resume', resume_id=resume.pk)
    return render(request, 'resumes/new_resume.html')


@login_required
def duplicate_resume_view(request, resume_id):
    source = get_object_or_404(Resume, pk=resume_id, user=request.user)
    clone = duplicate_resume(source)
    set_active_resume(request, clone)
    messages.success(request, f'Duplicated as "{clone.resume_name}"')
    return redirect('dashboard')


@login_required
def delete_resume(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    if Resume.objects.filter(user=request.user).count() <= 1:
        messages.error(request, 'You must keep at least one resume.')
        return redirect('dashboard')
    resume.delete()
    request.session.pop('active_resume_id', None)
    messages.success(request, 'Resume deleted.')
    return redirect('dashboard')


@login_required
def create_resume(request, resume_id=None):
    if resume_id is None and request.method == 'GET':
        active = get_user_resume(request)
        if active:
            return redirect('edit_resume', resume_id=active.pk)

    resume = None
    if resume_id:
        resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    elif request.method == 'POST' and request.POST.get('resume_id'):
        resume = get_object_or_404(Resume, pk=request.POST.get('resume_id'), user=request.user)

    formsets = _build_all_formsets(request, resume)

    if request.method == 'POST':
        resume_form = ResumeForm(request.POST, request.FILES, instance=resume)
        all_valid = resume_form.is_valid()
        for fs in formsets.values():
            all_valid = all_valid and fs.is_valid()

        if all_valid:
            resume = resume_form.save(commit=False)
            resume.user = request.user
            plain_pw = resume_form.cleaned_data.get('share_password_plain', '')
            set_share_password(resume, plain_pw)
            resume.save()
            if resume.photo and not resume_form.cleaned_data.get('photo'):
                pass
            _save_all_formsets(resume, formsets)
            set_active_resume(request, resume)
            messages.success(request, 'Resume saved successfully.')
            next_page = request.GET.get('next') or request.POST.get('next')
            if next_page in VALID_TEMPLATES:
                return redirect('view_resume', resume_id=resume.pk, template=next_page)
            return redirect('edit_resume', resume_id=resume.pk)
        messages.error(request, 'Please fix the errors below.')
        resume_form = ResumeForm(request.POST, request.FILES, instance=resume)
    else:
        resume_form = ResumeForm(instance=resume)

    preview_template = request.GET.get('preview', resume.preferred_template if resume else 't1')
    if preview_template not in VALID_TEMPLATES:
        preview_template = 't1'

    return render(request, 'resumes/form.html', {
        'form': resume_form,
        'resume': resume,
        'edu': formsets['edu'],
        'exp': formsets['exp'],
        'proj': formsets['proj'],
        'skill': formsets['skill'],
        'cert': formsets['cert'],
        'ach': formsets['ach'],
        'lang': formsets['lang'],
        'hobby': formsets['hobby'],
        'preview_template': preview_template,
        'template_choices': Resume._meta.get_field('preferred_template').choices,
    })


@login_required
@require_POST
def autosave_resume(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    data = json.loads(request.body.decode() or '{}')
    for field in ('resume_name', 'title', 'full_name', 'email', 'phone', 'summary', 'github', 'linkedin', 'preferred_template', 'accent_color', 'font_family'):
        if field in data:
            setattr(resume, field, data[field])
    resume.save()
    return JsonResponse({'ok': True, 'updated_at': resume.updated_at.isoformat()})


@login_required
@require_GET
def preview_fragment(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    if template not in VALID_TEMPLATES:
        template = 't1'
    html = render_resume_html(resume, template)
    return HttpResponse(html)


@login_required
def view_resume(request, resume_id, template):
    if template not in VALID_TEMPLATES:
        return redirect('dashboard')
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    set_active_resume(request, resume)
    track_event(resume, 'view', template)
    return render(request, 'resumes/view_wrapper.html', {
        'resume': resume,
        'template_name': TEMPLATE_MAP[template],
        'selected_template': template,
        'share_url': request.build_absolute_uri(reverse('public_resume', kwargs={'slug': resume.slug})),
    })


@login_required
def download_pdf(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    template = template if template in VALID_TEMPLATES else resume.preferred_template
    track_event(resume, 'pdf', template)
    return pdf_response(resume, template, f'{resume.resume_name}_{template}.pdf')


@login_required
def download_docx(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    track_event(resume, 'docx', resume.preferred_template)
    return export_docx(resume)


@login_required
def download_cover_letter(request, resume_id):
    from xhtml2pdf import pisa

    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    html = render_to_string('resumes/cover_letter.html', {'resume': resume, 'for_pdf': True})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cover_letter_{resume.pk}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
def qr_code(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    url = request.build_absolute_uri(reverse('public_resume', kwargs={'slug': resume.slug}))
    return qr_png_response(url)


def public_resume(request, slug):
    resume = get_object_or_404(Resume, slug=slug)
    if not resume.is_share_valid():
        return render(request, 'resumes/share_unavailable.html', status=404)

    if resume.share_password:
        if request.method == 'POST':
            form = SharePasswordForm(request.POST)
            if form.is_valid() and check_share_password(resume, form.cleaned_data['password']):
                request.session[f'share_ok_{resume.slug}'] = True
                return redirect('public_resume', slug=slug)
        elif not request.session.get(f'share_ok_{resume.slug}'):
            return render(request, 'resumes/share_password.html', {'resume': resume, 'form': SharePasswordForm()})
    else:
        request.session[f'share_ok_{resume.slug}'] = True

    template = request.GET.get('t', resume.preferred_template)
    if template not in VALID_TEMPLATES:
        template = resume.preferred_template
    track_event(resume, 'share', template)
    return render(request, 'resumes/public_view.html', {
        'resume': resume,
        'template_name': TEMPLATE_MAP[template],
        'selected_template': template,
    })


@login_required
def ats_checker(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    result = compute_ats_score(resume)
    return render(request, 'resumes/ats_checker.html', {'resume': resume, 'result': result})


@login_required
def jd_matcher(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    result = None
    form = JobDescriptionForm()
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            result = match_job_description(resume, form.cleaned_data['job_description'])
    return render(request, 'resumes/jd_matcher.html', {'resume': resume, 'form': form, 'result': result})


@login_required
@require_POST
def ai_summary(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    summary = generate_summary(resume)
    return JsonResponse({'summary': summary})


@login_required
def profile(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = TailwindPasswordChangeForm(user)
    resume = get_user_resume(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'profile' and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
        if action == 'password' and password_form.is_valid():
            password_form.save()
            update_session_auth_hash(request, password_form.user)
            messages.success(request, 'Password changed.')
            return redirect('profile')
        if action == 'delete_account':
            user.delete()
            return redirect('home')
    else:
        profile_form = ProfileForm(instance=user)
        password_form = TailwindPasswordChangeForm(user)

    return render(request, 'resumes/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'resume': resume,
    })
