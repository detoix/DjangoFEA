"""
Definition of views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from app.forms import NodeForm, ElementForm, LoadFormFactory, LoadForm
from app.models import Node, Element, Load, ConcentratedLoad, DistributedLoad, DistributedXLoad, Calculator
from django.http import HttpRequest
from datetime import datetime
import json

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #forms
    if request.method == "POST":
        nodeForm = NodeForm(request.POST)
        elementForm = ElementForm(request.POST)
        loadForm = LoadForm(request.POST)
        if request.POST.get('node') != None and nodeForm.is_valid():
            item = nodeForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('element') != None and elementForm.is_valid():
            item = elementForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('load') != None and loadForm.is_valid():
            loadForm = LoadFormFactory(request).make()
            item = loadForm.save(commit=False)
            item.author = request.user
            item.save()
        #elif request.POST.get('refresh') != None:
        #    value = Calculator().run()

    #entries
    if request.user.is_authenticated:
        nodes = Node.objects.filter(author=request.user).order_by('created_date')
        elements = Element.objects.filter(author=request.user).order_by('created_date')
        loads = Load.objects.filter(author=request.user).order_by('created_date')
        Calculator().calc()
    else:
        nodes = None
        elements = None
        loads = None

    #response
    return render(request, 'app/index.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
            'nodes':nodes,
            'elements':elements,
            'loads':loads,
            'nodeForm':NodeForm(),
            'elementForm':ElementForm(),
            'loadForm':LoadForm(),
            'dates':[obj.y for obj in nodes],
            'counts':[obj.x for obj in nodes],
            #'value':Calculator().run()
        })

def node_delete(request, pk):
    get_object_or_404(Node, pk=pk).delete()
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
