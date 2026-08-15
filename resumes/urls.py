from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('templates/', views.template_gallery, name='template_gallery'),
    path('my-resumes/', views.my_resumes, name='my_resumes'),
    path('profile/', views.profile, name='profile'),

    path('resume/new/', views.new_resume, name='new_resume'),
    path('resume/<int:resume_id>/select/', views.select_resume, name='select_resume'),
    path('resume/<int:resume_id>/delete/', views.delete_resume, name='delete_resume'),
    path('resume/<int:resume_id>/edit/', views.create_resume, name='edit_resume'),
    path('resume/<int:resume_id>/apply-template/<str:template>/', views.apply_template, name='apply_template'),
    path('create/', views.create_resume, name='create_resume'),

    path('resume/<int:resume_id>/preview/<str:template>/', views.preview_fragment, name='preview_fragment'),
    path('preview/sample/<str:template>/', views.preview_sample, name='preview_sample'),
    path('resume/<int:resume_id>/preview-draft/<str:template>/', views.preview_draft, name='preview_draft'),
    path('resume/<int:resume_id>/view/<str:template>/', views.view_resume, name='view_resume'),
    path('resume/<int:resume_id>/download/<str:template>/', views.download_pdf, name='download_pdf'),

    path('r/<uuid:slug>/', views.public_resume, name='public_resume'),

    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
]
