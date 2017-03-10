import gspread
from portfolio_manager.models import *
from oauth2client.service_account import ServiceAccountCredentials
import os
from dateutil.parser import parse

def from_data_array(data):

  # thefile = open('/tmp/dumppi', 'w')
  # for item in data:
  #   thefile.write("%s\n" % ';'.join(item))

  dimensions = data[0][2:]
  prev_id = -1
  dimension_objects = None
  project_dimension_objects = None
  project = None

  for update in data[1:]:

    history_date = parse(update[1], dayfirst=True)
    if history_date.tzinfo is None or history_date.tzinfo.utcoffset(history_date) is None:
      history_date = history_date.replace(tzinfo=pytz.utc)

    if 'm;' in update[0]: # milestone row

      parts = update[0].split(';')
      milestone_due_date = parse(parts[1], dayfirst=True)
      if milestone_due_date.tzinfo is None or milestone_due_date.tzinfo.utcoffset(milestone_due_date) is None:
        milestone_due_date = milestone_due_date.replace(tzinfo=pytz.utc)

      milestone = Milestone()
      milestone.due_date = milestone_due_date
      milestone.project = project;
      milestone._history_date = history_date
      milestone.save()

      for idx, milestone_value in enumerate(update[2:]):

        if milestone_value:
          dimension_name = dimensions[idx].strip()
          milestone_sub_class = globals()[dimension_name+"Milestone"]
          milestone_parent_class = milestone_sub_class.__bases__[0]
          dimension_milestone_object = milestone_parent_class()
          dimension_milestone_object.from_sheet(milestone_value)
          dimension_milestone_object.save()

          dimension_milestone = DimensionMilestone()
          dimension_milestone.milestone = milestone
          dimension_milestone.dimension_milestone_object = dimension_milestone_object
          dimension_milestone.project_dimension = project_dimension_objects[idx]
          dimension_milestone.save()

    else: 
      project_id = update[0]

      if project_id != prev_id: # new project

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

        if dimension_update:

          dimension_object = None
          create_project_dimension = False

          dimension_object_name = dimensions[idx].strip()

          try:
            dimension_object = dimension_objects[idx]
          except KeyError:
            try:
              dimension_sub_class = globals()[dimension_object_name+"Dimension"]
            except KeyError:
              # Add info to notification
              continue

            dimension_parent_class = dimension_sub_class.__bases__[0]
            dimension_object = dimension_parent_class()
            dimension_object.name = dimension_object_name
            create_project_dimension = True

          dimension_object.from_sheet(dimension_update.strip(), history_date)
          dimension_object.save()

          if dimension_object_name == 'OwningOrganization':
            project.parent = dimension_object.value
            project.save()

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

# Only sheets shared with reader@portfolio-sheet-data.iam.gserviceaccount.com can be imported!

def from_google_sheet(SheetUrl):
    try:
        scope = ['https://www.googleapis.com/auth/drive','https://spreadsheets.google.com/feeds','https://docs.google.com/feeds']
        dir_path = os.path.dirname(os.path.realpath(__file__))
        credentials = ServiceAccountCredentials.from_json_keyfile_name(dir_path+'/data/service_account.json', scope)
        gc = gspread.authorize(credentials)
        Sheet = gc.open_by_url(SheetUrl)
        worksheet = Sheet.get_worksheet(0)
        from_data_array(worksheet.get_all_values())
    except gspread.exceptions.SpreadsheetNotFound:
        print("spreadsheet not found")
    except gspread.exceptions.NoValidUrlKeyFound:
        print("URLi paskana")
