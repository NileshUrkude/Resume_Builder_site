from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse
from django.template.loader import render_to_string
try:
    from playwright.sync_api import sync_playwright
    _HAS_PLAYWRIGHT = True
except Exception:
    _HAS_PLAYWRIGHT = False

try:
    from weasyprint import HTML, CSS
    _HAS_WEASY = True
except Exception:
    _HAS_WEASY = False

from xhtml2pdf import pisa

from .models import Resume


class RelatedList:
    """Minimal related-manager stand-in for draft/sample preview templates."""

    def __init__(self, items):
        self._items = list(items)

    def all(self):
        return self._items


class SampleResume:
    """In-memory demo resume for gallery previews."""

    def __init__(self):
        self.pk = 0
        self.photo = None
        self.resume_name = 'Sample Resume'
        self.full_name = 'Alex Morgan'
        self.title = 'Product Engineer'
        self.email = 'alex.morgan@example.com'
        self.phone = '+1 (555) 010-2040'
        self.summary = (
            'Product-minded engineer with 6+ years shipping reliable web apps. '
            'Focused on clear UX, measurable impact, and calm collaboration.'
        )
        self.github = 'https://github.com/example'
        self.linkedin = 'https://linkedin.com/in/example'
        self.font_family = 'Arial'
        self.preferred_template = 't1'

        def bullets(text):
            lines = []
            for line in (text or '').splitlines():
                line = line.strip().lstrip('•-*').strip()
                if line:
                    lines.append(line)
            return lines

        class Entry:
            pass

        exp = Entry()
        exp.job_title = 'Senior Product Engineer'
        exp.company = 'Northwind Labs'
        exp.duration = '2021 – Present'
        exp.description = 'Led redesign of onboarding that cut time-to-value by 28%.\nShipped design-system components used across 4 product teams.'
        exp.date_range = exp.duration
        exp.bullet_points = bullets(exp.description)

        exp2 = Entry()
        exp2.job_title = 'Software Engineer'
        exp2.company = 'Brightline'
        exp2.duration = '2018 – 2021'
        exp2.description = 'Built customer dashboard used by 12k monthly actives.\nImproved API latency by 35% through caching and query tuning.'
        exp2.date_range = exp2.duration
        exp2.bullet_points = bullets(exp2.description)

        edu = Entry()
        edu.degree = 'B.S. Computer Science'
        edu.college = 'State University'
        edu.location = 'Boston, MA'
        edu.duration = '2014 – 2018'
        edu.date_range = edu.duration

        proj = Entry()
        proj.name = 'ResumePro Demo'
        proj.tech_stack = 'Django, Tailwind, HTMX'
        proj.description = 'Polished resume builder with live PDF-matched preview.'
        proj.bullet_points = bullets(proj.description)

        skill_items = []
        for name, level, label in (
            ('Python', 'expert', 'Expert'),
            ('JavaScript', 'expert', 'Expert'),
            ('Product Design', 'intermediate', 'Intermediate'),
            ('System Design', 'intermediate', 'Intermediate'),
        ):
            s = Entry()
            s.name = name
            s.level = level
            s.get_level_display = (lambda l=label: l)
            skill_items.append(s)

        cert = Entry(); cert.name = 'AWS Cloud Practitioner'
        ach = Entry(); ach.title = 'Hackathon winner — DevTools track'
        lang1 = Entry(); lang1.name = 'English'; lang1.proficiency = 'native'; lang1.get_proficiency_display = lambda: 'Native'
        lang2 = Entry(); lang2.name = 'Spanish'; lang2.proficiency = 'conversational'; lang2.get_proficiency_display = lambda: 'Conversational'
        hobby1 = Entry(); hobby1.name = 'Trail running'
        hobby2 = Entry(); hobby2.name = 'Photography'

        self.experiences = RelatedList([exp, exp2])
        self.educations = RelatedList([edu])
        self.projects = RelatedList([proj])
        self.skills = RelatedList(skill_items)
        self.certificates = RelatedList([cert])
        self.achievements = RelatedList([ach])
        self.languages = RelatedList([lang1, lang2])
        self.hobbies = RelatedList([hobby1, hobby2])

    def duration_display(self, start, end):
        return Resume.duration_display(self, start, end)


def get_sample_resume():
    return SampleResume()


TEMPLATE_MAP = {
    't1': 'resumes/t1.html',
    't1s': 'resumes/t1s.html',
    't2s': 'resumes/t2s.html',
    't3s': 'resumes/t3s.html',
    't4s': 'resumes/t4s.html',
}

VALID_TEMPLATES = frozenset(TEMPLATE_MAP.keys())

SINGLE_PAGE_TEMPLATES = frozenset({'t1', 't1s', 't2s', 't3s', 't4s'})

TEMPLATE_LABELS = {
    't1': 'Executive Navy',
    't1s': 'Ocean Teal',
    't2s': 'Plum Sidebar',
    't3s': 'Crimson Pro',
    't4s': 'Slate & Sky',
}

# Fixed palette per template — each design looks distinct regardless of user accent pick.
TEMPLATE_THEMES = {
    't1': {
        'primary': '#1e3a5f',
        'accent': '#c9a227',
        'text': '#1e293b',
        'muted': '#64748b',
        'light': '#faf8f5',
        'pill_bg': '#eef2f7',
        'pill_border': '#cbd5e1',
        'header_bg': '#1e3a5f',
        'header_text': '#ffffff',
    },
    't1s': {
        'primary': '#0f766e',
        'accent': '#14b8a6',
        'text': '#134e4a',
        'muted': '#5eead4',
        'light': '#f0fdfa',
        'pill_bg': '#ccfbf1',
        'pill_border': '#99f6e4',
        'header_bg': '#0f766e',
        'header_text': '#ffffff',
    },
    't2s': {
        'primary': '#5b21b6',
        'accent': '#a78bfa',
        'text': '#1e1b4b',
        'muted': '#6b7280',
        'light': '#faf5ff',
        'pill_bg': '#ede9fe',
        'pill_border': '#c4b5fd',
        'sidebar_bg': '#4c1d95',
        'sidebar_text': '#f5f3ff',
    },
    't3s': {
        'primary': '#b91c1c',
        'accent': '#ef4444',
        'text': '#1f2937',
        'muted': '#6b7280',
        'light': '#fef2f2',
        'pill_bg': '#fee2e2',
        'pill_border': '#fecaca',
        'stripe': '#dc2626',
    },
    't4s': {
        'primary': '#0f172a',
        'accent': '#0ea5e9',
        'text': '#334155',
        'muted': '#64748b',
        'light': '#f0f9ff',
        'pill_bg': '#e0f2fe',
        'pill_border': '#7dd3fc',
        'header_bg': '#0f172a',
        'header_text': '#ffffff',
    },
}


def normalize_template(template):
    return template if template in VALID_TEMPLATES else 't1'


def is_single_page(template):
    return normalize_template(template) in SINGLE_PAGE_TEMPLATES


def _resume_context(resume, request=None, template='t1'):
    tpl = normalize_template(template)
    theme = TEMPLATE_THEMES.get(tpl, TEMPLATE_THEMES['t1'])
    font = resume.font_family or 'Arial'
    photo_url = ''
    if resume.photo:
        url = resume.photo.url
        photo_url = request.build_absolute_uri(url) if request else url
    return {
        'resume': resume,
        'accent_color': theme['primary'],
        'font_family': font,
        'photo_url': photo_url,
        'theme': theme,
        'tpl': tpl,
    }


def render_resume_html(resume, template, for_pdf=False, request=None):
    tpl = normalize_template(template)
    ctx = _resume_context(resume, request, template=tpl)
    ctx['for_pdf'] = for_pdf
    ctx['single_page'] = is_single_page(tpl)
    return render_to_string(TEMPLATE_MAP[tpl], ctx)


def pdf_response(resume, template, filename='resume.pdf', request=None):
    html = render_resume_html(resume, template, for_pdf=True, request=request)
    # Prefer Playwright (Chromium) for pixel-perfect browser rendering
    if _HAS_PLAYWRIGHT:
        base_url = request.build_absolute_uri('/') if request else None
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            # Use base URL so relative asset URLs resolve
            if base_url:
                page.set_content(html, wait_until='networkidle', base_url=base_url)
            else:
                page.set_content(html, wait_until='networkidle')
            pdf_bytes = page.pdf(format='A4', margin={'top':'10mm','bottom':'10mm','left':'10mm','right':'10mm'}, print_background=True)
            browser.close()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # Next prefer WeasyPrint
    if _HAS_WEASY:
        base_url = request.build_absolute_uri('/') if request else None
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 10mm }')])
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    # Fallback to xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pisa.CreatePDF(src=html, dest=response, encoding='utf-8')
    return response


def get_user_resume(request, resume_id=None):
    qs = Resume.objects.filter(user=request.user)
    if resume_id:
        return qs.filter(pk=resume_id).first()
    active = request.session.get('active_resume_id')
    if active:
        resume = qs.filter(pk=active).first()
        if resume:
            return resume
    return qs.first()


def set_active_resume(request, resume):
    request.session['active_resume_id'] = resume.pk


def set_share_password(resume, raw_password):
    if raw_password:
        resume.share_password = make_password(raw_password)
    else:
        resume.share_password = ''


def check_share_password(resume, raw_password):
    if not resume.share_password:
        return True
    return check_password(raw_password, resume.share_password)


def save_ordered_formset(formset, resume, related_name, order_prefix):
    getattr(resume, related_name).all().delete()
    for idx, form in enumerate(formset):
        if form.cleaned_data and not form.cleaned_data.get('DELETE'):
            obj = form.save(commit=False)
            obj.resume = resume
            obj.order = idx
            obj.save()
