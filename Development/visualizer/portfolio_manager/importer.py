import gspread
import sys
import os
from dateutil.parser import parse
from django.core.management.color import no_style
from django.db import connection
from oauth2client.service_account import ServiceAccountCredentials
from portfolio_manager.models import *

class TypeHelper:
    def dimension_by_column(self, idx):
        abbr = self.dim_types[idx]
        return self.data_types[abbr]()

    def milestone_by_column(self, idx):
        abbr = self.dim_types[idx]
        return self.milestone_types[abbr]()

    def dim_name_by_column(self, idx):
        return self.dim_names[idx].strip()

    def __init__(self, dim_names, dim_types):
        self.dim_names = dim_names
        self.dim_types = dim_types
        self.data_types = {
            'TEXT': TextDimension,
            'NUM': DecimalDimension,
            'DATE': DateDimension,
            'AORG': AssociatedOrganizationDimension,
            'APROJ': AssociatedProjectsDimension,
            'APER': AssociatedPersonDimension,
            'APERS': AssociatedPersonsDimension
        }
        self.milestone_types = {
            'NUM': DecimalMilestone
        }

def parse_date_tz(data):
    history_date = parse(data, dayfirst=True) # Timestamp of the update is in second column
    # Set default timezone if timestamp doesn't include it
    if history_date.tzinfo is None or history_date.tzinfo.utcoffset(history_date) is None:
      history_date = history_date.replace(tzinfo=pytz.utc)

    return history_date

def from_data_array(data):
    rows_imported = 0
    milestones_imported = 0
    rows_skipped = 0
    helper = TypeHelper(dim_names=data[0][2:], dim_types=data[1][2:])
    prev_id = -1
    dimension_objects = None
    project_dimension_objects = None
    project = None

    #   Go through each row
    for counter, update in enumerate(data[2:]):
        milestonerow = False
        try:
            history_date = parse_date_tz(update[1])

            if 'm;' in update[0]: # Sheet row represents a milestone
                milestonerow = True
                parts = update[0].split(';') # ID column format m;[milestone_due_date]
                milestone_due_date = parse_date_tz(parts[1])

                milestone = Milestone()
                milestone.due_date = milestone_due_date
                milestone.project = project;
                milestone._history_date = history_date
                milestone.save()

                for idx, milestone_value in enumerate(update[2:]):
                    if milestone_value:
                        dimension_name = helper.dim_name_by_column(idx)
                        dimension_milestone_object = helper.milestone_by_column(idx)
                        dimension_milestone_object.from_sheet(milestone_value)
                        dimension_milestone_object.save()

                        # Connect dimension specific milestone to parent milestone object
                        dimension_milestone = DimensionMilestone()
                        dimension_milestone.milestone = milestone
                        dimension_milestone.dimension_milestone_object = dimension_milestone_object
                        dimension_milestone.project_dimension = project_dimension_objects[idx]
                        dimension_milestone.save()

            else: # Row represents an update to project's dimensions
                project_id = update[0] # First column contains project id

                if project_id != prev_id: # new project
                    # If there exists a project with the same id, remove it
                    try:
                        project = Project.objects.get(id=project_id)
                        project.delete()
                    except Project.DoesNotExist:
                        pass
                    project = Project()
                    project.id = update[0]
                    project.save()
                    prev_id = update[0]

                    dimension_objects = {}
                    project_dimension_objects = {}

                for idx, dimension_update in enumerate(update[2:]):

                    if dimension_update:    # If there is a value in the cell
                        dimension_object = None
                        create_project_dimension = False  # Check
                        dimension_object_name = helper.dim_name_by_column(idx)
                        try:
                            dimension_object = dimension_objects[idx]
                        except KeyError:
                            dimension_object = helper.dimension_by_column(idx)
                            dimension_object.name = dimension_object_name
                            create_project_dimension = True
                        dimension_object.from_sheet(dimension_update.strip(), history_date)
                        dimension_object.save()

                        # We should get rid of project.parent and use some AssociatedOrganization type of
                        # dimension instead. In general all project attributes should be represented by
                        # Dimensions
                        if dimension_object_name == 'OwningOrganization':
                            project.parent = dimension_object.value
                            project.save()

                        # We should get rid of project.name and use some TextDimension type of
                        # dimension instead. In general all project attributes should be represented by
                        # Dimensions
                        if dimension_object_name == 'Name':
                            project.name = dimension_object.value
                            project.save()

                        if create_project_dimension:
                            project_dimension = ProjectDimension()
                            project_dimension.project = project
                            project_dimension.dimension_object = dimension_object
                            project_dimension.save()

                        dimension_objects[idx] = dimension_object
                        project_dimension_objects[idx] = project_dimension

                # Create default project template for every organization that some project belongs to.
                if project.parent and project.parent.templates.all().count() == 0:
                    template = ProjectTemplate()
                    template.name = 'default'
                    template.organization = project.parent
                    template.save()

                    for key, dimension_object in dimension_objects.items():
                        template_dimension = ProjectTemplateDimension()
                        template_dimension.template = template
                        template_dimension.name = dimension_object.name
                        template_dimension.content_type = dimension_object.get_content_type()
                        template_dimension.save()
        except Exception as e:
            print("ERROR: {}. Skipping row {}".format(e, counter+3))
            rows_skipped += 1
            continue
        else:
            if(milestonerow):
                milestones_imported += 1
            else:
                rows_imported += 1

    print("Rows imported: {}".format(rows_imported))
    print("Milestones imported: {}".format(milestones_imported))
    print("Rows skipped: {}".format(rows_skipped))
    result = {
        'rows_imported': rows_imported,
        'milestones_imported': milestones_imported,
        'rows_skipped': rows_skipped
    }
    return result

# Only sheets shared with reader@portfolio-sheet-data.iam.gserviceaccount.com can be imported!
def from_google_sheet(SheetUrl):
    result = {
        'rows_imported': 0,
        'milestones_imported': 0,
        'rows_skipped': 0
    }
    try:
        scope = [
            'https://www.googleapis.com/auth/drive',
            'https://spreadsheets.google.com/feeds',
            'https://docs.google.com/feeds'
        ]
        dir_path = os.path.dirname(os.path.realpath(__file__))
        credentials = ServiceAccountCredentials.from_json_keyfile_name(dir_path+'/data/service_account.json', scope)
        gc = gspread.authorize(credentials)
        Sheet = gc.open_by_url(SheetUrl)
        worksheet = Sheet.get_worksheet(0)
        result = from_data_array(worksheet.get_all_values())
    except Exception as e:
        print("from_google_sheet_error: {}".format(e))
    finally:
        # Importer creates Project model instances with pre-defined IDs. That operation
        # messes up Postgresql primary key sequences. Lets reset the sequences.
        with connection.cursor() as cursor:
            for stmt in connection.ops.sequence_reset_sql(no_style(), [Project]):
                cursor.execute(stmt)
        return result
