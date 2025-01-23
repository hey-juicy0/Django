from django.urls import path
from . import views

urlpatterns = [
    # Blog 관련
    path('', views.PostList.as_view(), name='post_list'),
    path('create_post/', views.PostCreate.as_view(), name='create_post'),
    path('update_post/<int:pk>/', views.PostUpdate.as_view(), name='update_post'),
    path('<int:pk>/', views.PostDetail.as_view(), name='post_detail'),
    path('<int:pk>/new_comment/', views.new_comment, name='new_comment'),
    path('update_comment/<int:pk>/', views.CommentUpdate.as_view(), name='update_comment'),
    path('delete_comment/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('category/<str:slug>/', views.category_page, name='category_page'),
    path('tag/<str:slug>/', views.tag_page, name='tag_page'),
    path('search/<str:q>/', views.PostSearch.as_view(), name='search'),

    # Board 관련
    path('board/<str:slug>/', views.BoardPostList.as_view(), name='board_page'),
    path('board/<str:slug>/create_post/', views.PostCreate.as_view(), name='board_create_post'),  # 게시판 글 생성
    path('board/<str:slug>/<int:pk>/', views.PostDetail.as_view(), name='board_post_detail'),  # 게시판 글 상세
    path('board/<str:slug>/<int:pk>/update_post/', views.PostUpdate.as_view(), name='board_update_post'),  # 게시판 글 수정
    path('board/<str:slug>/<int:pk>/delete_comment/', views.delete_comment, name='board_delete_comment'),  # 게시판 글 삭제
    path('board/<str:slug>/<int:pk>/new_comment/', views.new_comment, name='board_new_comment'),  # 게시판 댓글 작성
    path('board/<str:slug>/<int:pk>/update_comment/', views.CommentUpdate.as_view(), name='board_update_comment'),

]
