##
#
# Portfolio Visualizer
#
# Copyright (C) 2017 Codento
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##
import gspread
import os
from dateutil.parser import parse
from django.core.management.color import no_style
from django.db import connection
from oauth2client.service_account import ServiceAccountCredentials
import pytz

from portfolio_manager.models import TextDimension, NumberDimension, DateDimension, AssociatedOrganizationDimension, \
    AssociatedProjectsDimension, AssociatedPersonDimension, AssociatedPersonsDimension, NumberMilestone, \
    DimensionMilestone, Project, FourFieldSnapshot, Milestone, ProjectDimension, ProjectTemplate, \
    ProjectTemplateDimension, GoogleSheet


class ImportHelper:
    def __init__(self, dim_names, dim_types):
        self.dim_names = dim_names
        self.dim_types = dim_types
        self.data_types = {
            'TEXT': TextDimension,
            'NUM': NumberDimension,
            'DATE': DateDimension,
            'AORG': AssociatedOrganizationDimension,
            'APROJ': AssociatedProjectsDimension,
            'APER': AssociatedPersonDimension,
            'APERS': AssociatedPersonsDimension
        }
        self.milestone_types = {
            'NUM': NumberMilestone
        }

    def dimension_by_column(self, idx):
        abbr = self.dim_types[idx]
        return self.data_types[abbr]()

    def milestone_by_column(self, idx):
        abbr = self.dim_types[idx]
        return self.milestone_types[abbr]()

    def dim_name_by_column(self, idx):
        return self.dim_names[idx].strip()

    def create_milestone(self, idx, value, milestone, project_dimension):
        dim_mile_object = self.milestone_by_column(idx)
        dim_mile_object.from_sheet(value)
        dim_mile_object.save()

        dim_mile = DimensionMilestone()
        dim_mile.milestone = milestone
        dim_mile.dimension_milestone_object = dim_mile_object
        dim_mile.project_dimension = project_dimension
        dim_mile.save()

    def remove_and_create_project(self, pid):
        # If there exists a project with the same id, remove it
        try:
            project = Project.objects.get(id=pid)
            project.delete()
        except Project.DoesNotExist:
            pass

        project = Project()
        project.id = pid
        project.save()
        return project

    def parse_date_tz(self, data):
        history_date = parse(data, dayfirst=True) # Timestamp of the update is in second column
        # Set default timezone if timestamp doesn't include it
        if history_date.tzinfo is None or history_date.tzinfo.utcoffset(history_date) is None:
            history_date = history_date.replace(tzinfo=pytz.utc)
        return history_date

    def type_row_is_valid(self):
        for column, abbr in enumerate(self.dim_types):
            if abbr not in self.data_types:
                return False, column + 3
        return True, -1


    def remove_fourfield_snaps(self):
        FourFieldSnapshot.objects.all().delete()
        return


def from_data_array(data):
    rows_imported = 0
    milestones_imported = 0
    rows_skipped = 0
    helper = ImportHelper(dim_names=data[0][2:], dim_types=data[1][2:])
    prev_id = -1
    dimension_objects = None
    project_dimension_objects = None
    project = None

    type_row_is_valid, row_num = helper.type_row_is_valid()
    if not type_row_is_valid:
        result = {
            'result': False,
            'error_msg': 'Fatal error in row 2 column {}'.format(row_num),
            'rows_imported': 0,
            'milestones_imported': 0,
            'rows_skipped': 0
        }
        return result

    try:
        helper.remove_fourfield_snaps()
    except Exception as e:
        print("Failed to remove fourfield snaps!")

    #   Go through each row
    for counter, update in enumerate(data[2:]):
        milestonerow = False
        try:
            history_date = helper.parse_date_tz(update[1])
            if 'm;' in update[0]: # Sheet row represents a milestone
                milestonerow = True
                parts = update[0].split(';') # ID column format m;[milestone_due_date]
                milestone_due_date = helper.parse_date_tz(parts[1])

                milestone = Milestone()
                milestone.due_date = milestone_due_date
                milestone.project = project;
                milestone._history_date = history_date
                milestone.save()

                for idx, milestone_value in enumerate(update[2:]):
                    if milestone_value:
                        helper.create_milestone(idx, milestone_value, milestone, project_dimension_objects[idx])
            else: # Row represents an update to project's dimensions
                if update[0] != prev_id: # new project
                    project = helper.remove_and_create_project(update[0])
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
                if project.parent:
                    for key, dimension_object in dimension_objects.items():
                        project.parent.add_template(
                            template_name='default',
                            dim_obj=dimension_object
                        )
        except Exception as e:
            print("ERROR: {}. Skipping row {}".format(e, counter+3))
            rows_skipped += 1
            continue
        else:
            if(milestonerow):
                milestones_imported += 1
            else:
                rows_imported += 1

    result = {
        'result': True,
        'rows_imported': rows_imported,
        'milestones_imported': milestones_imported,
        'rows_skipped': rows_skipped
    }
    return result

# Only sheets shared with reader@portfolio-sheet-data.iam.gserviceaccount.com can be imported!
def from_google_sheet(SheetUrl):
    result = {
        'result': False,
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
        worksheet = Sheet.sheet1
        sheetname = Sheet.title
        google_sheet = GoogleSheet(name=sheetname, url=SheetUrl)
        google_sheet.save()
        result = from_data_array(worksheet.get_all_values())
        result['name'] = sheetname
    except Exception as e:
        print("from_google_sheet_error: {}".format(e))
    finally:
        # Importer creates Project model instances with pre-defined IDs. That operation
        # messes up Postgresql primary key sequences. Lets reset the sequences.
        with connection.cursor() as cursor:
            for stmt in connection.ops.sequence_reset_sql(no_style(), [Project]):
                cursor.execute(stmt)
        return result
