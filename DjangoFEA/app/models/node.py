from django.db import models
from app.models import DataItem

class Node(DataItem):
    x = models.FloatField()
    y = models.FloatField()
    x_boundary_condition = models.BooleanField()
    y_boundary_condition = models.BooleanField()
    fi_boundary_condition = models.BooleanField()

    class Meta:
        unique_together = ('x', 'y')

    #kinematic boundary conditions - zeroing rows and placing ones diagonally
    def bc(self,K0,P0):
        self.id = list(Node.objects.all()).index(self)
        if self.x_boundary_condition == True:
            K0[self.id * 3,:]=0
            K0[self.id * 3, self.id * 3]=1
            P0[self.id * 3]=0
        if self.y_boundary_condition == True:
            K0[self.id * 3 + 1,:]=0
            K0[self.id * 3 + 1, self.id * 3 + 1]=1
            P0[self.id * 3 + 1]=0
        if self.fi_boundary_condition == True:
            K0[self.id * 3 + 2,:]=0
            K0[self.id * 3 + 2, self.id * 3 + 2]=1
            P0[self.id * 3 + 2]=0
        return K0,P0

    def __str__(self):
        return str(self.x) + ', ' + str(self.y)

