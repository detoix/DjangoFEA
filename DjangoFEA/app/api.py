from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from collections import OrderedDict

from app.serializers import NodeSerializer, SectionSerializer, ElementSerializer, ConcentratedLoadSerializer
from app.models import Node, Section, Element, ConcentratedLoad, Solver
from app.models import VoidResultsProvider, DeflectionResultsProvider, BendingResultsProvider, ShearResultsProvider, AxialResultsProvider

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

    def get_results(self, results_provider):
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
                        'label': 'Bar ' + str(obj.id),
                        'lineTension': 0,
                        'fill': False } for obj in elements]

        data = Solver(self.request.user).solve(results_provider)
        chart_data = { 'datasets': model_nodes + model_bars + data }
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