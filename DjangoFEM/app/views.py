"""
Definition of views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from app.forms import NodeForm, ElementForm
from app.models import Node, Element, Calculator
from django.http import HttpRequest
from datetime import datetime

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #form
    if request.method == "POST":
        nodeForm = NodeForm(request.POST)
        elementForm = ElementForm(request.POST)
        if request.POST.get('node') != None and nodeForm.is_valid():
            item = nodeForm.save(commit=False)
            item.author = request.user
            item.save()
        elif request.POST.get('element') != None and elementForm.is_valid():
            item = elementForm.save(commit=False)
            item.author = request.user
            item.save()
        #elif request.POST.get('refresh') != None:
        #    value = Calculator().run()

    #entries
    if request.user.is_authenticated:
        nodes = Node.objects.filter(author=request.user).order_by('created_date')
        elements = Element.objects.filter(author=request.user).order_by('created_date')
    else:
        nodes = None
        elements = None

    #response
    return render(request, 'app/index.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
            'nodes':nodes,
            'elements':elements,
            'nodeForm':NodeForm(),
            'elementForm':ElementForm(),
            #'value':Calculator().run()
        })

def node_delete(request, pk):
    get_object_or_404(Node, pk=pk).delete()
    return redirect('/')

def element_delete(request, pk):
    get_object_or_404(Element, pk=pk).delete()
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
