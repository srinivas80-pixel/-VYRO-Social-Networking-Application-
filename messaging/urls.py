from django.urls import path
from . import views

urlpatterns = [
    path('', views.messages_page, name='messages_page'),
    path('new/', views.new_conversation, name='new_conversation'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
]
