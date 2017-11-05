import django as django
from django.test import TestCase

class ElementModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        django.setup()

    def test_frame_element_gets_valid_state(self):
        from ..models import Element

        element = Element(hinge_start = False, hinge_end = False).set_hinges_state()

        self.assertEqual(element.calculate_B_partial_matrix, element.calculate_B_partial_matrix_frame_element)
        self.assertEqual(element.calculate_C_partial_matrix, element.calculate_C_partial_matrix_frame_element)
        self.assertEqual(element.calculate_D_partial_matrix, element.calculate_D_partial_matrix_frame_element)

    def test_start_hinge_element_gets_valid_state(self):
        from ..models import Element

        element = Element(hinge_start = True, hinge_end = False).set_hinges_state()

        self.assertEqual(element.calculate_B_partial_matrix, element.calculate_B_partial_matrix_left_hinge)
        self.assertEqual(element.calculate_C_partial_matrix, element.calculate_C_partial_matrix_left_hinge)
        self.assertEqual(element.calculate_D_partial_matrix, element.calculate_D_partial_matrix_left_hinge)

    def test_end_hinge_element_gets_valid_state(self):
        from ..models import Element

        element = Element(hinge_start = False, hinge_end = True).set_hinges_state()

        self.assertEqual(element.calculate_B_partial_matrix, element.calculate_B_partial_matrix_right_hinge)
        self.assertEqual(element.calculate_C_partial_matrix, element.calculate_C_partial_matrix_right_hinge)
        self.assertEqual(element.calculate_D_partial_matrix, element.calculate_D_partial_matrix_right_hinge)

    def test_truss_element_gets_valid_state(self):
        from ..models import Element

        element = Element(hinge_start = True, hinge_end = True).set_hinges_state()

        self.assertEqual(element.calculate_B_partial_matrix, element.calculate_B_partial_matrix_truss_element)
        self.assertEqual(element.calculate_C_partial_matrix, element.calculate_C_partial_matrix_truss_element)
        self.assertEqual(element.calculate_D_partial_matrix, element.calculate_D_partial_matrix_truss_element)

    def test_calculate_B_partial_matrix_frame_element(self):
        from ..models import Node, Section, Element
        import numpy as np
        import math as math

        element = Element(
            section = Section(E = 12.05, A = 10.9, J = 130.4),
            node_start = Node(x = 2, y = 4.5),
            node_end = Node(x = 8.5, y = 3)).calculate_B_partial_matrix_frame_element()

        l = math.hypot(element.node_end.x - element.node_start.x, element.node_end.y - element.node_start.y)
        expected = np.matrix([[(10.9 / 10000) / (130.4 / 100000000), 0, 0],
                              [0, 12 / l ** 2, - 6 / l],
                              [0, - 6 / l, 4]]) * (12.05 * 100000000) * (130.4 / 100000000) / l

        self.assertTrue(np.array_equal(element.B, expected))