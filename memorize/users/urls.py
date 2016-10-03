from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.profile, name='profile'),
   # url(r'^profile/$', views.profile, name='profile'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^facebook/$', views.user_facebook, name='user_facebook'),
    url(r'^change/$', views.user_password_change, name='change'),
    url(r'^reset/$', views.user_password_reset, name='reset'),
    url(r'^reset/reset-done/$', views.user_password_reset_done, name='reset-done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',            views.user_password_reset_confirm, name='reset-confirm'),
    #url(r'^reset/confirm', views.user_password_reset_confirm, name='reset-confirm'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/complete/$', views.user_password_reset_complete, name='reset-complete'),
    url(r'^reset/complete/$', views.user_password_reset_complete, name='reset-complete'),
    url(r'^edit_names/$',views.edit_names,name='edit-names'),
]
