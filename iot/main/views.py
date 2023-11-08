from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Solar_Panel, Characteristics
import logging
from django.core.serializers import serialize

import json

from django.views.generic import TemplateView

def dashboard_char_table(request):
    solar_panels = Solar_Panel.objects.all()
    characteristics = Characteristics.objects.order_by('-date', '-time')[:5]

    dates = [char.date.strftime("%Y-%m-%d") for char in characteristics]
    generated_power = [char.generated_power for char in characteristics]
    consumed_power = [char.consumed_power for char in characteristics]
    
    context = {
        'characteristics': characteristics,
        'panels': solar_panels,
        'dates': json.dumps(dates),
        'generated_power': json.dumps(generated_power),
        'consumed_power': json.dumps(consumed_power),
    }

    return render(request, "dashboard.html", context)

def char_table(request):
    char = Characteristics.objects.order_by('-date', '-time') 
    return render(request, "table.html", {'characteristics': char})

def solar_panels(request):
    solar = Solar_Panel.objects.all()
    return render(request, "panels.html", {'panels': solar})

