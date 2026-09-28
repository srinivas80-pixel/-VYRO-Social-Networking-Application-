from django.urls import path
from . import views
from . import notifications_views

urlpatterns = [
    path('feed/', views.home_feed, name='home'),
    path('user/<str:username>/', views.profile_view, name='profile_user'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('user/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('user/<str:username>/following/', views.following_list, name='following_list'),
    path('search/', views.search_view, name='search'),
    path('explore/', views.explore_view, name='explore'),
    path('notifications/', notifications_views.notifications_page, name='notifications'),
    path('notifications/<int:notif_id>/go/', notifications_views.notification_redirect, name='notification_redirect'),
    path('settings/', views.settings_view, name='settings'),
    path('meta-ai/', views.meta_ai_view, name='meta_ai'),
]
