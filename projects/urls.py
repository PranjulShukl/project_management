from django.urls import path
from . import views
# from .views_timeline import ProjectTimelineView
from .views import SendFeedbackRequestView, ClientFeedbackTokenView, feedback_thank_you
from .views import ProjectTimelineView, project_dashboard

app_name = 'projects'
print("DEBUG: Imported views:", ProjectTimelineView, project_dashboard)
urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('kanban/', views.ProjectKanbanView.as_view(), name='kanban'),
    path('timeline/', ProjectTimelineView.as_view(), name='timeline'),
    path('<int:project_id>/dashboard/', project_dashboard, name='project_dashboard'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/update-status/', views.update_project_status, name='update_status'),
    path('<int:pk>/submit/', views.ProjectSubmitView.as_view(), name='submit'),
    path('submit/<int:pk>/', views.submit_project, name='submit_project'),
    # Work Log URLs
    path('<int:project_pk>/work-log/add/', views.WorkLogCreateView.as_view(), name='add_work_log'),
    path('<int:pk>/send-feedback/', SendFeedbackRequestView.as_view(), name='send_feedback'),
    # path('<int:pk>/client-feedback/', ClientFeedbackView.as_view(), name='client_feedback'),
    path('client-feedback/<uuid:token>/', ClientFeedbackTokenView.as_view(),
         name='client_feedback_token'),
    path('feedback/thank-you/', feedback_thank_you, name='feedback_thank_you'),

]

print("DEBUG: URL patterns loaded:", urlpatterns)