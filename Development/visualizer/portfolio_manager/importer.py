import gspread
from portfolio_manager.models import *
from oauth2client.service_account import ServiceAccountCredentials
import os

def from_data_array(data):

  dimensions = data[0][2:]
  prev_id = -1
  dimension_objects = None
  project = None

  for update in data[1:]:

    project_id = update[0]

    if project_id != prev_id: # new project

      try:
        project = Project.objects.get(id=project_id)
        # org = Organization.objects.get(name=update[6])
        project.delete()
      except Project.DoesNotExist:
        pass
    # except Organization.DoesNotExist:
    #     pass

      project = Project()
    #   org = Organization()
    #   org.name = update[6]
      project.id = update[0]
      project.name = update[2]
      project.save()
      prev_id = update[0]

      dimension_objects = {}

    for idx, dimension_update in enumerate(update[2:]):

      if dimension_update:

        dimension_object = None
        create_project_dimension = False

        try:
          dimension_object = dimension_objects[idx]
        except KeyError:
          dimension_sub_class = globals()[dimensions[idx].strip()+"Dimension"]
          dimension_parent_class = dimension_sub_class.__bases__[0]
          dimension_object = dimension_parent_class()
          dimension_object.name = dimensions[idx].strip()
          create_project_dimension = True

        history_date = parse(update[1])
        if history_date.tzinfo is None or history_date.tzinfo.utcoffset(history_date) is None:
          history_date = history_date.replace(tzinfo=pytz.utc)

        dimension_object.from_sheet(dimension_update.strip(), history_date)
        dimension_object.save()

        if create_project_dimension:
          project_dimension = ProjectDimension()
          project_dimension.project = project
          project_dimension.dimension_object = dimension_object
          project_dimension.save()

          dimension_objects[idx] = dimension_object

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
