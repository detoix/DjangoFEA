from rest_framework import serializers
from app.models import Node, Section, Element, ConcentratedLoad

class NodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Node
        fields = '__all__'
        validators = []

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'

class ElementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Element
        fields = '__all__'

class ElementWithNodesSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    node_start = NodeSerializer()
    node_end = NodeSerializer()

    class Meta:
        model = Element
        fields = '__all__'

    def create(self, validated_data):
        node_start_data = validated_data.pop('node_start')
        node_start, created = Node.objects.get_or_create(
            x=node_start_data['x'],
            y=node_start_data['y'], 
            defaults={
                "x": node_start_data['x'],
                "y": node_start_data['y'],
                "x_boundary_condition": node_start_data['x_boundary_condition'],
                "y_boundary_condition": node_start_data['y_boundary_condition'],
                "fi_boundary_condition": node_start_data['fi_boundary_condition'],
                "author_id": 1
                })

        node_end_data = validated_data.pop('node_end')
        node_end, created = Node.objects.get_or_create(
            x=node_end_data['x'],
            y=node_end_data['y'],
            defaults={
                "x": node_end_data['x'],
                "y": node_end_data['y'],
                "x_boundary_condition": node_end_data['x_boundary_condition'],
                "y_boundary_condition": node_end_data['y_boundary_condition'],
                "fi_boundary_condition": node_end_data['fi_boundary_condition'],
                "author_id": 1
                })

        section = Section.objects.first()

        if validated_data['id'] == 0:
            element = Element.objects.create(
                node_start = node_start,
                node_end = node_end,
                hinge_start = True,
                hinge_end = True,
                author_id = 1,
                section = section)
        else:
            element, created = Element.objects.update_or_create(
                id=validated_data['id'], 
                defaults={
                    "node_start": node_start,
                    "node_end": node_end,
                    "hinge_start": True,
                    "hinge_end": True,
                    "author_id": 1,
                    "section": section
                    })
        return element

class ConcentratedLoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConcentratedLoad
        fields = '__all__'