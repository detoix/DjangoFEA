from rest_framework.viewsets import ModelViewSet

from app.serializers import NodeSerializer, SectionSerializer, ElementSerializer, ConcentratedLoadSerializer
from app.models import Node, Section, Element, ConcentratedLoad 

class NodeViewSet(ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer

class SectionApi(ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer

class ElementApi(ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer

class ConcentratedLoadApi(ModelViewSet):
    queryset = ConcentratedLoad.objects.all()
    serializer_class = ConcentratedLoadSerializer
