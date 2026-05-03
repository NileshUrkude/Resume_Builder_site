
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create/', views.create_resume, name='create_resume'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('view/<str:template>/', views.view_resume, name='view_resume'),
    path('download/<str:template>/', views.download_pdf, name='download_pdf'),  
    
    path('accounts/', include('django.contrib.auth.urls')),  # login
]