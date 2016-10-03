from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'memorize.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', include('main.urls')),
    url(r'^article_detail/', include('main.urls')),
    url(r'^users/', include('users.urls')),
    url(r'^files/', include('files.urls')),
    url(r'^repeat/', include('repeat.urls')),
    url('social-auth/',
include('social.apps.django_app.urls', namespace='social')),
    
]
