class ResultsProvider():
    def execute(self, element, displacements, associated_loads, nodes):
        pass

class VoidResultsProvider(ResultsProvider):
    def execute(self, element, displacements, associated_loads, nodes):
        return []

class DeflectionResultsProvider(ResultsProvider):
    def execute(self, element, displacements, associated_loads, nodes):
        return element.calculate_deflection(displacements, associated_loads, nodes)

class BendingResultsProvider(ResultsProvider):
    def execute(self, element, displacements, associated_loads, nodes):
        return element.calculate_bending(displacements, associated_loads, nodes)

class ShearResultsProvider(ResultsProvider):
    def execute(self, element, displacements, associated_loads, nodes):
        return element.calculate_shear(displacements, associated_loads, nodes)

class AxialResultsProvider(ResultsProvider):
    def execute(self, element, displacements, associated_loads, nodes):
        return element.calculate_axial(displacements, associated_loads, nodes)
