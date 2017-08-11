from rest_framework import serializers
from app.models import Node, Section, Element, ConcentratedLoad

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class ElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Element
        fields = '__all__'

class ConcentratedLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcentratedLoad
        fields = '__all__'