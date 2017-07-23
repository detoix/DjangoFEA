"""
Definition of forms.
"""

from django import forms
from app.models import Node, Section, Element, Load, ConcentratedLoad, DistributedLoad, DistributedXLoad
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
    x = forms.FloatField(label="")
    y = forms.FloatField(label="")
    x_boundary_condition = forms.BooleanField(required=False, label="")
    y_boundary_condition = forms.BooleanField(required=False, label="")
    fi_boundary_condition = forms.BooleanField(required=False, label="")

    class Meta:
        model = Node
        fields = ('x', 'y', 'x_boundary_condition', 'y_boundary_condition', 'fi_boundary_condition')

class SectionForm(forms.ModelForm):
    E = forms.FloatField(label="")
    A = forms.FloatField(label="")
    J = forms.FloatField(label="")
    ro = forms.FloatField(label="")

    class Meta:
        model = Section
        fields = ('E', 'A', 'J', 'ro')

class ElementForm(forms.ModelForm):
    section = forms.ModelChoiceField(queryset = Section.objects.all(), label="")
    node_start = forms.ModelChoiceField(queryset = Node.objects.all(), label="")
    node_end = forms.ModelChoiceField(queryset = Node.objects.all(), label="")
    hinge_start = forms.BooleanField(required=False, label="")
    hinge_end = forms.BooleanField(required=False, label="")

    class Meta:
        model = Element
        fields = ('section', 'node_start', 'node_end', 'hinge_start', 'hinge_end')

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
    #type = forms.ChoiceField(choices=[('0','concentrated'),  ('1','distributed'), ('2', 'distributed x')], label="")
    associated_element = forms.ModelChoiceField(queryset = Element.objects.all(), label="")
    f1 = forms.FloatField(label="")
    coord1 = forms.FloatField(label="")
    m = forms.FloatField(label="")
    deg = forms.FloatField(label="")

    class Meta:
        model = Load
        fields = ('associated_element', 'f1', 'coord1', 'm', 'deg')

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
