from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('topics/', views.TopicListView.as_view(), name='topic-list'),
    path('posts/', views.PostListView.as_view(), name='post-list'),
]
