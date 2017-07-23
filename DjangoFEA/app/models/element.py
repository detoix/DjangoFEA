from django.db import models
import numpy as np
import math as math
from app.models import DataItem, Node, Section

class Element(DataItem):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, unique=False)
    node_start = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_start")
    node_end = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_end")
    hinge_start = models.BooleanField()
    hinge_end = models.BooleanField()

    @property
    def num_of_calc(self):
        return 100

    class Meta:
        unique_together = ('node_start', 'node_end')

    def deflection(self, dis, associated_loads):
        L = math.sqrt ((self.node_end.x - self.node_start.x) **2 + (self.node_end.y - self.node_start.y) **2)
        sin = (self.node_end.y - self.node_start.y) / L
        cos = (self.node_end.x - self.node_start.x) / L
        node_a = list(Node.objects.all()).index(self.node_start)
        node_b = list(Node.objects.all()).index(self.node_end)

        xy = []
        length = np.linspace(0, L, self.num_of_calc + 1)
        for i in length:
            [x_dead, y_dead] = self.calculate_deflection_of_dead_loads(i, L, sin, cos)
            [x, y] = self.calculate_deflection(dis, i, L, sin, cos, node_a, node_b)

            x_load = 0
            y_load = 0
            for load in associated_loads:
                [x_l, y_l] = load.dis_loads(i)
                x_load += x_l
                y_load += y_l

            dx = x_dead + x + x_load
            dy = y_dead + y + y_load

            scale = 100000
            u = self.node_start.x + ((i + dx * scale) * cos - dy * scale * sin)
            v = self.node_start.y + ((i + dx * scale) * sin + dy * scale * cos)

            xy.append({ 'x': u, 'y': v })

        return xy

    def calculate_deflection_of_dead_loads(self, i, L, sin, cos):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000
        dl = self.section.ro*A/10000

        if self.hinge_start == False and self.hinge_end == False:
            dy_dead = -dl*i**2/24/E/J*(L-i)**2*cos*10000
        elif self.hinge_start == True and self.hinge_end == False:
            dy_dead = -dl*i/48/E/J*(L**3-3*L*i**2+2*i**3)*cos*10000
        elif self.hinge_start == False and self.hinge_end == True:
            dy_dead = -dl*(L-i)/48/E/J*(L**3-3*L*(L-i)**2+2*(L-i)**3)*cos*10000
        elif self.hinge_start == True and self.hinge_end == True:
            dy_dead = -dl*i/24/E/J*(L**3-2*L*i**2+i**3)*cos*10000
          
        #dead load
        dx_dead = (- dl*sin*L*(L-0-L/2)/L*i/(E*A) + dl*sin*(i-0)**2/(E*A)/2)*10000

        return dx_dead, dy_dead  

    def calculate_deflection(self, dis, i, L, sin, cos, node_a, node_b):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000

        #computed displacements
        u1 = dis[node_a*3]
        v1 = dis[node_a*3 + 1]
        f1 = dis[node_a*3 + 2]
        u2 = dis[node_b*3]
        v2 = dis[node_b*3 + 1]
        f2 = dis[node_b*3 + 2]

        zeta = i/L
        if self.hinge_start == False and self.hinge_end == False:
            V1 = (1-3*(zeta**2)+2*(zeta**3))
            V2 = L*(zeta-2*(zeta**2)+(zeta**3))
            V3 = (3*(zeta**2)-2*(zeta**3))
            V4 = L*(-(zeta**2)+(zeta**3))
        elif self.hinge_start == False and self.hinge_end == True:
            V1 = (1-3/2*(zeta**2)+1/2*(zeta**3))
            V2 = 1/2*(zeta**2)*i-3/2*zeta*i+i
            V3 = (3/2*(zeta**2)-1/2*(zeta**3))
            V4 = 0
        elif self.hinge_start == True and self.hinge_end == False:
            V1 = (1+1/2*(zeta**3)-3/2*zeta)
            V2 = 0
            V3 = -1/2*(zeta**3)+3/2*zeta
            V4 = -1/2*i+1/2*(zeta**2)*i
        elif self.hinge_start == True and self.hinge_end == True:
            V1 = (1-zeta)
            V2 = 0
            V3 = zeta
            V4 = 0
        dy = (-u1*sin+v1*cos)*V1+f1*V2+(-u2*sin+v2*cos)*V3+f2*V4

        #parallel displacements
        U1 = -(i-L)/L
        U2 = i/L
        dx = (u1*cos+v1*sin)*U1+(u2*cos+v2*sin)*U2
        
        return dx, dy

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

    def assemble(self, Ko):
        x1 = self.node_start.x
        y1 = self.node_start.y
        x2 = self.node_end.x
        y2 = self.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
            
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000
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

        ne = node_a * 3
        ke = node_b * 3
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

    def dead(self, po):
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

        ro = self.section.ro/100
        A = self.section.A
        dl = ro*A/100
        if bc0 == False and bc1 == False:
            po[node_a*3+1] += -dl*L/2
            po[node_a*3+2] += -dl*L**2/12*cos
            po[node_b*3+1] += -dl*L/2
            po[node_b*3+2] += dl*L**2/12*cos
        if bc0 == True and bc1 == False:
            po[node_a*3+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            po[node_a*3+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            po[node_a*3+2] += 0
            po[node_b*3+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            po[node_b*3+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            po[node_b*3+2] += dl*cos*L**2/8
        if bc0 == False and bc1 == True:
            po[node_a*3+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            po[node_a*3+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            po[node_a*3+2] += -dl*cos*L**2/8
            po[node_b*3+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            po[node_b*3+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            po[node_b*3+2] += 0
        if bc0 == True and bc1 == True:
            po[node_a*3+1] += -dl*L/2
            po[node_b*3+1] += -dl*L/2    
       
        return po

    def __str__(self):
        return str(self.pk)