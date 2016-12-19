from portfolio_manager.models import *
import pdb

from datetime import datetime, timedelta
from django.utils import timezone


def run():

  now = timezone.now()

  project = Project()
  project.save()

  d_project_manager = ProjectManagerDimension()
  d_project_manager.save()

  d_milestones = MilestonesDimension()
  d_milestones.save();

  d_members = MembersDimension()
  d_members.save()

  d_numeric = NumericDimension()
  d_numeric.value = 0;
  d_numeric.save()

  pd1 = ProjectDimension()
  pd1.project = project
  pd1.dimension_object = d_milestones
  pd1.save()

  pd2 = ProjectDimension()
  pd2.project = project
  pd2.dimension_object = d_project_manager
  pd2.save()

  pd3 = ProjectDimension()
  pd3.project = project
  pd3.dimension_object = d_members
  pd3.save()

  pd4 = ProjectDimension()
  pd4.project = project
  pd4.dimension_object = d_numeric
  pd4.save()

  person1 = Person();
  person1.first_name = 'Vito'
  person1.last_name = 'Rinnelli'
  person1.save()

  person2 = Person()
  person2.first_name = 'Dorothy'
  person2.last_name = 'Schutte'
  person2.save()

  person3 = Person()
  person3.first_name = 'Irv'
  person3.last_name = 'Schecter'
  person3.save()

  person4 = Person()
  person4.first_name = 'Tom'
  person4.last_name = 'Doss'
  person4.save()

  project_milestone = ProjectMilestone()
  project_milestone.deadline = now + timedelta(days=8)
  project_milestone.save()
  d_milestones.set_milestones([project_milestone])

  d_numeric_milestone = NumericDimensionMilestone()
  d_numeric_milestone.numeric_dimension = d_numeric
  d_numeric_milestone.value = 7
  d_numeric_milestone.save()

  project_milestone_d_numeric_milestone = ProjectMilestoneDimensionMilestone()
  project_milestone_d_numeric_milestone.project_milestone = project_milestone
  project_milestone_d_numeric_milestone.dimension_milestone_object = d_numeric_milestone
  project_milestone_d_numeric_milestone.save()

  # Update numeric dimension
  d_numeric.update_value(4, now + timedelta(days=2))
  d_numeric.update_value(5, now + timedelta(days=6))
  d_numeric.update_value(7, now + timedelta(days=7))

  # Update team members
  d_members.set_members([person1], now)
  d_members.set_members([person1, person2], now + timedelta(days=4))
  d_members.set_members([person2], now + timedelta(days=10))

  # Update project manager
  d_project_manager.update_value(person3, now)
  d_project_manager.update_value(person4, now + timedelta(days=7))

  print "Project dimensions"
  print project.dimensions.all()
  print ""

  print "Members history"
  for version in Version.objects.get_for_object(d_members):
    print str(map((lambda x: Person.objects.get(pk=x) ), version.field_dict['members']))+" @ "+str(version.revision.date_created)
  print ""

  print "Project manager history"
  for version in Version.objects.get_for_object(d_project_manager):
    print str(Person.objects.get(pk=version.field_dict['value_id']))+" @ "+str(version.revision.date_created)
  print ""

  print "Numeric history"
  for version in Version.objects.get_for_object(d_numeric):
    print "id "+str(version.field_dict['id'])+" value: "+str(version.field_dict['value'])+" @ "+str(version.revision.date_created)
  print ""

  print "Milestones history"
  for version in Version.objects.get_for_object(d_milestones):
    print str(map((lambda x: ProjectMilestone.objects.get(pk=x) ), version.field_dict['milestones']))+" @ "+str(version.revision.date_created)
  print ""
