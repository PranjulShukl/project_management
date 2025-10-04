from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import Project, WorkLog

class WorkLogForm(forms.ModelForm):
    date = forms.DateField(
        label='Work Date',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'max': timezone.now().date().isoformat(),
            'required': True
        }),
        help_text='Select the date when the work was done'
    )
    
    description = forms.CharField(
        label='Work Description',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Example: Completed database schema design, started implementing user authentication...',
            'required': True
        }),
        help_text='Describe the tasks completed, progress made, and any challenges faced'
    )
    
    hours_worked = forms.DecimalField(
        label='Hours Worked',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.5',
            'min': '0.5',
            'max': '24',
            'placeholder': '8',
            'required': True
        }),
        help_text='Enter the number of hours worked (in 0.5 hour increments)',
        min_value=0.5,
        max_value=24,
        decimal_places=1
    )

    class Meta:
        model = WorkLog
        fields = ['date', 'description', 'hours_worked']

    def clean_date(self):
        date = self.cleaned_data['date']
        
        # Check if date is in the future
        if date > timezone.now().date():
            raise forms.ValidationError("You cannot log work for future dates.")

        # Check for existing work log on this date
        if self.project and self.user and not self.instance.pk:  # Only check on new work logs
            existing_log = WorkLog.objects.filter(
                project=self.project,
                user=self.user,
                date=date
            ).exists()
            if existing_log:
                raise forms.ValidationError(
                    "You have already logged work for this project on this date. "
                    "Please edit the existing log or choose a different date."
                )
        if date > timezone.now().date():
            raise forms.ValidationError("You cannot log work for future dates.")
        return date

    def __init__(self, *args, **kwargs):
        print("\n=== WorkLogForm.__init__ ===")
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)
        print(f"Initializing WorkLogForm - User: {self.user}, Project: {self.project}")
        super().__init__(*args, **kwargs)
        
        # Set up form field attributes
        self.fields['date'].widget.attrs.update({
            'class': 'form-control',
            'required': True,
            'max': timezone.now().date().isoformat()
        })
        
        self.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'rows': 4,
            'required': True,
            'placeholder': 'Describe the work done today'
        })
        
        self.fields['hours_worked'].widget.attrs.update({
            'class': 'form-control',
            'step': '0.5',
            'min': '0.5',
            'max': '24',
            'required': True
        })
        
        print("Form initialized successfully with fields:", self.fields.keys())

        if self.project:
            existing_log = WorkLog.objects.filter(
                project=self.project,
                user=self.user,
                date=timezone.now().date()
            ).first()
            if existing_log and not self.instance:
                raise forms.ValidationError(
                    "You have already logged work for this project today."
                )

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name',
            'category',
            'tender_award_date',
            'completion_date',
            'company',
            'location',
            'description',
        ]
        widgets = {
            'tender_award_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ProjectSubmitForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['is_submitted']
        widgets = {
            'is_submitted': forms.HiddenInput()
        }

class ProjectFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects...'
        })
    )
    
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by category'
        })
    )
    
    # Filter by submission status
    SUBMISSION_CHOICES = (
        ('', 'All'),
        ('submitted', 'Submitted'),
        ('not_submitted', 'Not Submitted'),
    )
    is_submitted = forms.ChoiceField(
        choices=SUBMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ClientFeedbackForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['client_feedback', 'client_confirmed_completed']
        widgets = {
            'client_feedback': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'client_confirmed_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }