"""
Definition of models.
"""

from django.db import models
from django.utils import timezone
import numpy as np
import math as math

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
    x = models.FloatField()
    y = models.FloatField()
    x_boundary_condition = models.BooleanField()
    y_boundary_condition = models.BooleanField()
    fi_boundary_condition = models.BooleanField()

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
        return str(self.x)

class Element(DataItem):
    E = models.FloatField()
    A = models.FloatField()
    J = models.FloatField()
    ro = models.FloatField()
    node_start = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_start")
    node_end = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_end")
    hinge_start = models.BooleanField()
    hinge_end = models.BooleanField()

    class Meta:
        unique_together = ('node_start', 'node_end')

    #assembling stiffness matrix
    '''The function acts as follows:
        1. create empty matrixes,
        2. read positions of first and second node of each bar element,
        3. read characteristics,
        4. calculate transformation matrix R,
        5. compute partial matrixes B, C, D, for each type of bar (fixed-fixed, pinned-fixed, fixed-pinned, pinned-pinned),
        6. matrix transformation,
        7. assemble Bg, Cg, Dg (global coordinates) into global stiffness matrix Ko
        '''

    def assemble(self, dof, Ko):
        x1 = self.node_start.x
        y1 = self.node_start.y
        x2 = self.node_end.x
        y2 = self.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
            
        E = self.E*100000000
        A = self.A/10000
        J = self.J/100000000
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
        R = np.matrix([[x2 - x1, y1 - y2, 0],
                            [y2 - y1, x2 - x1, 0],
                            [0, 0, L]]) / L
        #frame element
        if self.hinge_start == False and self.hinge_end == False:
            B = np.matrix([[A / J, 0, 0],
                                [0, 12 / L ** 2, - 6 / L],
                                [0, - 6 / L, 4]])
            B = E * J * B / L
            C = np.matrix([[- A / J, 0, 0],
                                [0, - 12 / L ** 2, 6 / L],
                                [0, - 6 / L, 2]])
            C = E * J * C / L
            D = np.matrix([[A / J, 0, 0],
                                [0, 12 / L ** 2, 6 / L],
                                [0, 6 / L, 4]])
            D = E * J * D / L
            
        #lelf hinge
        elif self.hinge_start == True and self.hinge_end == False:
            B = np.matrix([[A / J, 0, 0],
                                [0, 3 / L ** 2, - 3 / L],
                                [0, - 3 / L, 3]])
            B = E * J * B / L
            C = np.matrix([[- A / J, 0, 0],
                                [0, - 3 / L ** 2, 3 / L],
                                [0, 0, 0]])
            C = E * J * C / L
            D = np.matrix([[A / J, 0, 0],
                                [0, 3 / L ** 2, 0],
                                [0, 0, 0]])
            D = E * J * D / L

        #right hinge    
        elif self.hinge_start == False and self.hinge_end == True:
            B = np.matrix([[A / J, 0, 0],
                                [0, 3 / L ** 2, 0],
                                [0, 0, 0]])
            B = E * J * B / L
            C = np.matrix([[- A / J, 0, 0],
                                [0, - 3 / L ** 2, 0],
                                [0, - 3 / L, 0]])
            C = E * J * C / L
            D = np.matrix([[A / J, 0, 0],
                                [0, 3 / L ** 2, 3 / L],
                                [0, 3 / L, 3]])
            D = E * J * D / L
                                
        #truss element
        else:
            B = np.matrix([[A * E / L, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]])
            C = np.matrix([[- A * E / L, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]])
            D = np.matrix([[A * E / L, 0, 0],
                                [0, 0, 0],
                                [0, 0, 0]])
        #trasformation
        Bg = R*B*R.T
        Cg = R*C*R.T
        Dg = R*D*R.T
                        
        #assembling
        node_a = list(Node.objects.all()).index(self.node_start)
        node_b = list(Node.objects.all()).index(self.node_end)

        ne = node_a * dof
        ke = node_b * dof
        Ko[ne:ne+Dg.shape[0], ne:ne+Dg.shape[1]] += Dg
        Ko[ke:ke+Bg.shape[0], ke:ke+Bg.shape[1]] += Bg
        Ko[ne:ne+Cg.shape[0], ke:ke+Cg.shape[1]] += Cg
        Ko[ke:ke+Cg.T.shape[0], ne:ne+Cg.T.shape[1]] += Cg.T
        return Ko
        
    #apply dead loads
    '''the function acts as follows:
        1. Read nodes and variables for each bar,
        2. update global force matrix po
        '''

    def dead(self, pZeros):
        dof = 3
        Neq = dof * len(Node.objects.all())
        po = np.empty(Neq)
        po.fill(0)

        x1 = self.node_start.x
        y1 = self.node_start.y
        x2 = self.node_end.x
        y2 = self.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
            
        node_a = list(Node.objects.all()).index(self.node_start)
        node_b = list(Node.objects.all()).index(self.node_end)
        bc0 = self.hinge_start
        bc1 = self.hinge_end
                  
        sin = (y2-y1) / L
        cos = (x2-x1) / L 

        ro = self.ro/100
        A = self.A
        dl = ro*A/100
        if bc0 == False and bc1 == False:
            po[node_a*dof+1] += -dl*L/2
            po[node_a*dof+2] += -dl*L**2/12*cos
            po[node_b*dof+1] += -dl*L/2
            po[node_b*dof+2] += dl*L**2/12*cos
        if bc0 == True and bc1 == False:
            po[node_a*dof+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            po[node_a*dof+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            po[node_a*dof+2] += 0
            po[node_b*dof+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            po[node_b*dof+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            po[node_b*dof+2] += dl*cos*L**2/8
        if bc0 == False and bc1 == True:
            po[node_a*dof+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            po[node_a*dof+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            po[node_a*dof+2] += -dl*cos*L**2/8
            po[node_b*dof+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            po[node_b*dof+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            po[node_b*dof+2] += 0
        if bc0 == True and bc1 == True:
            po[node_a*dof+1] += -dl*L/2
            po[node_b*dof+1] += -dl*L/2    
        pZeros[0] = po           
        return pZeros

    def __str__(self):
        return str(self.E)

class Load(DataItem):
    type = models.IntegerField()
    nature = models.IntegerField()
    group = models.IntegerField()
    associated_element = models.ForeignKey(Element, on_delete=models.CASCADE, unique=False)
    f1 = models.FloatField()
    f2 = models.FloatField()
    coord1 = models.FloatField()
    coord2 = models.FloatField()
    m = models.FloatField()
    deg = models.FloatField()

class ConcentratedLoad(Load):
    def __str__(self):
        return "conc"

    #static boundary conditions
    '''the function acts as follows:
        1. read nodes, bar data etc.,
        2. in case of concentrated load, basing on element type
            (fixed-fixed etc.), apply load to global force matrix,
        3. in case of distributed load, first check if distX or distY
            and set appropriate values of angles and loads,
        4. fill po matrix with values.
        '''

    def bc(self):
        dof = 3
        Neq = dof * len(Node.objects.all())
        po = np.empty(Neq)
        po.fill(0)
            
        x1 = self.associated_element.node_start.x
        y1 = self.associated_element.node_start.y
        x2 = self.associated_element.node_end.x
        y2 = self.associated_element.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
        angle = self.deg*math.pi/180
            
        node_a = list(Node.objects.all()).index(self.associated_element.node_start)
        node_b = list(Node.objects.all()).index(self.associated_element.node_end)
        bc0 = self.associated_element.hinge_start
        bc1 = self.associated_element.hinge_end
                  
        sin_loc = math.sin(angle)
        cos_loc = math.cos(angle)
        sin = (y2-y1) / L
        cos = (x2-x1) / L 
   
        p = self.f1
        Mz = self.m
        b = self.coord1*L
        a = L-b
        if bc0 == False and bc1 == False:
            #concentrated force part
            po[node_a*dof] += sin*(-p*cos_loc*(a**2)*(L+2*b))/(L ** 3) - a/L*p*sin_loc*cos
            po[node_a*dof+1] += -cos*(-p*cos_loc*(a**2)*(L+2*b))/(L ** 3) - a/L*p*sin_loc*sin
            po[node_a*dof+2] += cos_loc*p*b*(a ** 2)/(L ** 2)
            po[node_b*dof] += (-sin*p*cos_loc*(b**2)*(L+2*a))/(L ** 3) - b/L*p*sin_loc*cos
            po[node_b*dof+1] += -cos*(-p*cos_loc*(b**2)*(L+2*a))/(L ** 3) - b/L*p*sin_loc*sin
            po[node_b*dof+2] += -cos_loc*p*a*(b ** 2)/(L ** 2) 
            #concentrated moment part
            po[node_a*dof] += sin*(6*Mz*a)/L**3*(L-a)
            po[node_a*dof+1] += -cos*(6*Mz*a)/L**3*(L-a)
            po[node_a*dof+2] += Mz/L**2*(3*a**2-2*a*L)
            po[node_b*dof] += -sin*(6*Mz*a)/L**3*(L-a)
            po[node_b*dof+1] += cos*(6*Mz*a)/L**3*(L-a)
            po[node_b*dof+2] += Mz/L**2*(L**2-4*a*L+3*a**2)
        elif bc0 == False and bc1 == True:
            #concentrated force part
            po[node_a*dof] += sin*(-p*cos_loc*a*(3-(a/L)**2)/(2*L)) - a/L*p*sin_loc*cos
            po[node_a*dof+1] += -cos*(-p*cos_loc*a*(3-(a/L)**2)/(2*L)) - a/L*p*sin_loc*sin
            po[node_a*dof+2] += cos_loc*p*0.5*b*a*(2-b/L)/L
            po[node_b*dof] += sin*(-p*cos_loc*(b**2)*(3-b/L))/(L ** 2)/2 - b/L*p*sin_loc*cos
            po[node_b*dof+1] += -cos*(-p*cos_loc*(b**2)*(3-b/L))/(L ** 2)/2 - b/L*p*sin_loc*sin
            po[node_b*dof+2] += 0
            #concentrated moment part
            po[node_a*dof] += sin*3*Mz/2/L*(1-a**2/L**2)
            po[node_a*dof+1] += -cos*3/2*Mz/L*(1-a**2/L**2)
            po[node_a*dof+2] += -Mz/2*(1-3*a**2/L**2)
            po[node_b*dof] += -sin*3/2*Mz/L*(1-a**2/L**2)
            po[node_b*dof+1] += cos*3/2*Mz/L*(1-a**2/L**2)
            po[node_b*dof+2] += 0
        elif bc0 == True and bc1 == False:
            #concentrated force part
            po[node_a*dof] += sin*(-p*cos_loc*(a**2)*(3-a/L))/(L ** 2)/2 - a/L*p*sin_loc*cos
            po[node_a*dof+1] += -cos*(-p*cos_loc*(a**2)*(3-a/L))/(L ** 2)/2 - a/L*p*sin_loc*sin
            po[node_a*dof+2] += 0
            po[node_b*dof] += sin*(-p*cos_loc*b*(3-(b/L)**2)/(2*L)) - b/L*p*sin_loc*cos
            po[node_b*dof+1] += -cos*(-p*cos_loc*b*(3-(b/L)**2)/(2*L)) - b/L*p*sin_loc*sin
            po[node_b*dof+2] += -p*cos_loc*0.5*b*a*(2-a/L)/L
            #concentrated moment part
            po[node_a*dof] += sin*3*Mz/2/L*(1-b**2/L**2)
            po[node_a*dof+1] += -cos*3/2*Mz/L*(1-b**2/L**2)
            po[node_a*dof+2] += 0
            po[node_b*dof] += -sin*3/2*Mz/L*(1-b**2/L**2)
            po[node_b*dof+1] += cos*3/2*Mz/L*(1-b**2/L**2)
            po[node_b*dof+2] += -Mz/2*(1-3*b**2/L**2)
        else:
            #concentrated force part
            po[node_a*dof] += sin*(-p*cos_loc*a/L) - a/L*p*sin_loc*cos
            po[node_a*dof+1] += -cos*(-p*cos_loc*a/L) - a/L*p*sin_loc*sin
            po[node_a*dof+2] += 0
            po[node_b*dof] += sin*(-p*cos_loc*b/L) - b/L*p*sin_loc*cos
            po[node_b*dof+1] += -cos*(-p*cos_loc*b/L) - b/L*p*sin_loc*sin
            po[node_b*dof+2] += 0
            #concentrated moment part
            po[node_a*dof] += sin*Mz/L
            po[node_a*dof+1] += -cos*Mz/L
            po[node_a*dof+2] += 0
            po[node_b*dof] += -sin*Mz/L
            po[node_b*dof+1] += cos*Mz/L
            po[node_b*dof+2] += 0

        return po

class DistributedLoad(Load):
    def __str__(self):
        return "distr"

    def abc(self):
        return 3

class DistributedXLoad(Load):
    def __str__(self):
        return "distr-X"

    def abc(self):
        return 3

class Calculator():
    def __init__(self):
        self.nodes = Node.objects.all()
        self.elements = Element.objects.all()
        self.loads = ConcentratedLoad.objects.all()

    def run(self):
        return self.loads[0].abc()

    def calc(self):
        dof = 3
        Neq = dof * len(Node.objects.all())
        for load in self.loads:
            K0 = np.zeros([Neq, Neq])
            for element in self.elements:
                K0 = element.assemble(dof, K0)
            P0 = load.bc()
            K = np.matrix.copy(K0)
            P = np.matrix.copy(P0)
            for node in self.nodes:
                [K0, P0] = node.bc(K0, P0)
            displacements = np.linalg.solve(K0,P0)
            reactions = np.dot(K, displacements)-P