from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from .views_kanban import ProjectKanbanView, update_project_status
from .models import Project, WorkLog
from .forms import ProjectForm, ProjectFilterForm, WorkLogForm
from .filters import ProjectFilter

from django.contrib.auth import get_user_model
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Project
from .filters import ProjectFilter, ProjectFilterForm

User = get_user_model()






class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10

    def get_queryset(self):
        queryset = Project.objects.all() if self.request.user.is_director() else Project.objects.filter(user=self.request.user)
        self.filterset = ProjectFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        context['filter_form'] = ProjectFilterForm(self.request.GET)
        # include users list for director filter dropdown
        if self.request.user.is_director():
            context['users'] = User.objects.all()
        return context


import django_filters
from .models import Project

class ProjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Project Name')
    user = django_filters.ModelChoiceFilter(queryset=None, label='User')

    class Meta:
        model = Project
        fields = ['name', 'user']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set user queryset for filter
        from django.contrib.auth import get_user_model
        self.filters['user'].queryset = get_user_model().objects.all()

    

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

@login_required
@require_POST
def submit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.user != project.user and not request.user.is_director():
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    project.is_submitted = True
    project.submission_date = timezone.now()  # set submission timestamp

    project.save()
    return JsonResponse({'status': 'success', 'message': 'Project submitted successfully!'})

class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'
    success_url = reverse_lazy('projects:list')
    
    def test_func(self):
        return not self.request.user.is_director()
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Project created successfully!')
        return super().form_valid(form)

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/project_form.html'  # Changed to project_form.html
    context_object_name = 'project'
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.user and not project.is_submitted
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        context.update({
            'is_edit_mode': True,
            'work_logs': project.work_logs.select_related('user').order_by('-date', '-created_at'),
            'work_log_form': WorkLogForm(
                initial={
                    'date': timezone.now().date(),
                    'hours_worked': 8.0,
                },
                project=project,
                user=self.request.user
            )
        })
        return context
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def dispatch(self, request, *args, **kwargs):
        print("\n=== ProjectDetailView.dispatch ===")
        print(f"Request method: {request.method}")
        print(f"Request path: {request.path}")
        print(f"User: {request.user}")
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        project = self.get_object()
        return self.request.user.is_director() or self.request.user == project.user

    def get_context_data(self, **kwargs):
        print("\n=== ProjectDetailView.get_context_data ===")
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        print(f"Project: {project}")
        print(f"User: {self.request.user}")
        
        context.update({
            'work_logs': project.work_logs.select_related('user').order_by('-date', '-created_at'),
            'work_log_form': WorkLogForm(
                initial={
                    'date': timezone.now().date(),
                    'hours_worked': 8.0,
                },
                project=project,
                user=self.request.user
            ),
            'is_edit_mode': False  # This is view mode, not edit mode
        })
        work_log_form = WorkLogForm(
            initial={
                'date': timezone.now().date(),
                'hours_worked': 8.0,
            },
            project=project,
            user=self.request.user
        )
        print("Work log form created successfully")
        
        context.update({
            'work_logs': project.work_logs.select_related('user').order_by('-date', '-created_at'),
            'work_log_form': work_log_form,
            'debug': True
        })
        
        print("\nContext keys:", list(context.keys()))
        return context

    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if not project.is_submitted and request.user == project.user:
            project.is_submitted = True
            project.save()
            messages.success(request, 'Project submitted successfully!')
        return redirect('projects:detail', pk=project.pk)

class WorkLogCreateView(LoginRequiredMixin, CreateView):
    model = WorkLog
    form_class = WorkLogForm
    template_name = 'projects/work_log_form.html'

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs['project_pk'])

    def is_ajax(self):
        return self.request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['project'] = self.get_project()
        return kwargs

    def form_valid(self, form):
        project = self.get_project()

        # Permission check
        if not (self.request.user.is_director() or self.request.user == project.user):
            if self.is_ajax():
                return JsonResponse({'error': 'Permission denied'}, status=403)
            messages.error(self.request, 'Permission denied')
            return redirect('projects:detail', pk=project.pk)

        # Set instance attributes
        form.instance.project = project
        form.instance.user = self.request.user
        self.object = form.save()

        # AJAX request → return JSON
        if self.is_ajax():
            html = render_to_string(
                'projects/work_log_item.html',
                {'work_log': self.object, 'is_edit_mode': True},
                request=self.request
            )
            return JsonResponse({
                'status': 'success',
                'html': html,
                'message': 'Work log added successfully!'
            })

        # Non-AJAX → redirect back to same project detail page
        messages.success(self.request, 'Work log added successfully!')
        return redirect('projects:detail', pk=project.pk)

    def form_invalid(self, form):
        project = self.get_project()
        if self.is_ajax():
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
        messages.error(self.request, 'There were errors in the form. Please correct them.')
        return redirect('projects:detail', pk=project.pk)


    def form_invalid(self, form):
        print("\n=== WorkLogCreateView.form_invalid ===")
        print(f"Form errors: {form.errors}")
        if self.is_ajax():
            error_data = {field: errors[0] for field, errors in form.errors.items()}
            # Check for unique constraint violation
            if 'date' in error_data and "already logged work" in str(error_data['date']):
                status_code = 409  # Conflict
            else:
                status_code = 400  # Bad Request
                
            print(f"Returning JSON error response: {error_data}")
            return JsonResponse({
                'status': 'error',
                'error': error_data
            }, status=status_code)
        return super().form_invalid(form)

    def get_template_names(self):
        if self.is_ajax():
            return ['projects/work_log_form_inner.html']
        return [self.template_name]



class ProjectSubmitView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    fields = []  # No fields to edit, just updating is_submitted
    http_method_names = ['post']  # Only allow POST requests
    
    def test_func(self):
        project = self.get_object()
        return self.request.user == project.user and not project.is_submitted
    
    def form_valid(self, form):
        project = form.instance
        project.is_submitted = True
        messages.success(self.request, 'Project submitted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.project.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)

# Remove this duplicate ProjectDetailView class as we already have one above

# views.py

# views.py
from django.views.generic import UpdateView, DetailView
from django.views import View
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Project
from .forms import ClientFeedbackForm


# class SendFeedbackRequestView(View):
#     """Send an email to client with feedback link."""
#     def get(self, request, pk):
#         project = get_object_or_404(Project, pk=pk, user=request.user)
#         if project.client_email:
#             feedback_url = request.build_absolute_uri(
#                 reverse('projects:client_feedback', args=[project.pk])
#             )
#             send_mail(
#                 subject=f"Feedback Request for Project: {project.name}",
#                 message=f"Please provide your feedback for the project here: {feedback_url}",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 recipient_list=[project.client_email],
#             )
#             messages.success(request, "Feedback request sent to client.")
#         return redirect('projects:detail', pk=pk)
from django.views import View
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import FeedbackToken

class SendFeedbackRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk, user=request.user)
        if not project.client_email:
            return JsonResponse({'status': 'error', 'message': 'Client email not set.'}, status=400)

        # Create a one-time token
        fb_token = FeedbackToken.objects.create(project=project)

        feedback_url = request.build_absolute_uri(
            reverse('projects:client_feedback_token', args=[str(fb_token.token)])
        )

        send_mail(
            subject=f"Feedback request for project: {project.name}",
            message=f"Please provide feedback here: {feedback_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[project.client_email],
            fail_silently=False,
        )

        return JsonResponse({'status': 'success', 'message': 'Feedback request sent to client.'})



# class ClientFeedbackView(UpdateView):
#     """Form where client can submit feedback."""
#     model = Project
#     form_class = ClientFeedbackForm
#     template_name = "projects/client_feedback.html"
#     context_object_name = "project"

#     def form_valid(self, form):
#         messages.success(self.request, "Thank you for your feedback!")
#         return super().form_valid(form)

#     def get_success_url(self):
#         return reverse('projects:client_feedback', args=[self.object.pk])


from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import UpdateView
from django.contrib import messages
from .models import FeedbackToken, Project
from .forms import ClientFeedbackForm

class ClientFeedbackTokenView(UpdateView):
    template_name = "projects/client_feedback.html"
    form_class = ClientFeedbackForm
    model = Project
    context_object_name = "project"

    def dispatch(self, request, *args, **kwargs):
        self.token_obj = get_object_or_404(FeedbackToken, token=kwargs['token'])
        if self.token_obj.used:
            messages.error(request, "This feedback link has already been used.")
            return render(request, "projects/feedback_expired.html")
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return self.token_obj.project

    def form_valid(self, form):
        messages.success(self.request, "Thank you for your feedback!")
        self.token_obj.mark_used()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:feedback_thank_you')

def feedback_thank_you(request):
    return render(request, "projects/feedback_thank_you.html")





# views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import Project, WorkLog


# --- Timeline View (All Projects) ---
class ProjectTimelineView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/timeline.html'
    context_object_name = 'projects'

    def get_queryset(self):
        if hasattr(self.request.user, 'is_director') and self.request.user.is_director():
            queryset = Project.objects.all()
        else:
            queryset = Project.objects.filter(user=self.request.user)
        return queryset.order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projects = self.get_queryset()

        # Calculate total effort for each project
        for project in projects:
            total_hours = project.work_logs.aggregate(total=Sum('hours_worked'))['total'] or 0
            project.total_hours = total_hours

            # Active days
            active_days = project.work_logs.values('date').distinct().count()
            project.active_days = active_days

            # Days left until completion
            project.days_left = (project.completion_date - timezone.now().date()).days if project.completion_date else None

        context['today'] = timezone.now().date()
        return context


# --- Dashboard View (Single Project) ---
def project_dashboard(request, project_id):
    print("DEBUG: project_dashboard called with project_id =", project_id)
    project = get_object_or_404(Project, id=project_id)

    logs = WorkLog.objects.filter(project=project)

    total_hours = logs.aggregate(total=Sum('hours_worked'))['total'] or 0
    active_days = logs.values('date').distinct().count()
    avg_daily_hours = (total_hours / active_days) if active_days else 0

    workload_by_user = logs.values('user__username').annotate(total=Sum('hours_worked'))
    daily_trend = logs.values('date').annotate(total=Sum('hours_worked')).order_by('date')

    cumulative = []
    running_total = 0
    for d in daily_trend:
        running_total += float(d['total'])
        cumulative.append({'date': d['date'], 'cumulative': running_total})

    idle_days = []
    if logs.exists():
        dates = sorted(set([l.date for l in logs]))
        for i in range(1, len(dates)):
            gap = (dates[i] - dates[i-1]).days - 1
            if gap > 0:
                idle_days.append({'from': dates[i-1] + timedelta(days=1),
                                  'to': dates[i] - timedelta(days=1),
                                  'days': gap})

    days_left = (project.completion_date - timezone.now().date()).days if project.completion_date else None

    context = {
        "project": project,
        "total_hours": total_hours,
        "avg_daily_hours": round(avg_daily_hours, 1),
        "active_days": active_days,
        "days_left": days_left,
        "workload_by_user": list(workload_by_user),
        "daily_trend": list(daily_trend),
        "cumulative": cumulative,
        "idle_days": idle_days,
    }
    return render(request, "projects/dashboard.html", context)
