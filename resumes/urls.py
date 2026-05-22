from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('templates/', views.template_gallery, name='template_gallery'),
    path('profile/', views.profile, name='profile'),

    path('resume/new/', views.new_resume, name='new_resume'),
    path('resume/<int:resume_id>/select/', views.select_resume, name='select_resume'),
    path('resume/<int:resume_id>/duplicate/', views.duplicate_resume_view, name='duplicate_resume'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/<int:resume_id>/edit/', views.create_resume, name='edit_resume'),
    path('create/', views.create_resume, name='create_resume'),

    path('resume/<int:resume_id>/autosave/', views.autosave_resume, name='autosave_resume'),
    path('resume/<int:resume_id>/preview/<str:template>/', views.preview_fragment, name='preview_fragment'),
    path('resume/<int:resume_id>/view/<str:template>/', views.view_resume, name='view_resume'),
    path('resume/<int:resume_id>/download/<str:template>/', views.download_pdf, name='download_pdf'),
    path('resume/<int:resume_id>/download-docx/', views.download_docx, name='download_docx'),
    path('resume/<int:resume_id>/cover-letter/', views.download_cover_letter, name='download_cover_letter'),
    path('resume/<int:resume_id>/qr/', views.qr_code, name='qr_code'),

    path('resume/<int:resume_id>/ats/', views.ats_checker, name='ats_checker'),
    path('resume/<int:resume_id>/jd-match/', views.jd_matcher, name='jd_matcher'),
    path('resume/<int:resume_id>/ai-summary/', views.ai_summary, name='ai_summary'),

    path('r/<uuid:slug>/', views.public_resume, name='public_resume'),

    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
]
