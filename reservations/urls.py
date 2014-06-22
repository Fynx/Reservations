from django.conf.urls import patterns, include, url
#from dajaxice.core import dajaxice_autodiscover

from django.contrib import admin
from django.contrib import auth
from res import views

admin.autodiscover()
#dajaxice.autodiscover()

urlpatterns = patterns('',
    url(r'^$', include('res.urls')),
    url(r'^res/', include('res.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^account/login/', 'res.views.login_view'),
    url(r'^account/logout/', 'res.views.logout_view'),
    #url(r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
)