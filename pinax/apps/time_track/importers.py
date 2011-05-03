import csv
from datetime import datetime


from pinax.apps.projects.models import Project
from pinax.apps.time_track.models import LoggedTime



importer_choices = (
    ("", "[Select One]"),
    ("HamsterTsvImporter", "Gnome Time Tracker TSV Export"),
    ("FreshbooksCsvImporter", "Fresh Books CSV Export"),
)



class AbstractImporter:
    
    _projects = {}
    
    def __init__(self, uploaded_file, user):
        self.uploaded_file = uploaded_file
        self.user = user
    
    def get_logged_times(self):
        raise NotImplementedError()
    
    def _get_project(self, slug):
        if not slug in self._projects:
            try:
                self._projects[slug] = Project.objects.get(slug=slug)
            except:
                raise ValueError("Project '%s' not found" % slug)
        return self._projects[slug]


class HamsterTsvImporter(AbstractImporter):
    
    format = "%Y-%m-%d %H:%M:%S"
    
    def get_logged_times(self):
        tsv_reader = csv.reader(self.uploaded_file, delimiter="\t")
        tsv_reader.next() # to skip the header row
        return [self._logged_time_from_row(row) for row in tsv_reader if row[4] == "Work"]
    
    def _logged_time_from_row(self, row):
        # 0 -> activity (project slug)
        # 1 -> start_time (parse into date)
        # 2 -> end_time (parse into date)
        # 3 -> duration_minutes (unused)
        # 4 -> category (must be 'Work')
        # 5 -> description (summary)
        # 6 -> tags (unused)
        project = self._get_project(row[0])
        start = datetime.strptime(row[1], self.format)
        finish = datetime.strptime(row[2], self.format)
        return LoggedTime(group=project, summary=row[5],
                    owner=self.user, start=start, finish=finish)


class FreshbooksCsvImporter(AbstractImporter):
    
    format = "%m/%d/%y"
    
    def get_logged_times(self):
        csv_reader = csv.reader(self.uploaded_file)
        csv_reader.next() # to skip the header row
        return [self._logged_time_from_row(row) for row in csv_reader]
    
    def _logged_time_from_row(self, row):
        # 0 -> team (unused)
        # 1 -> date (parse into date)
        # 2 -> project (project slug)
        # 3 -> task (unused)
        # 4 -> notes (summary)
        # 5 -> hours (float of hours)
        # 6 -> billed (unused)
        project = self._get_project(row[2])
        start = datetime.strptime(row[1], self.format)
        finish = start + timedelta(hours=float(row[5]))
        return LoggedTime(group=project, summary=row[4],
                    owner=self.user, start=start, finish=finish)

