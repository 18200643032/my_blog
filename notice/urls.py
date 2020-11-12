# @Time : 2020/11/12 11:05 
# @modele : urls
# @Author : zhengzhong
# @Software: PyCharm
from django.urls import path
from . import views

app_name = 'notice'

urlpatterns = [
    #通知列表
    path('list/',views.CommentNoticeListView.as_view(),name='list'),
    path('update/',views.CommentNoticeUpdateView.as_view(),name='update'),
]