from django.urls import path
from . import views

urlpatterns = [
    path('update_post/<int:pk>/', views.PostUpdate.as_view()),
    path('create_post/', views.PostCreate.as_view()),
    path('tag/<str:slug>/', views.tag_page),
    path('category/<str:slug>/', views.category_page),   # views.py의 함수인 경우 함수명만 입력
    path('<int:pk>/', views.PostDetail.as_view()),       # 클래스인 경우 클래스명 입력후 .as_view()까지 입력
    path('', views.PostList.as_view()),
    path('<int:pk>/new_comment/', views.new_comment),
    # path('<int:pk>/', views.single_post_page),
    # path('', views.index),
]
