"""
Definition of urls for DjangoFEM.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
from django.conf.urls import include
from django.contrib import admin
from app.models import Node

admin.autodiscover()
admin.site.register(Node)

urlpatterns = [
    url(r'^$', app.views.home, name='home'),
    #url(r'^node/(?P<pk>[0-9]+)/edit/$', app.views.home, name='node_edit'),
    #url(r'^node/(?P<pk>[0-9]+)/edit/$', app.views.node_edit, name='node_edit'),
    #url(r'^element/(?P<pk>[0-9]+)/edit/$', app.views.element_edit, name='element_edit'),
    url(r'^node/(?P<pk>[0-9]+)/delete/$', app.views.node_delete, name='node_delete'),
    url(r'^section/(?P<pk>[0-9]+)/delete/$', app.views.section_delete, name='section_delete'),
    url(r'^element/(?P<pk>[0-9]+)/delete/$', app.views.element_delete, name='element_delete'),
    url(r'^load/(?P<pk>[0-9]+)/delete/$', app.views.load_delete, name='load_delete'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about', app.views.about, name='about'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
]
