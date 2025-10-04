from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None

        # Get the view name from the function
        view_name = view_func.__name__.lower()

        # Director-only views
        director_only_views = ['adminsite']
        if any(view in view_name for view in director_only_views) and not request.user.is_director():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('projects:list')

        # Employee-only views (e.g., project creation)
        employee_only_views = ['projectcreate']
        if any(view in view_name for view in employee_only_views) and request.user.is_director():
            messages.error(request, "Directors cannot create projects.")
            return redirect('projects:list')

        return None