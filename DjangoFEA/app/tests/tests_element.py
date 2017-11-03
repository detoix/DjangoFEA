import django
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