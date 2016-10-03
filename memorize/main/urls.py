from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.article_list, name='article_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.article_detail, name='article_detail'),
    url(r'^contact/$', views.contact, name='contact'),
]
