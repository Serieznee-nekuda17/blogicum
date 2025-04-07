from django.urls import path, include

from . import views

app_name = 'blog'

post_urls = [
    path('create/', views.CreatePostView.as_view(), name='create_post'),
    path('<int:post_id>/',
         views.PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/edit/',
         views.UpdatePostView.as_view(), name='edit_post'),
    path('<int:post_id>/delete/',
         views.DeletePostView.as_view(), name='delete_post'),
    path('<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('<int:post_id>/edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('<int:post_id>/delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
]

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('posts/', include(post_urls,)),
    path('category/<slug:category_slug>/',
         views.CategoryPostView.as_view(), name='category_posts'),
    path('profile/edit-profile/',
         views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/',
         views.UserProfileView.as_view(), name='profile'),
]
