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
from app.models import Node, Section, Element, ConcentratedLoad
from app.api import NodeViewSet, SectionApi, ElementApi, ConcentratedLoadApi
from django.views.generic import TemplateView

admin.autodiscover()
admin.site.register(Node)
admin.site.register(Section)
admin.site.register(Element)
admin.site.register(ConcentratedLoad)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'^nodes', NodeViewSet)

urlpatterns = [
    url(r'^$', app.views.home, name='home'),
    url(r'^deflection', app.views.deflection, name='deflection'),
    url(r'^bending', app.views.bending, name='bending'),
    url(r'^shear', app.views.shear, name='shear'),
    url(r'^axial', app.views.axial, name='axial'),
    url(r'^(?P<item_type>[\w\-]+)/new/$', app.views.item_new, name='item_new'),
    url(r'^(?P<item_type>[\w\-]+)/(?P<pk>[0-9]+)/edit/$', app.views.item_edit, name='item_edit'),
    url(r'^(?P<item_type>[\w\-]+)/(?P<pk>[0-9]+)/delete/$', app.views.item_delete, name='item_delete'),
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

urlpatterns = urlpatterns + router.urls