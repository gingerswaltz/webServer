from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from .models import Reading
from .models import Ip
import matplotlib.pyplot as plt
from datetime import datetime
import logging


def index(request):
    readings = Reading.objects.all()
    context = {'readings': readings}
    return render(request, 'main/index.html', context)


def about(request):
    return render(request, 'main/about.html')


# def reading(request):
#     return render(request, 'main/reading_list.html')

class ReadingDeleteView(DeleteView):
    model = Reading
    success_url = '/'
    template_name = 'main/reading_confirm_delete.html'

    # class Meta:
    #     model = Reading
    #     fields = ['installation_number', 'date', 'time', 'generated_power', 'consumed_power', 'vertical_position',
    #               'horizontal_position', 'additional_field']
    #
    # def form_valid(self, form):
    #     additional_field_value = form.cleaned_data.get('additional_field')
    #     reading = form.save(commit=False)
    #     reading.additional_field = additional_field_value
    #     reading.save()
    #     return super().form_valid(form)
    #
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['additional_field_value'] = self.request.POST.get('additional_field')
    #     return kwargs


class ReadingListView(ListView):
    model = Reading


class ReadingForm(forms.ModelForm):
    # additional_field = forms.CharField(label="Additional Field")

    class Meta:
        model = Reading
        fields = ['installation_number', 'date', 'time', 'generated_power', 'consumed_power', 'vertical_position',
                  'horizontal_position']


logger = logging.getLogger(__name__)


class ReadingCreateView(CreateView):
    model = Reading
    form_class = ReadingForm
    template_name = 'main/reading_form.html'
    success_url = '/'


def form_valid(self, form):
    # Получение значения из формы
    installation_number = form.cleaned_data['installation_number']
    date = form.cleaned_data['date']
    time = form.cleaned_data['time']
    generated_power = form.cleaned_data['generated_power']
    consumed_power = form.cleaned_data['consumed_power']
    vertical_position = form.cleaned_data['vertical_position']
    horizontal_position = form.cleaned_data['horizontal_position']

    # Проверка наличия записи или создание новой
    obj, created = Reading.objects.get_or_create(
        installation_number=installation_number,
        date=date,
        time=time,
        generated_power=generated_power,
        consumed_power=consumed_power,
        vertical_position=vertical_position,
        horizontal_position=horizontal_position
    )

    return super(Reading, self).form_valid(form)


class ReadingUpdateView(UpdateView):
    model = Reading
    form_class = ReadingForm
    success_url = '/'
    template_name = 'main/reading_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action'] = 'Изменить'
        return context




def graphics(request):
    readings = Reading.objects.all() # Получение данных из базы данных
    context = {'readings': readings}
    return render(request, 'main/graphics.html', context)

#
# # Разделение данных на различные списки
# dates = [reading.date for reading in readings]
# times = [datetime.combine(reading.date, reading.time) for reading in readings]
# generated_power = [reading.generated_power for reading in readings]
# consumed_power = [reading.consumed_power for reading in readings]
#
# # График вырабатываемой мощности в зависимости от даты и времени
# plt.figure(figsize=(12, 6))
# plt.plot(times, generated_power, label='Вырабатываемая мощность')
# plt.xlabel('Дата и время')
# plt.ylabel('Мощность')
# plt.title('Вырабатываемая мощность')
# plt.legend()
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()
#
# # График потребляемой мощности в зависимости от даты и времени
# plt.figure(figsize=(12, 6))
# plt.plot(times, consumed_power, label='Потребляемая мощность')
# plt.xlabel('Дата и время')
# plt.ylabel('Мощность')
# plt.title('Потребляемая мощность')
# plt.legend()
# plt.xticks(rotation=45)
# plt.grid(True)
# plt.show()

