from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.file_browser, name='file_browser'),
    url(r'^send_file/$', views.send_file, name='send_file'),
    url(r'^send_file/(?P<picture>[0-9A-Za-z_\-]+)/$', views.send_file, name='send_pic'),
    url(r'^download/(?P<in_download_hash>\w{25})/$', views.download_file, name='download_file'),
    url(r'^remove/(?P<in_remove_hash>\w{25})/$', views.remove_file, name='remove_file'),
    url(r'^share/$', views.share_assets, name='share_assets'),
    url(r'^share/(?P<in_share_hash>\w{25})/$', views.share_assets_wrapper, name='share_assets_wrapper'),
    url(r'^new_dir/$', views.new_dir, name='new_dir'),
    url(r'^remove_dir/(?P<in_remove_hash>\w{25})/$', views.remove_dir, name='remove_dir'),
    url(r'^change_dir/(?P<in_dir_hash>\w{25})/$', views.change_dir, name='change_dir'),
    url(r'^change_dir/(?P<in_dir_hash>\w{25})/(?P<is_share>[0-9A-Za-z_\-]+)/$', views.change_dir, name='see_share_dir'),
    url(r'^open_file/(?P<in_open_hash>\w{25})/$',views.open_file, name="open_file"),
    url(r'^unshare/(?P<in_share_hash>\w{25})/$', views.unshare, name='unshare'),
]
