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

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #forms
    if request.method == "POST":
        nodeForm = NodeForm(request.POST)
        sectionForm = SectionForm(request.POST)
        elementForm = ElementForm(request.POST)
        loadForm = ConcentratedLoadForm(request.POST)
        if request.POST.get('node') != None and nodeForm.is_valid():
            item = nodeForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('section') != None and sectionForm.is_valid():
            item = sectionForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('element') != None and elementForm.is_valid():
            item = elementForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('load') != None and loadForm.is_valid():
            item = loadForm.save(commit=False)
            item.author = request.user
            item.save()
        #elif request.POST.get('refresh') != None:
        #    value = Calculator().run()

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
        chart_data = { 'datasets': model_nodes + model_bars + Solver(request.user).solve() }
    else:
        nodes = None
        sections = None
        elements = None
        loads = None
        chart_data = None

    #response
    return render(request, 'app/index.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
            'nodes':nodes,
            'sections':sections,
            'elements':elements,
            'loads':loads,
            'nodeForm':NodeForm(),
            'sectionForm':SectionForm(),
            'elementForm':ElementForm(),
            'loadForm':ConcentratedLoadForm(),
            'chartData':json.dumps(chart_data),
        })

def node_delete(request, pk):
    get_object_or_404(Node, pk=pk).delete()
    return redirect('/')

def section_delete(request, pk):
    get_object_or_404(Section, pk=pk).delete()
    return redirect('/')

def element_delete(request, pk):
    get_object_or_404(Element, pk=pk).delete()
    return redirect('/')

def load_delete(request, pk):
    get_object_or_404(Load, pk=pk).delete()
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
