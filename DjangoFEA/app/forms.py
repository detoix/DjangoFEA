"""
Definition of forms.
"""

from django import forms
from app.models import Node, Element, Load, ConcentratedLoad, DistributedLoad, DistributedXLoad
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
    x = forms.FloatField(initial=0)
    y = forms.FloatField(initial=0)
    x_boundary_condition = forms.BooleanField(required=False)
    y_boundary_condition = forms.BooleanField(required=False)
    fi_boundary_condition = forms.BooleanField(required=False)

    class Meta:
        model = Node
        fields = ('x', 'y', 'x_boundary_condition', 'y_boundary_condition', 'fi_boundary_condition')

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

class LoadFormFactory():
     def __init__(self, request):
        self.request = request
        self.type = request.POST.get('type')

     def make(self):
        if self.type == "0":
            return ConcentratedLoadForm(self.request.POST)
        if self.type == "1":
            return DistributedLoadForm(self.request.POST)
        if self.type == "2":
            return DistributedXLoadForm(self.request.POST)

class LoadForm(forms.ModelForm):
    type = forms.ChoiceField(choices=[('0','concentrated'),  ('1','distributed'), ('2', 'distributed x')])
    nature = forms.ChoiceField(choices= [('0','constant'), ('1','variable')])
    group = forms.IntegerField(initial=0)
    associated_element = forms.ModelChoiceField(queryset = Element.objects.all())
    f1 = forms.FloatField(initial=0)
    f2 = forms.FloatField(initial=0)
    coord1 = forms.FloatField(initial=0)
    coord2 = forms.FloatField(initial=0)
    m = forms.FloatField(initial=0)
    deg = forms.FloatField(initial=0)

    class Meta:
        model = Load
        fields = ('type', 'nature', 'group', 'associated_element', 'f1', 'f2', 'coord1', 'coord2', 'm', 'deg')

class ConcentratedLoadForm(LoadForm):
    class Meta:
        model = ConcentratedLoad
        fields = LoadForm.Meta.fields

class DistributedLoadForm(LoadForm):
    class Meta:
        model = DistributedLoad
        fields = LoadForm.Meta.fields

class DistributedXLoadForm(LoadForm):
    class Meta:
        model = DistributedLoad
        fields = LoadForm.Meta.fields