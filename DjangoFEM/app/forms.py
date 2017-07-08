"""
Definition of forms.
"""

from django import forms
from app.models import Node, Element
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))

class NodeForm(forms.ModelForm):
    x_coord = forms.FloatField(initial=0)
    y_coord = forms.FloatField(initial=0)
    x_boundary_condition = forms.BooleanField(required=False)
    y_boundary_condition = forms.BooleanField(required=False)
    fi_boundary_condition = forms.BooleanField(required=False)

    class Meta:
        model = Node
        fields = ('x_coord', 'y_coord', 'x_boundary_condition', 'y_boundary_condition', 'fi_boundary_condition')

class ElementForm(forms.ModelForm):
    E = forms.FloatField(initial=0)
    A = forms.FloatField(initial=0)
    J = forms.FloatField(initial=0)
    ro = forms.FloatField(initial=0)
    node_start = forms.ModelChoiceField(queryset = Node.objects.all())
    node_end = forms.ModelChoiceField(queryset = Node.objects.all())
    hinge_start = forms.BooleanField(required=False)
    hinge_end = forms.BooleanField(required=False)

    class Meta:
        model = Element
        fields = ('E', 'A', 'J', 'ro', 'node_start', 'node_end', 'hinge_start', 'hinge_end')