# @Time : 2020/11/5 11:36 
# @modele : urls
# @Author : zhengzhong
# @Software: PyCharm
from django.urls import path
from . import views
app_name = 'article'
urlpatterns = [
    path('article-list',views.article_list,name='article_list'),
    path('article-detail/<int:id>/', views.article_detail,name='article_detail'),
    path('article-create/',views.article_create,name='article_create'),
    path('article-delete/<int:id>/',views.article_delete,name='article_delete'),
    #安全的删除文章
    path('article-safe-delete/<int:id>/',views.article_safe_delete,name='article_safe_delete'),
    path('article-update/<int:id>/',views.article_update,name='article_update'),
    #详情类视图
    path('detail-view/<int:pk>',views.ArticleDetailView.as_view(),name='detail_view'),
    path('create-view/',views.ArticleCreateView.as_view(),name='create_view'),



]