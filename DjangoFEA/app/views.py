"""
Definition of views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.core import serializers
from app.forms import NodeForm, SectionForm, ElementForm, ConcentratedLoadForm
from app.models import Node, Section, Element, Load, ConcentratedLoad, DistributedLoad, DistributedXLoad, Solver
from django.http import HttpRequest
from datetime import datetime
import json

def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

def get_type_by_string(object_type):
    if object_type == 'node':
        return Node, NodeForm
    elif object_type == 'section':
        return Section, SectionForm
    elif object_type == 'element':
        return Element, ElementForm
    elif object_type == 'load':
        return ConcentratedLoad, ConcentratedLoadForm
    else:
        return None, None

def deflection(request):
    return home(request, dt=Solver(request.user).solve(0))

def bending(request):
    return home(request, dt=Solver(request.user).solve(1))

def shear(request):
    return home(request, dt=Solver(request.user).solve(2))

def axial(request):
    return home(request, dt=Solver(request.user).solve(3))

def home(request, dt = [], node_pk = None, section_pk = None, element_pk = None, concentrated_load_pk = None):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #entries
    if request.user.is_authenticated:
        nodes = Node.objects.filter(author=request.user).order_by('created_date')
        sections = Section.objects.filter(author=request.user).order_by('created_date')
        elements = Element.objects.filter(author=request.user).order_by('created_date')
        loads = ConcentratedLoad.objects.filter(author=request.user).order_by('created_date')
        model_nodes = [{ 'data': 
                            [{ 'x': obj.x, 'y': obj.y} for obj in nodes], 
                         'label': "Nodes", 
                         'lineTension': 0,
                         'fill': False,
                         'pointStyle': 'triangle',
                         'pointRadius': 10,
                         'showLine': False }]
        model_bars = [{ 'data': 
                            [{ 'x': obj.node_start.x, 'y': obj.node_start.y},
                             { 'x': obj.node_end.x, 'y': obj.node_end.y}], 
                        'label': 'Bar ' + str(obj),
                        'lineTension': 0,
                        'fill': False } for obj in elements]
        chart_data = { 'datasets': model_nodes + model_bars + dt }
    else:
        nodes = None
        sections = None
        elements = None
        loads = None
        chart_data = None

    edited_node = get_object_or_none(Node, pk=node_pk)
    if edited_node != None:
        nodeForm = NodeForm(instance = edited_node)
    else:
        nodeForm = NodeForm()

    edited_section = get_object_or_none(Section, pk=section_pk)
    if edited_section != None:
        sectionForm = SectionForm(instance = edited_section)
    else:
        sectionForm = SectionForm()

    edited_element = get_object_or_none(Element, pk=element_pk)
    if edited_element != None:
        elementForm = ElementForm(instance = edited_element)
    else:
        elementForm = ElementForm()

    edited_concentrated_load = get_object_or_none(ConcentratedLoad, pk=element_pk)
    if edited_concentrated_load != None:
        concentratedLoadForm = ConcentratedLoadForm(instance = edited_concentrated_load)
    else:
        concentratedLoadForm = ConcentratedLoadForm()
    
    #response
    return render(request, 'app/index.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
            'nodes':nodes,
            'sections':sections,
            'elements':elements,
            'concentrated_loads':loads,
            'nodeForm':nodeForm,
            'emptyNodeForm':NodeForm(),
            'sectionForm':sectionForm,
            'emptySectionForm':SectionForm(),
            'elementForm':elementForm,
            'emptyElementForm':ElementForm(),
            'concentratedLoadForm':concentratedLoadForm,
            'emptyConcentratedLoadForm':ConcentratedLoadForm(),
            'chartData':json.dumps(chart_data),
        })

def item_delete(request, item_type, pk):
    object_type, associated_form = get_type_by_string(item_type)
    if object_type != None:
        get_object_or_404(object_type, pk=pk).delete()
    return redirect('/')

def item_new(request, item_type):
    object_type, associated_form = get_type_by_string(item_type)
    if object_type != None and associated_form != None and request.user.is_authenticated and request.method == "POST":
        if associated_form(request.POST).is_valid():
            item = associated_form(request.POST).save(commit=False)
            item.author = request.user
            item.save()
    return redirect('/')

def item_edit(request, item_type, pk):
    object_type, associated_form = get_type_by_string(item_type)
    if object_type != None and associated_form != None and request.user.is_authenticated and request.method == "POST":
        if associated_form(request.POST).is_valid():
            edited = get_object_or_none(object_type, pk=pk)
            if edited != None:
                item = associated_form(request.POST, instance = edited).save(commit=False)
                item.author = request.user
                item.save()
                return redirect('/')

    if item_type == 'node':
        return home(request, node_pk = pk)
    elif item_type == 'section':
        return home(request, section_pk = pk)
    elif item_type == 'element':
        return home(request, element_pk = pk)
    elif item_type == 'load':
        return home(request, concentrated_load_pk = pk)
    else:
        return redirect('/')

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        }
    )
