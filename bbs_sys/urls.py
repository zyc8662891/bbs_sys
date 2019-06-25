"""bbs_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from appo import views
from bbs_sys import settings
from django.views.static import serve
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index),
    url(r'index/$',views.index),
    url(r'^register/$', views.register),
    url(r'^check_username/$', views.check_username),
    #点赞点踩
    url(r'^upordown/$',views.upordown),
    url(r'^my_login/$',views.my_login,name='my_login'),
    url(r'^login_code/$',views.login_code),
    url(r'^backend/$',views.backend),
    # url(r'^backend/add_article/$',),
    #添加文章
    url(r'add_article',views.add_article),
    url(r'add_article/$',views.add_article),

    url(r'^my_logout/$',views.my_logout),
    url(r'^update_password/$',views.update_password),
    url(r'^update_avatar/$',views.update_avatar),
    url(r'^media/(?P<path>.*)',serve,{'document_root':settings.MEDIA_ROOT}),
    # url('^(?P<username>\w+)/article/(?P<article_id>\d+)$',)
    #文章详情 /owen/article/?.html
    url(r'^(?P<site>\w+)/article/(?P<aid>\d+).html$',views.article_page,name='article_page'),

    #个人站点
    url(r'^(?P<site>\w+)$',views.site_page),
    url(r'^(?P<site>\w+)/$',views.site_page),
    url(r'edit_article/(?P<article_id>\d+)',views.edit_article),















]