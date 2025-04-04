from django import forms
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username',
                'password1', 'password2']

class DateInput(forms.DateInput):
    input_type = 'date'


class DashboardForm(forms.Form):
    text = forms.CharField(max_length=100, label="Enter your search:")


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'description']


class HomeworkForm(forms.ModelForm):
    class Meta:
        model = Homework
        widgets = {'due': DateInput()}
        fields = ['subject', 'title', 'description', 'due', 'is_finished']

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo

        fields = ['title', 'is_finished']


class ConversionForm(forms.Form):
    CHOICES = [('length', 'Length'),
            ('mass', 'Mass')]

    measurement = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)



class ConversionLengthForm(forms.Form):
    value = forms.FloatField(label="Enter Value", required=True)
    measure1 = forms.ChoiceField(choices=[('Yard', 'Yard'), ('Foot', 'Foot')], required=True)
    measure2 = forms.ChoiceField(choices=[('Yard', 'Yard'), ('Foot', 'Foot')], required=True)

class ConversionMassForm(forms.Form):
    value = forms.FloatField(label="Enter Value", required=True)
    measure1 = forms.ChoiceField(choices=[('Pound', 'Pound'), ('Kilogram', 'Kilogram')], required=True)
    measure2 = forms.ChoiceField(choices=[('Pound', 'Pound'), ('Kilogram', 'Kilogram')], required=True)
