from django.db import models
from django.db.models.signals import post_init
import numpy as np
import math as math
from app.models import DataItem, Node, Section

class Element(DataItem):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, unique=False)
    node_start = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_start")
    node_end = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="node_end")
    hinge_start = models.BooleanField()
    hinge_end = models.BooleanField()
    #start_x = models.FloatField()
    #start_y = models.FloatField()
    #end_x = models.FloatField()
    #end_y = models.FloatField()
   
    @property
    def num_of_calc(self):
        return 10

    @property
    def E(self):
        return self.section.E * 100000000

    @property
    def A(self):
        return self.section.A / 10000

    @property
    def J(self):
        return self.section.J / 100000000

    @property
    def L(self):  
        return math.hypot(self.node_end.x - self.node_start.x, self.node_end.y - self.node_start.y)

    @property
    def R(self):
        x1 = self.node_start.x
        y1 = self.node_start.y
        x2 = self.node_end.x
        y2 = self.node_end.y      
        return np.matrix([[x2 - x1, y1 - y2, 0],
                          [y2 - y1, x2 - x1, 0],
                          [0, 0, self.L]]) / self.L

    class Meta:
        unique_together = ('node_start', 'node_end')

    def append_to_global_stiffness_matrix(self, K0, nodes):
        return self.calculate_B_partial_matrix() \
                   .calculate_C_partial_matrix() \
                   .calculate_D_partial_matrix() \
                   .transform_partial_matrices() \
                   .find_indices_in_global_stiffness_matrix(nodes) \
                   .append_to_and_return(K0)

    def set_hinges_state(self):
        if self.hinge_start == False and self.hinge_end == False:
            self.calculate_B_partial_matrix = self.calculate_B_partial_matrix_frame_element
            self.calculate_C_partial_matrix = self.calculate_C_partial_matrix_frame_element
            self.calculate_D_partial_matrix = self.calculate_D_partial_matrix_frame_element
        elif self.hinge_start == True and self.hinge_end == False:
            self.calculate_B_partial_matrix = self.calculate_B_partial_matrix_left_hinge
            self.calculate_C_partial_matrix = self.calculate_C_partial_matrix_left_hinge
            self.calculate_D_partial_matrix = self.calculate_D_partial_matrix_left_hinge
        elif self.hinge_start == False and self.hinge_end == True:
            self.calculate_B_partial_matrix = self.calculate_B_partial_matrix_right_hinge
            self.calculate_C_partial_matrix = self.calculate_C_partial_matrix_right_hinge
            self.calculate_D_partial_matrix = self.calculate_D_partial_matrix_right_hinge
        else:
            self.calculate_B_partial_matrix = self.calculate_B_partial_matrix_truss_element
            self.calculate_C_partial_matrix = self.calculate_C_partial_matrix_truss_element
            self.calculate_D_partial_matrix = self.calculate_D_partial_matrix_truss_element
        return self

    def calculate_B_partial_matrix_frame_element(self):
        self.B = np.matrix([[self.A / self.J, 0, 0],
                            [0, 12 / self.L ** 2, - 6 / self.L],
                            [0, - 6 / self.L, 4]]) * self.E * self.J / self.L
        return self

    def calculate_C_partial_matrix_frame_element(self):
        self.C = np.matrix([[- self.A / self.J, 0, 0],
                            [0, - 12 / self.L ** 2, 6 / self.L],
                            [0, - 6 / self.L, 2]]) * self.E * self.J / self.L
        return self

    def calculate_D_partial_matrix_frame_element(self):
        self.D = np.matrix([[self.A / self.J, 0, 0],
                            [0, 12 / self.L ** 2, 6 / self.L],
                            [0, 6 / self.L, 4]]) * self.E * self.J / self.L
        return self

    def calculate_B_partial_matrix_left_hinge(self):
        self.B = np.matrix([[self.A / self.J, 0, 0],
                            [0, 3 / self.L ** 2, - 3 / self.L],
                            [0, - 3 / self.L, 3]]) * self.E * self.J / self.L
        return self

    def calculate_C_partial_matrix_left_hinge(self):
        self.C = np.matrix([[- self.A / self.J, 0, 0],
                            [0, - 3 / self.L ** 2, 3 / self.L],
                            [0, 0, 0]]) * self.E * self.J / self.L
        return self

    def calculate_D_partial_matrix_left_hinge(self):
        self.D = np.matrix([[self.A / self.J, 0, 0],
                            [0, 3 / self.L ** 2, 0],
                            [0, 0, 0]]) * self.E * self.J / self.L
        return self

    def calculate_B_partial_matrix_right_hinge(self):
        self.B = np.matrix([[self.A / self.J, 0, 0],
                            [0, 3 / self.L ** 2, 0],
                            [0, 0, 0]]) * self.E * self.J / self.L
        return self

    def calculate_C_partial_matrix_right_hinge(self):
        self.C = np.matrix([[- self.A / self.J, 0, 0],
                            [0, - 3 / self.L ** 2, 0],
                            [0, - 3 / self.L, 0]]) * self.E * self.J / self.L
        return self

    def calculate_D_partial_matrix_right_hinge(self):
        self.D = np.matrix([[self.A / self.J, 0, 0],
                            [0, 3 / self.L ** 2, 3 / self.L],
                            [0, 3 / self.L, 3]]) * self.E * self.J / self.L
        return self

    def calculate_B_partial_matrix_truss_element(self):
        self.B = np.matrix([[self.A * self.E / self.L, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        return self

    def calculate_C_partial_matrix_truss_element(self):
        self.C = np.matrix([[- self.A * self.E / self.L, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        return self

    def calculate_D_partial_matrix_truss_element(self):
        self.D = np.matrix([[self.A * self.E / self.L, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        return self

    def set_empty_matrices(self):
        self.B = np.matrix([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        self.C = np.matrix([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        self.D = np.matrix([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
        return self

    def transform_partial_matrices(self):
        self.Bg = self.R*self.B*self.R.T
        self.Cg = self.R*self.C*self.R.T
        self.Dg = self.R*self.D*self.R.T
        return self

    def find_indices_in_global_stiffness_matrix(self, nodes):
        self.ne = nodes.index(self.node_start) * 3
        self.ke = nodes.index(self.node_end) * 3
        return self

    def append_to_and_return(self, K0):
        K0[self.ne:self.ne + self.Dg.shape[0], self.ne:self.ne + self.Dg.shape[1]] += self.Dg
        K0[self.ke:self.ke + self.Bg.shape[0], self.ke:self.ke + self.Bg.shape[1]] += self.Bg
        K0[self.ne:self.ne + self.Cg.shape[0], self.ke:self.ke + self.Cg.shape[1]] += self.Cg
        K0[self.ke:self.ke + self.Cg.T.shape[0], self.ne:self.ne + self.Cg.T.shape[1]] += self.Cg.T
        return K0
        
    def append_dead_load_to_force_matrix(self, P0, nodes):
        x1 = self.node_start.x
        y1 = self.node_start.y
        x2 = self.node_end.x
        y2 = self.node_end.y      
        L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
            
        node_a = nodes.index(self.node_start)
        node_b = nodes.index(self.node_end)
        bc0 = self.hinge_start
        bc1 = self.hinge_end
                  
        sin = (y2-y1) / L
        cos = (x2-x1) / L 

        ro = self.section.ro/100
        A = self.section.A
        dl = ro*A/100

        if bc0 == False and bc1 == False:
            P0[node_a*3+1] += -dl*L/2
            P0[node_a*3+2] += -dl*L**2/12*cos
            P0[node_b*3+1] += -dl*L/2
            P0[node_b*3+2] += dl*L**2/12*cos
        if bc0 == True and bc1 == False:
            P0[node_a*3+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            P0[node_a*3+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            P0[node_a*3+2] += 0
            P0[node_b*3+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            P0[node_b*3+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            P0[node_b*3+2] += dl*cos*L**2/8
        if bc0 == False and bc1 == True:
            P0[node_a*3+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
            P0[node_a*3+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
            P0[node_a*3+2] += -dl*cos*L**2/8
            P0[node_b*3+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
            P0[node_b*3+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
            P0[node_b*3+2] += 0
        if bc0 == True and bc1 == True:
            P0[node_a*3+1] += -dl*L/2
            P0[node_b*3+1] += -dl*L/2    

        return P0

    def calculate_deflection(self, displacements, associated_loads, nodes):
        L = math.sqrt ((self.node_end.x - self.node_start.x) **2 + (self.node_end.y - self.node_start.y) **2)
        sin = (self.node_end.y - self.node_start.y) / L
        cos = (self.node_end.x - self.node_start.x) / L
        node_a = nodes.index(self.node_start)
        node_b = nodes.index(self.node_end)

        xy = []
        length = np.linspace(0, L, self.num_of_calc + 1)
        for i in length:
            [x_dead, y_dead] = self.calculate_deflection_of_dead_loads_in_point(i, L, sin, cos)
            [x, y] = self.calculate_hermite_deflection_in_point(displacements, i, L, sin, cos, node_a, node_b)

            x_load = 0
            y_load = 0
            for load in associated_loads:
                [x_l, y_l] = load.calculate_deflection_in_point(i)
                x_load += x_l
                y_load += y_l

            dx = x_dead + x + x_load
            dy = y_dead + y + y_load

            xy.append({'tag': '(u: ' + format(dx, '.3f') + ', v: ' + format(dy, '.3f') + ')',
                       'x0': self.node_start.x + i * cos,
                       'y0': self.node_start.y + i * sin,
                       'dx': dx,
                       'dy': dy,
                       'sin': sin,
                       'cos': cos})
        return xy

    def calculate_deflection_of_dead_loads_in_point(self, i, L, sin, cos):
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

    def calculate_hermite_deflection_in_point(self, dis, i, L, sin, cos, node_a, node_b):
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

    def calculate_bending(self, displacements, associated_loads, nodes):
        L = math.sqrt ((self.node_end.x - self.node_start.x) **2 + (self.node_end.y - self.node_start.y) **2)
        sin = (self.node_end.y - self.node_start.y) / L
        cos = (self.node_end.x - self.node_start.x) / L
        node_a = nodes.index(self.node_start)
        node_b = nodes.index(self.node_end)

        xy = []
        length = np.linspace(0, L, self.num_of_calc + 1)
        for i in length:
            y_dead = self.calculate_bending_of_dead_loads_in_point(i, L, sin, cos)
            y = self.calculate_hermite_bending_in_point(displacements, i, L, sin, cos, node_a, node_b)

            y_load = 0
            for load in associated_loads:
                y_l = load.calculate_bending_in_point(i)
                y_load += y_l

            dy = y_dead + y + y_load

            xy.append({'tag': format(dy, '.3f') + ' kNm',
                       'x0': self.node_start.x + i * cos,
                       'y0': self.node_start.y + i * sin,
                       'dx': 0,
                       'dy': dy,
                       'sin': sin,
                       'cos': cos})
        return xy

    def calculate_bending_of_dead_loads_in_point(self, i, L, sin, cos):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000
        dl = self.section.ro*A/10000

        if self.hinge_start == False and self.hinge_end == False:
            dy_dead = dl/12*(6*L*i-L**2-6*i**2)*cos*10000
        elif self.hinge_start == True and self.hinge_end == False:
            dy_dead = dl*i*(3*L/8-i/2)*cos*10000
        elif self.hinge_start == False and self.hinge_end == True:
            dy_dead = dl*(L-i)*(3*L/8-(L-i)/2)*cos*10000
        elif self.hinge_start == True and self.hinge_end == True:
            dy_dead = dl*i/2*(L-i)*cos*10000

        return dy_dead  

    def calculate_hermite_bending_in_point(self, dis, i, L, sin, cos, node_a, node_b):
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
            V1 = 12*i/(L**3)-6/(L**2)
            V2 = 6*i/(L**2)-4/L
            V3 = 6/(L**2)-12*i/(L**3)
            V4 = 6*i/(L**2)-2/L         
        elif self.hinge_start == False and self.hinge_end == True:
            V1 = 3*i/(L**3)-3/(L**2)
            V2 = 3*i/(L**2)-3/L
            V3 = 3/(L**2)-3*i/(L**3)
            V4 = 0
        elif self.hinge_start == True and self.hinge_end == False:
            V1 = 3*i/(L**3)
            V2 = 0
            V3 = -3*i/(L**3)
            V4 = 3*i/(L**2)   
        elif self.hinge_start == True and self.hinge_end == True:
            V1 = 0
            V2 = 0
            V3 = 0
            V4 = 0
        dy = E*J*((-u1*sin+v1*cos)*V1+f1*V2+(-u2*sin+v2*cos)*V3+f2*V4)

        return dy

    def calculate_shear(self, displacements, associated_loads, nodes):
        L = math.sqrt ((self.node_end.x - self.node_start.x) **2 + (self.node_end.y - self.node_start.y) **2)
        sin = (self.node_end.y - self.node_start.y) / L
        cos = (self.node_end.x - self.node_start.x) / L
        node_a = nodes.index(self.node_start)
        node_b = nodes.index(self.node_end)

        xy = []
        length = np.linspace(0, L, self.num_of_calc + 1)
        for i in length:
            y_dead = self.calculate_shear_of_dead_loads_in_point(i, L, sin, cos)
            y = self.calculate_hermite_shear_in_point(displacements, i, L, sin, cos, node_a, node_b)

            y_load = 0
            for load in associated_loads:
                y_l = load.calculate_shear_in_point(i)
                y_load += y_l

            dy = y_dead + y + y_load

            xy.append({'tag': format(dy, '.3f') + ' kN',
                       'x0': self.node_start.x + i * cos,
                       'y0': self.node_start.y + i * sin,
                       'dx': 0,
                       'dy': dy,
                       'sin': sin,
                       'cos': cos})
        return xy

    def calculate_shear_of_dead_loads_in_point(self, i, L, sin, cos):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000
        dl = self.section.ro*A/10000

        if self.hinge_start == False and self.hinge_end == False:
            dy_dead = dl*(L/2-i)*cos*10000
        elif self.hinge_start == True and self.hinge_end == False:
            dy_dead = dl*(3/8*L-i)*cos*10000
        elif self.hinge_start == False and self.hinge_end == True:
            dy_dead = dl*(5/8*L-i)*cos*10000
        elif self.hinge_start == True and self.hinge_end == True:
            dy_dead = dl*(L/2-i)*cos*10000

        return dy_dead  

    def calculate_hermite_shear_in_point(self, dis, i, L, sin, cos, node_a, node_b):
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
            V1 = 12/(L**3)
            V2 = 6/(L**2)
            V3 = -12/(L**3)
            V4 = 6/(L**2)   
        elif self.hinge_start == False and self.hinge_end == True:
            V1 = 3/(L**3)
            V2 = 3/(L**2)
            V3 = -3/(L**3)
            V4 = 0
        elif self.hinge_start == True and self.hinge_end == False:
            V1 = 3/(L**3)
            V2 = 0
            V3 = -3/(L**3)
            V4 = 3/(L**2)   
        elif self.hinge_start == True and self.hinge_end == True:
            V1 = 0
            V2 = 0
            V3 = 0
            V4 = 0
        dy = E*J*((-u1*sin+v1*cos)*V1+f1*V2+(-u2*sin+v2*cos)*V3+f2*V4)

        return dy

    def calculate_axial(self, displacements, associated_loads, nodes):
        L = math.sqrt ((self.node_end.x - self.node_start.x) **2 + (self.node_end.y - self.node_start.y) **2)
        sin = (self.node_end.y - self.node_start.y) / L
        cos = (self.node_end.x - self.node_start.x) / L
        node_a = nodes.index(self.node_start)
        node_b = nodes.index(self.node_end)

        xy = []
        length = np.linspace(0, L, self.num_of_calc + 1)
        for i in length:
            y_dead = self.calculate_axial_of_dead_loads_in_point(i, L, sin, cos)
            y = self.calculate_hermite_axial_in_point(displacements, i, L, sin, cos, node_a, node_b)

            y_load = 0
            for load in associated_loads:
                y_l = load.calculate_axial_in_point(i)
                y_load += y_l

            dy = y_dead + y + y_load

            xy.append({'tag': format(dy, '.3f') + ' kN',
                       'x0': self.node_start.x + i * cos,
                       'y0': self.node_start.y + i * sin,
                       'dx': 0,
                       'dy': dy,
                       'sin': sin,
                       'cos': cos})
        return xy

    def calculate_axial_of_dead_loads_in_point(self, i, L, sin, cos):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000
        dl = self.section.ro*A/10000

        return (- dl*sin*L*(L-0-L/2)/L + dl*sin*(i-0))*10000

    def calculate_hermite_axial_in_point(self, displacements, i, L, sin, cos, node_a, node_b):
        E = self.section.E*100000000
        A = self.section.A/10000
        J = self.section.J/100000000

        #computed displacements
        u1 = displacements[node_a*3]
        v1 = displacements[node_a*3 + 1]
        f1 = displacements[node_a*3 + 2]
        u2 = displacements[node_b*3]
        v2 = displacements[node_b*3 + 1]
        f2 = displacements[node_b*3 + 2]

        zeta = i/L

        V1 = -1/L
        V2 = 1/L

        return E*A*((u1*cos+v1*sin)*V1+(u2*cos+v2*sin)*V2)

def post_constructor(**kwargs):
    instance = kwargs.get('instance') \
        .set_hinges_state() \
        .set_empty_matrices()
   
post_init.connect(post_constructor, Element)