"""
Definition of urls for DjangoFEA.
"""

from django.conf.urls import include, url
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from app.views import home
from app.models import Node, Section, Element, ConcentratedLoad
from app.api import NodeViewSet, SectionViewSet, ElementViewSet, ConcentratedLoadViewSet, ModelViewSet, DeflectionViewSet, BendingViewSet, ShearViewSet, AxialViewSet

admin.autodiscover()
admin.site.register(Node)
admin.site.register(Section)
admin.site.register(Element)
admin.site.register(ConcentratedLoad)

router = DefaultRouter()
router.register(r'^nodes', NodeViewSet)
router.register(r'^sections', SectionViewSet)
router.register(r'^elements', ElementViewSet)
router.register(r'^concentrated-loads', ConcentratedLoadViewSet)

urlpatterns = [
    url(r'^$', ensure_csrf_cookie(home)),
    url(r'^auth_api/', include('auth_api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^model/$', ModelViewSet.as_view()),
    url(r'^deflection/$', DeflectionViewSet.as_view()),
    url(r'^bending/$', BendingViewSet.as_view()),
    url(r'^shear/$', ShearViewSet.as_view()),
    url(r'^axial/$', AxialViewSet.as_view()),
] + router.urls