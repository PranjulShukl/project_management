import django_filters
from .models import Project
from django import forms

class ProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(lookup_expr='icontains')
    company = django_filters.CharFilter(lookup_expr='icontains')
    is_submitted = django_filters.ChoiceFilter(
        choices=(('True', 'Submitted'), ('False', 'Not Submitted')),
        label='Submission Status'
    )

    class Meta:
        model = Project
        fields = ['name', 'category', 'company', 'is_submitted']

from django import forms
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()  # Correctly get the User model

class ProjectFilterForm(forms.Form):
    name = forms.CharField(required=False, label='Project Name')
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False)