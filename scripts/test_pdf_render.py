import os
import sys
# Ensure project root is on sys.path so Django settings can be imported
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Resume_Builder.settings')
import django
django.setup()

from resumes.models import Resume
from resumes.utils import render_resume_html
from django.test import RequestFactory

rf = RequestFactory()
request = rf.get('/')
# ensure host for absolute URIs
request.META['HTTP_HOST'] = 'localhost:8000'

resume = Resume.objects.first()
if not resume:
    print('NO_RESUME_FOUND')
    sys.exit(2)

template = resume.preferred_template or 't1'
html = render_resume_html(resume, template, for_pdf=True, request=request)
with open('tmp_resume_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)

# Try WeasyPrint
try:
    from weasyprint import HTML, CSS
    base_url = request.build_absolute_uri('/')
    HTML(string=html, base_url=base_url).write_pdf('tmp_resume.pdf', stylesheets=[CSS(string='@page { size: A4; margin: 10mm }')])
    print('WROTE_PDF_WEASY')
except Exception as e:
    print('WEASY_FAIL', e)
    try:
        from xhtml2pdf import pisa
        with open('tmp_resume.pdf', 'wb') as f:
            pisa.CreatePDF(src=html, dest=f, encoding='utf-8')
        print('WROTE_PDF_XHTML2PDF')
    except Exception as e2:
        print('PDF_FAIL', e2)
        sys.exit(3)

print('DONE')
