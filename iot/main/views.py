from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Solar_Panel, Characteristics
import logging

def dashboard_char_table(request):
    solar = Solar_Panel.objects.all()
    char = Characteristics.objects.order_by('-date', '-time')[:5]
    return render(request, "dashboard.html", {'characteristics': char, 'panels':solar})

def char_table(request):
    char = Characteristics.objects.order_by('-date', '-time') 
    return render(request, "table.html", {'characteristics': char})

def solar_panels(request):
    solar = Solar_Panel.objects.all()
    return render(request, "panels.html", {'panels': solar})