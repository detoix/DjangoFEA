from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from app.serializers import NodeSerializer, SectionSerializer, ElementSerializer, ConcentratedLoadSerializer
from app.models import Node, Section, Element, ConcentratedLoad, Solver

import json

class NodeViewSet(ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = NodeSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

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

class ConcentratedLoadViewSet(ModelViewSet):
    queryset = ConcentratedLoad.objects.all()
    serializer_class = ConcentratedLoadSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(author=self.request.user)

class ResultsViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get_results(self, request, results_type):
        nodes = Node.objects.filter(author=self.request.user).order_by('created_date')
        elements = Element.objects.filter(author=self.request.user).order_by('created_date')
        
        model_nodes = [{ 'data': 
                            [{ 'x': obj.x, 'y': obj.y} for obj in nodes], 
                         'label': "Nodes", 
                         'lineTension': 0,
                         'fill': False,
                         'pointStyle': 'triangle',
                         'pointRadius': 10,
                         'showLine': False }]
        model_bars = [{ 'data': 
                            [{ 'x': obj.node_start.x, 'y': obj.node_start.y},
                             { 'x': obj.node_end.x, 'y': obj.node_end.y}], 
                        'label': 'Bar ' + str(obj),
                        'lineTension': 0,
                        'fill': False } for obj in elements]

        if results_type == None:
            data = []
        else:
            data = Solver(self.request.user).solve(results_type)
        chart_data = { 'datasets': model_nodes + model_bars + data }
        return Response(json.dumps(chart_data))

class ModelViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(request, None)

class DeflectionViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(request, 0)

class BendingViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(request, 1)

class ShearViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(request, 2)

class AxialViewSet(ResultsViewSet):
    def get(self, request):
        return super().get_results(request, 3)