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

def get_type_by_string(item_type):
    if item_type == 'node':
        return Node, NodeForm
    elif item_type == 'section':
        return Section, SectionForm
    elif item_type == 'element':
        return Element, ElementForm
    elif item_type == 'load':
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

def home(request, dt = [], node_pk = None, section_pk = None):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #forms
    if request.user.is_authenticated and request.method == "POST":

        sectionForm = SectionForm(request.POST)
        elementForm = ElementForm(request.POST)
        loadForm = ConcentratedLoadForm(request.POST)

        
        if request.POST.get('element') != None and elementForm.is_valid():
            item = ElementForm(request.POST).save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('load') != None and loadForm.is_valid():
            item = ConcentratedLoadForm(request.POST).save(commit=False)
            item.author = request.user
            item.save()

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
    
    #response
    return render(request, 'app/index.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
            'nodes':nodes,
            'sections':sections,
            'elements':elements,
            'loads':loads,
            'nodeForm':nodeForm,
            'emptyNodeForm':NodeForm(),
            'sectionForm':sectionForm,
            'emptySectionForm':SectionForm(),
            'elementForm':ElementForm(),
            'loadForm':ConcentratedLoadForm(),
            'chartData':json.dumps(chart_data),
        })

def item_delete(request, item_type, pk):
    item_type, associated_form = get_type_by_string(item_type)
    if item_type != None:
        get_object_or_404(item_type, pk=pk).delete()
    return redirect('/')

def item_new(request, item_type):
    item_type, associated_form = get_type_by_string(item_type)
    if item_type != None and associated_form != None and request.user.is_authenticated and request.method == "POST":
        if associated_form(request.POST).is_valid():
            item = associated_form(request.POST).save(commit=False)
            item.author = request.user
            item.save()
    return redirect('/')

def node_edit(request, pk):
    if request.user.is_authenticated and request.method == "POST":
        nodeForm = NodeForm(request.POST)
        if request.POST.get('edit_node') != None and nodeForm.is_valid():
            edited = get_object_or_none(Node, pk=pk)
            if edited != None:
                item = NodeForm(request.POST, instance = edited).save(commit=False)
                item.author = request.user
                item.save()
                return redirect('/')
    return home(request, node_pk = pk)

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
