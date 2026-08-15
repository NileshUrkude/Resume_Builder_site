from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .forms import (
    AchievementFormSet,
    CertificateFormSet,
    EducationFormSet,
    ExperienceFormSet,
    HobbyFormSet,
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
    Skill,
)
from .utils import (
    TEMPLATE_LABELS,
    TEMPLATE_MAP,
    TEMPLATE_THEMES,
    _resume_context,
    check_share_password,
    get_sample_resume,
    get_user_resume,
    normalize_template,
    pdf_response,
    render_resume_html,
    save_ordered_formset,
    set_active_resume,
    set_share_password,
)


class RelatedList:
    """Minimal related-manager stand-in for draft preview templates."""

    def __init__(self, items):
        self._items = list(items)

    def all(self):
        return self._items


class DraftResume:
    """In-memory resume that mirrors attribute access used by resume templates."""

    def __init__(self, base, fields, relations):
        self.pk = base.pk
        self.user = base.user
        self.slug = base.slug
        self.photo = base.photo
        self.share_password = base.share_password
        self.is_public = base.is_public
        defaults = {
            'resume_name': base.resume_name,
            'full_name': base.full_name,
            'title': base.title,
            'email': base.email,
            'phone': base.phone,
            'summary': base.summary or '',
            'github': base.github or '',
            'linkedin': base.linkedin or '',
            'preferred_template': base.preferred_template,
            'font_family': base.font_family or 'Arial',
        }
        defaults.update(fields or {})
        for key, value in defaults.items():
            setattr(self, key, value)
        for rel_name, items in (relations or {}).items():
            setattr(self, rel_name, RelatedList(items))

    def duration_display(self, start, end):
        return Resume.duration_display(self, start, end)


_FORMSET_MODELS = {
    'edu': (Education, 'educations'),
    'exp': (Experience, 'experiences'),
    'proj': (Project, 'projects'),
    'skill': (Skill, 'skills'),
    'cert': (Certificate, 'certificates'),
    'ach': (Achievement, 'achievements'),
    'lang': (Language, 'languages'),
    'hobby': (Hobby, 'hobbies'),
}

_RESUME_DRAFT_FIELDS = (
    'resume_name', 'full_name', 'title', 'email', 'phone', 'summary',
    'github', 'linkedin', 'preferred_template', 'font_family', 'is_public',
)


def _row_has_data(cleaned):
    for field, value in cleaned.items():
        if field in ('DELETE', 'id', 'order'):
            continue
        if value not in (None, '', False):
            return True
    return False


def _draft_field_value(form, resume, name):
    cleaned = getattr(form, 'cleaned_data', None) or {}
    if name in cleaned:
        return cleaned[name]
    if form.is_bound:
        raw = form.data.get(name)
        if raw is not None:
            if name == 'is_public':
                return name in form.data
            return raw
    return getattr(resume, name)


def _objects_from_formset(formset, model, resume):
    formset.is_valid()
    items = []
    for form in formset.forms:
        cleaned = getattr(form, 'cleaned_data', None) or {}
        if not cleaned or cleaned.get('DELETE') or not _row_has_data(cleaned):
            continue
        kwargs = {}
        for field in form.fields:
            if field in ('DELETE', 'id'):
                continue
            if field in cleaned:
                kwargs[field] = cleaned[field]
        obj = model(**kwargs)
        # Use the real Resume for FK typing; date helpers only need duration_display.
        obj.resume = resume
        items.append(obj)
    return items


def _build_draft_resume(request, resume):
    form = ResumeForm(request.POST, request.FILES, instance=resume)
    form.is_valid()
    fields = {name: _draft_field_value(form, resume, name) for name in _RESUME_DRAFT_FIELDS}
    fields['preferred_template'] = normalize_template(fields.get('preferred_template') or 't1')
    fields['summary'] = fields.get('summary') or ''
    fields['github'] = (fields.get('github') or '').strip()
    fields['linkedin'] = (fields.get('linkedin') or '').strip()
    draft = DraftResume(resume, fields, {
        'educations': [],
        'experiences': [],
        'projects': [],
        'skills': [],
        'certificates': [],
        'achievements': [],
        'languages': [],
        'hobbies': [],
    })
    formsets = _build_formsets(request, resume)
    for prefix, (model, rel_name) in _FORMSET_MODELS.items():
        setattr(draft, rel_name, RelatedList(_objects_from_formset(formsets[prefix], model, resume)))
    return draft


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


def _build_formsets(request, resume=None):
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


def _save_formsets(resume, formsets):
    save_ordered_formset(formsets['edu'], resume, 'educations', 'edu')
    save_ordered_formset(formsets['exp'], resume, 'experiences', 'exp')
    save_ordered_formset(formsets['proj'], resume, 'projects', 'proj')
    save_ordered_formset(formsets['skill'], resume, 'skills', 'skill')
    save_ordered_formset(formsets['cert'], resume, 'certificates', 'cert')
    save_ordered_formset(formsets['ach'], resume, 'achievements', 'ach')
    save_ordered_formset(formsets['lang'], resume, 'languages', 'lang')
    save_ordered_formset(formsets['hobby'], resume, 'hobbies', 'hobby')


def _gallery_blurb(tid):
    blurbs = {
        't1': 'Navy & gold executive style — centered header, classic rules.',
        't1s': 'Teal minimal stack — clean sections with mint accents.',
        't2s': 'Purple sidebar — contact & skills on a colored panel.',
        't3s': 'Crimson timeline — red stripe with dense two columns.',
        't4s': 'Dark slate header — sky-blue highlights, modern grid.',
    }
    return blurbs.get(tid, 'Single-page professional layout.')


def _safe_redirect(request, next_url, fallback='dashboard'):
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect(fallback)


@login_required
def dashboard(request):
    resumes = Resume.objects.filter(user=request.user)
    resume = get_user_resume(request)
    share_url = ''
    render_ctx = {}
    if resume:
        template = normalize_template(resume.preferred_template)
        render_ctx = _resume_context(resume, request, template=template)
        if resume.is_public:
            share_url = request.build_absolute_uri(reverse('public_resume', kwargs={'slug': resume.slug}))
    else:
        template = 't1'
    return render(request, 'resumes/dashboard.html', {
        'resume': resume,
        'resumes': resumes,
        'template': template,
        'template_label': TEMPLATE_LABELS.get(template, 'Executive Navy'),
        'preview_template': TEMPLATE_MAP[template],
        'share_url': share_url,
        'template_choices': list(TEMPLATE_LABELS.items()),
        **render_ctx,
    })


@login_required
def select_resume(request, resume_id):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    set_active_resume(request, resume)
    messages.success(request, f'Switched to {resume.resume_name}')
    return _safe_redirect(request, request.GET.get('next'), 'dashboard')


@login_required
def new_resume(request):
    if request.method == 'POST':
        resume = Resume.objects.create(
            user=request.user,
            resume_name=request.POST.get('resume_name', 'My Resume') or 'My Resume',
            title='',
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email or '',
            phone='',
            summary='',
        )
        set_active_resume(request, resume)
        return redirect('edit_resume', resume_id=resume.pk)
    return render(request, 'resumes/new_resume.html')


@login_required
@require_POST
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

    formsets = _build_formsets(request, resume)

    if request.method == 'POST':
        resume_form = ResumeForm(request.POST, request.FILES, instance=resume)
        all_valid = resume_form.is_valid()
        for fs in formsets.values():
            all_valid = all_valid and fs.is_valid()

        if all_valid:
            resume = resume_form.save(commit=False)
            resume.user = request.user
            resume.preferred_template = normalize_template(resume.preferred_template)
            raw_pw = resume_form.cleaned_data.get('share_password_input', '')
            if raw_pw:
                set_share_password(resume, raw_pw)
            resume.save()
            _save_formsets(resume, formsets)
            set_active_resume(request, resume)
            messages.success(request, 'Resume saved.')
            return redirect('edit_resume', resume_id=resume.pk)
        messages.error(request, 'Please fix the errors below.')
        resume_form = ResumeForm(request.POST, request.FILES, instance=resume)
    else:
        resume_form = ResumeForm(instance=resume)

    preview_template = normalize_template(
        request.GET.get('preview', resume.preferred_template if resume else 't1')
    )

    preview_url = ''
    draft_preview_url = ''
    if resume:
        preview_url = reverse('preview_fragment', kwargs={'resume_id': resume.pk, 'template': '__tpl__'})
        draft_preview_url = reverse('preview_draft', kwargs={'resume_id': resume.pk, 'template': '__tpl__'})

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
        'preview_url': preview_url,
        'draft_preview_url': draft_preview_url,
        'template_choices': list(TEMPLATE_LABELS.items()),
        'template_themes': TEMPLATE_THEMES,
        'template_chips': [
            (tid, TEMPLATE_LABELS[tid], TEMPLATE_THEMES[tid]['primary'])
            for tid in TEMPLATE_LABELS
        ],
    })


@login_required
def template_gallery(request):
    resume = get_user_resume(request)
    templates = [
        (tid, TEMPLATE_LABELS[tid], _gallery_blurb(tid), TEMPLATE_THEMES[tid]['primary'])
        for tid in ('t1', 't1s', 't2s', 't3s', 't4s')
    ]
    current = normalize_template(resume.preferred_template) if resume else 't1'
    return render(request, 'resumes/template_gallery.html', {
        'resume': resume,
        'templates': templates,
        'current_template': current,
    })


@login_required
@require_POST
def apply_template(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    resume.preferred_template = normalize_template(template)
    resume.save()
    messages.success(request, f'Template set to {TEMPLATE_LABELS.get(resume.preferred_template, "Executive Navy")}.')
    return redirect('template_gallery')


@login_required
def view_resume(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    template = normalize_template(template)
    ctx = _resume_context(resume, request, template=template)
    share_url = ''
    if resume.is_public:
        share_url = request.build_absolute_uri(reverse('public_resume', kwargs={'slug': resume.slug}))
    return render(request, 'resumes/view_wrapper.html', {
        'resume': resume,
        'template_name': TEMPLATE_MAP[template],
        'selected_template': template,
        'template_label': TEMPLATE_LABELS.get(template, 'Executive Navy'),
        'share_url': share_url,
        'template_choices': list(TEMPLATE_LABELS.items()),
        **ctx,
    })


@login_required
def my_resumes(request):
    resumes = Resume.objects.filter(user=request.user)
    active = get_user_resume(request)
    return render(request, 'resumes/my_resumes.html', {
        'resumes': resumes,
        'active_resume': active,
    })


@login_required
@require_GET
def preview_fragment(request, resume_id, template):
    template = normalize_template(template)
    if request.GET.get('sample') == '1':
        html = render_resume_html(get_sample_resume(), template, for_pdf=True, request=request)
        return HttpResponse(html)
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    html = render_resume_html(resume, template, for_pdf=True, request=request)
    return HttpResponse(html)


@login_required
@require_GET
def preview_sample(request, template):
    template = normalize_template(template)
    html = render_resume_html(get_sample_resume(), template, for_pdf=True, request=request)
    return HttpResponse(html)


@login_required
@require_POST
def preview_draft(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    template = normalize_template(template)
    draft = _build_draft_resume(request, resume)
    html = render_resume_html(draft, template, for_pdf=True, request=request)
    return HttpResponse(html)


@login_required
def download_pdf(request, resume_id, template):
    resume = get_object_or_404(Resume, pk=resume_id, user=request.user)
    template = normalize_template(template or resume.preferred_template)
    filename = f'{resume.resume_name.replace(" ", "_")}_{template}.pdf'
    return pdf_response(resume, template, filename, request=request)


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
            return render(
                request,
                'resumes/share_password.html',
                {'resume': resume, 'form': form, 'error': 'Incorrect password.'},
            )
        if not request.session.get(f'share_ok_{resume.slug}'):
            return render(request, 'resumes/share_password.html', {'resume': resume, 'form': SharePasswordForm()})
    else:
        request.session[f'share_ok_{resume.slug}'] = True

    template = normalize_template(request.GET.get('t', resume.preferred_template))
    ctx = _resume_context(resume, request, template=template)
    return render(request, 'resumes/public_view.html', {
        **ctx,
        'template_name': TEMPLATE_MAP[template],
        'template': template,
    })


@login_required
def profile(request):
    user = request.user
    resume = get_user_resume(request)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'profile':
            profile_form = ProfileForm(request.POST, instance=user)
            password_form = TailwindPasswordChangeForm(user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated.')
                return redirect('profile')
        elif action == 'password':
            profile_form = ProfileForm(instance=user)
            password_form = TailwindPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Password changed.')
                return redirect('profile')
        elif action == 'delete_account':
            user.delete()
            return redirect('home')
        else:
            profile_form = ProfileForm(instance=user)
            password_form = TailwindPasswordChangeForm(user)
    else:
        profile_form = ProfileForm(instance=user)
        password_form = TailwindPasswordChangeForm(user)

    return render(request, 'resumes/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'resume': resume,
    })
