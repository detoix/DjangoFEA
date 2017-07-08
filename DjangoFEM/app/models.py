from django.db import models
from django.utils import timezone

class DataItem(models.Model):
    author = models.ForeignKey('auth.User')
    project_name = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)

    def publish(self):
        self.save()

    def __str__(self):
        return self.project_name

    class Meta:
        abstract = True

class Node(DataItem):
    x_coord = models.FloatField()
    y_coord = models.FloatField()
    x_boundary_condition = models.BooleanField()
    y_boundary_condition = models.BooleanField()
    fi_boundary_condition = models.BooleanField()

    def __str__(self):
        return str(self.x_coord)

class Element(DataItem):
    E = models.FloatField()
    A = models.FloatField()
    J = models.FloatField()
    ro = models.FloatField()
    node_start = models.ManyToManyField(Node, related_name="node_start")
    node_end = models.ManyToManyField(Node, related_name="node_end")
    hinge_start = models.BooleanField()
    hinge_end = models.BooleanField()

    def __str__(self):
        return str(self.node_start.getpa)

class Calculator():
    def run(self):
        self.nodes = Node.objects.all()
        self.elements = Element.objects.all()
        self.a = "2"