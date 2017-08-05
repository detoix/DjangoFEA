import numpy as np
import math as math
from app.models import Node, Element, ConcentratedLoad

class Solver():
    def __init__(self, user):
        self.user = user
        self.nodes = Node.objects.filter(author=user).order_by('created_date')
        self.elements = Element.objects.filter(author=user).order_by('created_date')
        self.loads = ConcentratedLoad.objects.filter(author=user).order_by('created_date')

    def run(self):
        return self.loads[0].abc()

    #calculate displacements
    '''The function acts as follows:
        1. 
        '''

    def solve(self, expected_result):
        dof = 3
        Neq = dof * len(self.nodes)

        K0 = np.zeros([Neq, Neq])
        P0 = np.zeros(Neq)

        for element in self.elements:
            K0 = element.assemble_stiffness_matrix(K0)
            P0 = element.append_dead_load_to_force_matrix(P0)

        for load in self.loads:
            P0 = load.append_to_force_matrix(P0)

        K = np.matrix.copy(K0)
        P = np.matrix.copy(P0)
        for node in self.nodes:
            [K0, P0] = node.bc(K0, P0)
        displacements = np.linalg.solve(K0,P0)
        reactions = np.dot(K, displacements)-P

        result = []
        for element in self.elements:
            associated_loads = self.loads.filter(associated_element=element)
            if expected_result == 0:
                xy = element.calculate_deflection(displacements, associated_loads)
            elif expected_result == 1:
                xy = element.calculate_bending(displacements, associated_loads)
            elif expected_result == 2:
                xy = element.calculate_shear(displacements, associated_loads)
            elif expected_result == 3:
                xy = element.calculate_axial(displacements, associated_loads)
            result.append({ 'data': xy, 'label': 'Results ' + str(element), 'fill': False })
        return result