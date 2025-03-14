from django.urls import path, include
from . import views

urlpatterns = [
    path("dashboard/", views.Dashboard, name="dashboard"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    # path("menu/", views.manage_menu, name="manage_menu"),
    path("register/", views.RegisterView, name="register"),
    path("login/", views.LoginView , name="login"),
    path("logout/", views.LogoutView , name="logout"),
    path('forgot-password/', views.ForgotPasswordView, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.ResetPasswordSentView, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPasswordView, name='reset-password'),
    path('feedback/delete/<int:feedback_id>/', views.delete_feedback, name='delete_feedback'),


    path('menu/', views.menu_list, name='menu_list'),
    path('menu/add/', views.add_menu_item, name='menu_add'),
    path('menu/update/<int:item_id>/', views.update_menu_item, name='menu_update'),
    path('menu/delete/<int:item_id>/', views.delete_menu_item, name='menu_delete'),

    path('get-menu-items/', views.get_menu_items, name='get_menu_items'),
    path('get_chart_data/', views.get_chart_data, name='get_chart_data'),
]

