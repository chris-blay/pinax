from datetime import datetime
from sys import stderr

from django import forms
from django.core.exceptions import ImproperlyConfigured
from django.db.models import get_app
from django.utils.translation import ugettext
from django.contrib.auth.models import User

from pinax.apps.time_track.models import LoggedTime
from pinax.apps.time_track.importers import importer_choices



class LoggedTimeForm(forms.ModelForm):
    """
    Form for creating logged times
    """
    
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        
        super(LoggedTimeForm, self).__init__(*args, **kwargs)
        
        if group:
            owner_queryset = group.member_queryset()
        else:
            owner_queryset = self.fields["owner"].queryset
        
        self.fields["owner"].queryset = owner_queryset
        self.fields["summary"].widget.attrs["size"] = 65
    
    class Meta:
        model = LoggedTime
        fields = [
            "summary",
            "owner",
            "start",
            "finish"
        ]
    
    def clean(self):
        self.check_group_membership()
        return self.cleaned_data
    
    def check_group_membership(self):
        group = self.group
        if group and not self.group.user_is_member(self.user):
            raise forms.ValidationError("You must be a member to create tasks")


class EditLoggedTimeForm(forms.ModelForm):
    """
    Form for editing logged times
    """
    
    def __init__(self, user, group, *args, **kwargs):
        self.user = user
        self.group = group
        
        super(EditLoggedTimeForm, self).__init__(*args, **kwargs)
        
        self.fields["summary"].widget.attrs["size"] = 65
        
        if not workflow.is_task_manager(self.instance, user):
            del self.fields["detail"]
    
    class Meta(LoggedTimeForm.Meta):
        fields = [
            "summary",
            "start",
            "finish"
        ]

class UploadLoggedTimeForm(forms.Form):
    """
    Form for uploading and importing a file of logged times
    """
    
    # TODO make this configurable in settings
    file_input = forms.FileField("time_track_upload")
    file_type = forms.ChoiceField(choices=importer_choices)
    
    def add_file_input_error(self, ex):
        self._errors['file_input'] = self.error_class([ex])

