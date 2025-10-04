from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Project
import json

class ProjectKanbanView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/kanban.html'
    context_object_name = 'projects'

    def get_queryset(self):
        if self.request.user.is_director():
            return Project.objects.all()
        return Project.objects.filter(user=self.request.user)

@login_required
@require_http_methods(["POST"])
def update_project_status(request, pk):
    try:
        project = Project.objects.get(pk=pk)
        if request.user != project.user and not request.user.is_director():
            return JsonResponse({'error': 'Permission denied'}, status=403)

        data = json.loads(request.body)
        status = data.get('status')

        if status == 'completed':
            project.is_completed = True
        elif status in ['not_started', 'in_progress']:
            project.is_completed = False

        project.save()
        return JsonResponse({'status': 'success'})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)