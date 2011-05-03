from datetime import datetime
import re

from pinax.apps.projects.models import Project
from pinax.apps.time_track.models import LoggedTime



importer_choices = (
    ("", "[Select One]"),
    ("HamsterTsvImporter", "Gnome Time Tracker TSV Export"),
    ("FreshbooksCsvImporter", "Fresh Books CSV Export"),
)



class AbstractImporter:
    
    projects = {}
    
    def __init__(self, uploaded_file, user):
        self.file_contents = uploaded_file.read()
        self.user = user
    
    def get_logged_times(self):
        raise NotImplementedError()
    
    def _get_project(self, slug):
        if not slug in self.projects:
            self.projects[slug] = Project.objects.filter(slug=slug)
        if self.projects[slug]:
            return self.projects[slug][0]
        return None


class HamsterTsvImporter(AbstractImporter):
    
    def get_logged_times(self):
        logged_times = []
        skip_one = True
        for match in re.finditer(r"(?P<activity>.*?)\t(?P<start_time>.*?)\t(?P<end_time>.*?)\t(?P<duration_minutes>.*?)\t(?P<category>.*?)\t(?P<description>.*?)\t.*?\n?\r?", self.file_contents):
            if skip_one:
                skip_one = False
                continue
            activity = match.group('activity')
            project = self._get_project(activity)
            if not project:
                raise ValueError("Project '%s' not found" % activity)
            # TODO optionally get this from the settings
            format = "%Y-%m-%d %H:%M:%S"
            start = datetime.strptime(match.group('start_time'), format)
            finish = datetime.strptime(match.group('end_time'), format)
            logged_times.append(LoggedTime(group=project, summary=match.group('description'), owner=self.user, start=start, finish=finish))
        if not logged_times:
            raise ValueError("No logged times found")
        return logged_times


class FreshbooksCsvImporter(AbstractImporter):
    
    pass # TODO
