from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'company', 'is_submitted', 'created_at')
    list_filter = ('is_submitted', 'category')
    search_fields = ('name', 'company', 'description', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)  # removed updated_at

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_submitted:  # If project exists and is submitted
            return [field.name for field in obj._meta.fields]  # Make all fields readonly
        return self.readonly_fields

