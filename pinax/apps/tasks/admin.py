from django.contrib import admin
from attachments.admin import AttachmentInlines
from pinax.apps.tasks.models import Task, Milestone



class TaskOptions(admin.ModelAdmin):
    inlines = [AttachmentInlines]



admin.site.register(Task, TaskOptions)
admin.site.register(Milestone, TaskOptions)
