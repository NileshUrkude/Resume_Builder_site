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
from .template_registry import (
    SINGLE_PAGE_TEMPLATES,
    TEMPLATE_LABELS,
    TEMPLATE_MAP,
    TEMPLATE_THEMES,
    VALID_TEMPLATES,
)

__all__ = [
    'TEMPLATE_LABELS',
    'TEMPLATE_MAP',
    'TEMPLATE_THEMES',
    'VALID_TEMPLATES',
    'normalize_template',
    'is_single_page',
    'render_resume_html',
    'pdf_response',
    'get_user_resume',
    'set_active_resume',
    'set_share_password',
    'check_share_password',
    'save_ordered_formset',
]


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
    if _HAS_PLAYWRIGHT:
        base_url = request.build_absolute_uri('/') if request else None
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            if base_url:
                page.set_content(html, wait_until='networkidle', base_url=base_url)
            else:
                page.set_content(html, wait_until='networkidle')
            pdf_bytes = page.pdf(
                format='A4',
                margin={'top': '8mm', 'bottom': '8mm', 'left': '8mm', 'right': '8mm'},
                print_background=True,
            )
            browser.close()
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    if _HAS_WEASY:
        base_url = request.build_absolute_uri('/') if request else None
        pdf_bytes = HTML(string=html, base_url=base_url).write_pdf(
            stylesheets=[CSS(string='@page { size: A4; margin: 8mm }')],
        )
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

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
