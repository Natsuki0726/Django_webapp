from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


from .views import (
    IndexView,
    PostDetailView,
    CategoryListView,
    CategoryPostView,
    TagListView,
    TagPostView,
    SearchPostView,
    CommentFormView,
    comment_approve,
    comment_remove,
    ReplyFormView,
    reply_approve,
    reply_remove,
    ContactFormView,
    ContactResultView,
)

app_name = 'blog'
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name="blog/login.html"), name='login'),
    path('signup/', views.signup, name='signup'),
    path('home/', IndexView.as_view(), name='index'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('category/<str:category_slug>/', CategoryPostView.as_view(), name='category_post'),
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tag/<str:tag_slug>/', TagPostView.as_view(), name='tag_post'),
    path('search/', SearchPostView.as_view(), name='search_post'),
    path('comment/<int:pk>/', CommentFormView.as_view(), name='comment_form'),
    path('comment/<int:pk>/approve/', comment_approve, name='comment_approve'),
    path('comment/<int:pk>/remove/', comment_remove, name='comment_remove'),
    path('reply/<int:pk>/', ReplyFormView.as_view(), name='reply_form'),
    path('reply/<int:pk>/approve/', reply_approve, name='reply_approve'),
    path('reply/<int:pk>/remove/', reply_remove, name='reply_remove'),
    path("post/<int:pk>/like/",views.like,name="like"),
    path('contact/', ContactFormView.as_view(), name='contact_form'),
    path('contact/result/', ContactResultView.as_view(), name='contact_result'),
    path('logout/', auth_views.LogoutView.as_view(next_page="blog:login"), name='logout'),
    path('create/', views.Create.as_view(), name="create"),
]