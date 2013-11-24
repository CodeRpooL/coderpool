from django.conf.urls.defaults import *
from social_auth import urls
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$','login.views.welcome'),
    (r'^logout/$','login.views.userLogout'),
    (r'^home/$','login.views.home'),
    (r'^login/$','login.views.userLogin'),
    (r'^contestant/register/$','contestant.views.register'),
    (r'^contestant/changecontest/$','contestant.views.changecontest'),

    (r'^contest/createqn/$','admin.views.createqn'),


    (r'^ajkps/', include(admin.site.urls)),
    (r'',include(urls)),

)
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
             'document_root': settings.MEDIA_ROOT,}),)
