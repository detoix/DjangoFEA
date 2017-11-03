import numpy as np
import math as math
from app.models import Node, Element, ConcentratedLoad

class Solver():
    def __init__(self, user):
        self.user = user
        self.nodes = list(Node.objects.filter(author=user).order_by('created_date'))
        self.elements = Element.objects.filter(author=user).order_by('created_date')
        self.loads = ConcentratedLoad.objects.filter(author=user).order_by('created_date')

    def solve(self, results_provider):
        dof = 3
        Neq = dof * len(self.nodes)

        K0 = np.zeros([Neq, Neq])
        P0 = np.zeros(Neq)

        for element in self.elements:
            K0 = element.append_to_global_stiffness_matrix(K0, self.nodes)
            P0 = element.append_dead_load_to_force_matrix(P0, self.nodes)

        for load in self.loads:
            P0 = load.append_to_force_matrix(P0, self.nodes)

        K = np.matrix.copy(K0)
        P = np.matrix.copy(P0)
        for node in self.nodes:
            [K0, P0] = node.bc(K0, P0, self.nodes)
        displacements = np.linalg.solve(K0,P0)
        reactions = np.dot(K, displacements)-P

        result = []
        for element in self.elements:
            associated_loads = self.loads.filter(associated_element=element)
            xy = results_provider.execute(element, displacements, associated_loads, self.nodes)
            result.append({ 'data': xy, 'label': 'Results ' + str(element.id), 'fill': False })
        return result