from django.conf.urls import url, include
from django.contrib import admin

from server.helloworld.helloworld import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'helloworld.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^hello', views.index),

]
