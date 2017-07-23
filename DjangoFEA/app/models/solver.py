import numpy as np
import math as math
from app.models import Node, Element, ConcentratedLoad

class Solver():
    def __init__(self):
        self.nodes = Node.objects.all()
        self.elements = Element.objects.all()
        self.loads = ConcentratedLoad.objects.all()

    def run(self):
        return self.loads[0].abc()

    #calculate displacements
    '''The function acts as follows:
        1. 
        '''

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

        for element in self.elements:
            xy = element.deflection(displacements)
        return xy

