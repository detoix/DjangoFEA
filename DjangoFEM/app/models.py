"""
Definition of models.
"""

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

    #kinematic boundary conditions - zeroing rows and placing ones diagonally
    def bc(self,Ko,po):
        K = np.matrix.copy(Ko)
        P = np.matrix.copy(po)
        for item in self._registry:
            if item.bcx_var.get() == 0:
                Ko[item.id.get() * 3,:]=0
                Ko[item.id.get() * 3,item.id.get() * 3]=1
                po[item.id.get() * 3]=0
            if item.bcy_var.get() == 0:
                Ko[item.id.get() * 3 + 1,:]=0
                Ko[item.id.get() * 3 + 1,item.id.get() * 3 + 1]=1
                po[item.id.get() * 3 + 1]=0
            if item.bcfi_var.get() == 0:
                Ko[item.id.get() * 3 + 2,:]=0
                Ko[item.id.get() * 3 + 2,item.id.get() * 3 + 2]=1
                po[item.id.get() * 3 + 2]=0
        return K,P

    def __str__(self):
        return str(self.x_coord)

class Element(DataItem):
    E = models.FloatField()
    A = models.FloatField()
    J = models.FloatField()
    ro = models.FloatField()
    node_start = models.OneToOneField(Node, null=True, related_name="node_start")
    node_end = models.OneToOneField(Node, null=True, related_name="node_end")
    hinge_start = models.BooleanField()
    hinge_end = models.BooleanField()

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

    def assemble(self):
        dof = 3
        Neq = dof * len(node.entry._registry)
        Ko = np.empty([Neq, Neq])
        Ko.fill(0)
        for item in self._registry:
            x1 = node.entry._registry[item.node_a_var.get()].x_var.get()
            y1 = node.entry._registry[item.node_a_var.get()].y_var.get()
            x2 = node.entry._registry[item.node_b_var.get()].x_var.get()
            y2 = node.entry._registry[item.node_b_var.get()].y_var.get()
            
            E = item.E_var.get()*100000000
            A = item.A_var.get()/10000
            J = item.J_var.get()/100000000
            L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)
            R = np.matrix([[x2 - x1, y1 - y2, 0],
                                [y2 - y1, x2 - x1, 0],
                                [0, 0, L]]) / L
            #frame element
            if item.bc_a_var.get() == 0 and item.bc_b_var.get() == 0:
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
            elif item.bc_a_var.get() == 1 and item.bc_b_var.get() == 0:
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
            elif item.bc_a_var.get() == 0 and item.bc_b_var.get() == 1:
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
            ne = item.node_a_var.get() * dof
            ke = item.node_b_var.get() * dof
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
        Neq = dof * len(node.entry._registry)
        po = np.empty(Neq)
        po.fill(0)
        for item in self._registry:
            x1 = node.entry._registry[item.node_a_var.get()].x_var.get()
            y1 = node.entry._registry[item.node_a_var.get()].y_var.get()
            x2 = node.entry._registry[item.node_b_var.get()].x_var.get()
            y2 = node.entry._registry[item.node_b_var.get()].y_var.get()   
            L = math.sqrt ((x2 - x1) **2 + (y2 - y1) **2)

            node_a = item.node_a_var.get()
            node_b = item.node_b_var.get()
            bc0 = item.bc_a_var.get()
            bc1 = item.bc_b_var.get()
                  
            sin = (y2-y1) / L
            cos = (x2-x1) / L 

            ro = item.ro_var.get()/100
            A = item.A_var.get()
            dl = ro*A/100
            if bc0 == 0 and bc1 == 0:
                po[node_a*dof+1] += -dl*L/2
                po[node_a*dof+2] += -dl*L**2/12*cos
                po[node_b*dof+1] += -dl*L/2
                po[node_b*dof+2] += dl*L**2/12*cos
            if bc0 == 1 and bc1 == 0:
                po[node_a*dof+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
                po[node_a*dof+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
                po[node_a*dof+2] += 0
                po[node_b*dof+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
                po[node_b*dof+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
                po[node_b*dof+2] += dl*cos*L**2/8
            if bc0 == 0 and bc1 == 1:
                po[node_a*dof+0] += dl*cos*sin*L*5/8 - dl*cos*sin*L/2
                po[node_a*dof+1] += -dl*cos**2*L*5/8 - dl*sin**2*L/2
                po[node_a*dof+2] += -dl*cos*L**2/8
                po[node_b*dof+0] += dl*cos*sin*L*3/8 - dl*cos*sin*L/2
                po[node_b*dof+1] += -dl*cos**2*L*3/8 - dl*sin**2*L/2
                po[node_b*dof+2] += 0
            if bc0 == 1 and bc1 == 1:
                po[node_a*dof+1] += -dl*L/2
                po[node_b*dof+1] += -dl*L/2    
        pZeros[0] = po           
        return pZeros

    def __str__(self):
        return str(self.node_start.getpa)

class Calculator():
    def __init__(self):
        self.nodes = Node.objects.all()
        self.elements = Element.objects.all()

    def run(self):
        return self.elements[0].node_start.x_coord * self.elements[0].node_start.y_coord