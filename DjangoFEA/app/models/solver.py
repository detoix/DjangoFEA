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

    def solve(self):
        dof = 3
        Neq = dof * len(self.nodes)

        K0 = np.zeros([Neq, Neq])
        P0 = np.zeros(Neq)

        for element in self.elements:
            K0 = element.assemble(K0)
            P0 = element.dead(P0)

        for load in self.loads:
            P0 = load.bc(P0)

        K = np.matrix.copy(K0)
        P = np.matrix.copy(P0)
        for node in self.nodes:
            [K0, P0] = node.bc(K0, P0)
        displacements = np.linalg.solve(K0,P0)
        reactions = np.dot(K, displacements)-P

        to_return = []
        for element in self.elements:
            associated_loads = ConcentratedLoad.objects.filter(author=self.user).filter(associated_element=element)
            xy = element.deflection(displacements, associated_loads)

            result2 = { 'data': xy, 'label': 'Results ' + str(element), 'fill': False }

            to_return.append(result2)
        return to_return

