"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest
from datetime import datetime
import json

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)

    #response
    return render(request, 'layout.html', 
        {
            'title':'Home Page',
            'year' :datetime.now().year,
        })