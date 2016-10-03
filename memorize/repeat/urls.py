from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.list, name='list'),
   # url(r'^(?P<user>[0-9A-Za-z]+)/(?P<pk>[0-9]+)/$', views.see_list, name='see_list'),
    url(r'^(?P<pk>[0-9]+)/$', views.see_list, name='see_list'),
    url(r'^revision/(?P<pk>[0-9]+)/$', views.revise, name='revise'),
    url(r'^add_list/$', views.add_list, name='add_list'),
    url(r'^remove_list/(?P<pk>[0-9]+)/$', views.remove_list, name='remove_list'),
    url(r'^add_flashcard/(?P<pk>[0-9]+)/$', views.add_flashcard, name='add_flashcard'),
    url(r'^remove_flashcard/(?P<pk>[0-9]+)/$', views.remove_flashcard, name='remove_flashcard'),
    url(r'^add/(?P<list_pk>[0-9]+)/(?P<answer_value>[0-9]+)/(?P<flashcard_pk>[0-9]+)/$', views.update_flashcard, name='update_flashcard'),
    url(r'^limit/(?P<pk>[0-9]+)/$', views.limit, name='limit'),
    
]
