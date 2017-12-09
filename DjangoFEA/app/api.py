from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, status

from collections import OrderedDict
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework_xml.parsers import XMLParser
from rest_framework_xml.renderers import XMLRenderer
from app.serializers import NodeSerializer, SectionSerializer, ElementSerializer, ElementWithNodesSerializer, ConcentratedLoadSerializer
from app.models import Node, Section, Element, ConcentratedLoad, Solver
from app.models import VoidResultsProvider, DeflectionResultsProvider, BendingResultsProvider, ShearResultsProvider, AxialResultsProvider

import json

class NodeViewSet(ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class NodeAllViewSet(ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    parser_classes = (XMLParser, JSONParser)
    renderer_classes = (XMLRenderer, JSONRenderer)

class SectionViewSet(ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class ElementViewSet(ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class ElementAllViewSet(ModelViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementWithNodesSerializer
    parser_classes = (XMLParser, JSONParser)
    renderer_classes = (XMLRenderer, JSONRenderer)

class Upload(APIView):
    parser_classes = (XMLParser, JSONParser)
    renderer_classes = (XMLRenderer, JSONRenderer)

    def get(self, request, format=None):
        elements = Element.objects.all()
        serializer = ElementWithNodesSerializer(elements, many=True)
        return Response({"other": 0, "elements": serializer.data})

    def post(self, request, *args, **kwargs):
        elements = request.data['elements']

        serializer = ElementWithNodesSerializer(data=elements, many=True)
        if serializer.is_valid():
            serializer.save()

            #self.delete_redundant_elements(elements)
                #.delete_redundant_nodes([x['node_start'] for x in elements] + [x['node_end'] for x in elements])

            return Response({"other": 0, "elements": serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_redundant_elements(self, collection):
        ids = set([x['id'] for x in collection])
        for x in Element.objects.all():
            if x.id not in ids:
                Element.delete(x)
        return self

    def delete_redundant_nodes(self, collection):
        #ids = [set([int(x['x']), int(x['y'])]) for x in collection]
        for x in Node.objects.all():
            if set([int(x.x), int(x.y)]) not in collection:
                Node.delete(x)
        return self


class ConcentratedLoadViewSet(ModelViewSet):
    queryset = ConcentratedLoad.objects.all()
    serializer_class = ConcentratedLoadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class ResultsViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get_results(self, results_provider):
        nodes = Node.objects.filter(author=self.request.user).order_by('created_date')
        elements = Element.objects.filter(author=self.request.user).order_by('created_date')
        loads = ConcentratedLoad.objects.filter(author=self.request.user).order_by('created_date')

        model_loads = [{ 'data': 
                            [{ 'x': obj.x, 'y': obj.y} for obj in loads], 
                         'label': "Loads", 
                         'lineTension': 0,
                         'fill': False,
                         'pointStyle': ['custom:{0}:{1}'.format(obj.f1, obj.angle) for obj in loads],
                         'pointRadius': 10,
                         'showLine': False }]

        model_bars = [{ 'data': 
                            [{ 'x': obj.node_start.x, 'y': obj.node_start.y},
                             { 'x': obj.node_end.x, 'y': obj.node_end.y}], 
                        'label': 'Bar ' + str(obj.id),
                        'lineTension': 0,
                        'fill': False } for obj in elements]

        data = Solver(self.request.user).solve(results_provider)
        chart_data = { 'datasets': model_loads + model_bars + data }
        return Response(json.dumps(chart_data))

class ModelViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(VoidResultsProvider())

class DeflectionViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(DeflectionResultsProvider())

class BendingViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(BendingResultsProvider())

class ShearViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(ShearResultsProvider())

class AxialViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(AxialResultsProvider())