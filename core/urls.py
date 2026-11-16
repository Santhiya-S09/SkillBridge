
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path(
        'career-guidance/',
        views.career_guidance,
        name='career_guidance'
    ),
    path(
        'skill-assessment/',
        views.skill_assessment,
        name='skill_assessment'
    ),
    path(
        'assessment-history/',
        views.assessment_history,
        name='assessment_history'
    ),
    path(
        'learning-roadmap/',
        views.learning_roadmap,
        name='learning_roadmap'
    ),
    path(
        'skill-gap-analysis/',
        views.skill_gap_analysis,
        name='skill_gap_analysis'
    ),
    path(
        'learning-center/<int:step_number>/',
        views.learning_center,
        name='learning_center'
    ),
    path(
        'learning-center/<slug:career_slug>/<int:step_number>/',
        views.career_learning_center,
        name='career_learning_center'
    ),

    # Separate Admin Panel
    path(
        'admin-login/',
        views.admin_login,
        name='admin_login'
    ),
    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),
    path(
        'admin-logout/',
        views.admin_logout,
        name='admin_logout'
    ),
]
