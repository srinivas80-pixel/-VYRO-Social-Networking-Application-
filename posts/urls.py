from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/like/', views.like_post, name='like_post'),
    path('<int:post_id>/repost/', views.repost, name='repost'),
    path('<int:post_id>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/reply/', views.reply_to_post, name='reply_to_post'),
    path('<int:post_id>/quote/', views.quote_post, name='quote_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('bookmarks/', views.bookmarks_page, name='bookmarks'),
    path('share-users/', views.share_users, name='share_users'),
    path('share-to-dm/', views.share_to_dm, name='share_to_dm'),
]
