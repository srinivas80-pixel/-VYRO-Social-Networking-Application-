from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import home_redirect
from profile_section.views import hashtag_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='landing'),
    path('auth/', include('authentication.urls')),
    path('home/', include('profile_section.urls')),
    path('profile/', include('profile_section.urls')),
    path('posts/', include('posts.urls')),
    path('messages/', include('messaging.urls')),
    path('explore/hashtag/<str:tag_name>/', hashtag_view, name='hashtag_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
