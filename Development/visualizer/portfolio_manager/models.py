# from __future__ import unicode_literals
#
# from django.db import models
# from simple_history.models import HistoricalRecords
#
# class Organization (models.Model):
#     name = models.CharField(max_length=50, primary_key=True)
#     history = HistoricalRecords()
#     def __str__(self):
#         return str(self.name)
#
#     def __unicode__(self):
#         return self.name
#
# class Project (models.Model):
#     name = models.CharField(max_length=50)
#     parent = models.ForeignKey('Organization',on_delete=models.CASCADE)
#     history = HistoricalRecords()


from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
from datetime import datetime
import pytz

def import_models_data(data):

  Project.objects.all().delete()

  dimensions = data[0][2:]
  prev_id = -1

  for update in data[1:]:
    project_id = update[0]
    project = None

    if project_id != prev_id: # new project
      project = Project()
      project.id = update[0]
      project.save()
      prev_id = update[0]
    
      for idx, dimension in enumerate(dimensions):
        if dimension == 'Members' or dimension == 'ProjectDependencies':
          continue

        dimension_class = globals()[dimension+"Dimension"]
        dimension_object = dimension_class()
        dimension_object.from_sheet(update[2+idx])
        dimension_object.save()

        project_dimension = ProjectDimension()
        project_dimension.project = project
        project_dimension.dimension_object = dimension_object
        project_dimension.save()

    else:
      project = Project.objects.get(pk=project_id)

      for idx, dimension_update in enumerate(update[2:]):
        if dimension_update:
          if dimensions[idx] == 'Members' or dimensions[idx] == 'ProjectDependencies':
            continue
          project_dimension = ProjectDimension.objects.get(project=project, content_type=ContentType.objects.get_for_model(globals()[dimensions[idx]+"Dimension"]))
          project_dimension.dimension_object.from_sheet(dimension_update)
          project_dimension.dimension_object.save()
      
   

    
#Model for a Organization
#Id generated automatically
class Organization (models.Model):
  name = models.CharField(max_length=50, primary_key=True)
  history = HistoricalRecords()

  def __str__(self):
    return str(self.name)

  def __unicode__(self):
    return self.name

#Model for a Project instance
#Id generated automatically
class Project (models.Model):
  name = models.CharField(max_length=50)
  parent = models.ForeignKey('Organization', null=True,on_delete=models.CASCADE)
  history = HistoricalRecords()

#Model for a project dimension
class ProjectDimension (models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dimensions')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_object = GenericForeignKey('content_type', 'object_id')

  def __unicode__(self):
    return self.dimension_object.__class__.__name__

  def __str__(self):
    return unicode(self).encode('utf-8')

#model for a Dimension to use in comparisons
class Dimension (models.Model):
  class Meta:
    abstract = True

  name = models.CharField(max_length=64)

  def get_content_type(self):
    return ContentType.objects.get_for_model(self).id

  def update_value(self, value, when=None):
      self.value = value
      self.save()

#Dimensions for Integer, Decimal and Text inputs
#update_value adds timestamp when edited
class NumericDimension (Dimension):

  value = models.IntegerField()


#model for comparisons between milestones and NumericDimension values
class NumericDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='milestones')
  value = models.IntegerField()

  def __unicode__(self):
    return "id: "+str(self.numeric_dimension.id)+" value: "+str(self.value)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def on_schedule(self, deadline):
    versions = Version.objects.get_for_object(self.numeric_dimension)
    versions = versions.filter(revision__date_created__lte=deadline)

    dimension_value = self.numeric_dimension.value
    try:
        dimension_value = versions[0].field_dict["value"]
    except IndexError:
      pass

    return self.value <= dimension_value

class ProjectMilestone (models.Model):
  deadline = models.DateTimeField()

  def __unicode__(self):
    return str(map((lambda x: x.dimension_milestone_object.__class__.__name__+": "+str(x.dimension_milestone_object)) , self.dimension_milestones.all()))+" @ "+str(self.deadline)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def on_schedule(self):
    for dimension_milestone in self.dimension_milestones.all():
      if not dimension_milestone.dimension_milestone_object.on_schedule(self.deadline):
        return False

    return True

class MilestonesDimension (Dimension):

  milestones = models.ManyToManyField(ProjectMilestone, related_name='milestones_dimensions')

  def set_milestones(self, milestones):
      self.milestones.set(milestones)

#Model for
class ProjectMilestoneDimensionMilestone (models.Model):
  project_milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='dimension_milestones')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_milestone_object = GenericForeignKey('content_type', 'object_id')

class Person (models.Model):
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64)

  def __unicode__(self):
    return self.first_name+" "+self.last_name

  def __str__(self):
    return unicode(self).encode('utf-8')

#Dimension for project participant management
class MembersDimension(Dimension):
  members = models.ManyToManyField(Person)

  def set_members(self, members, when=None):
      self.members.set(members)

  # def from_sheet(self, value):
  #   pass

  # def update_from_sheet(self, value):

  #   members_update = []

  #   for first_name in value.split(','):
  #     member = None
  #     member_first_name = first_name.strip()
  #     try:
  #       member = Person.objects.get(first_name=member_first_name)
  #     except Person.DoesNotExist:
  #       member = Person()
  #       member.first_name = member_first_name
  #       member.save()
  #     members_update.append(member)

  #   self.members.set(members_update)

class DecimalDimension (Dimension):
    value = models.DecimalField(max_digits = 20, decimal_places = 2)
    
    def from_sheet(self, value):
      self.value = value

    def update_from_sheet(self, value):
      pass

#model for comparisons between milestones and DecimalDimension values
class DecimalDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(DecimalDimension, on_delete=models.CASCADE, related_name='decimal_milestones')
  value = models.IntegerField()

class TextDimension (Dimension):
    value = models.TextField()
    
    def from_sheet(self, value):
      self.value = value

    def update_from_sheet(self, value):
      pass

class AssociatedPersonDimension (Dimension):
  value = models.ForeignKey(Person, null=True)
  
  def from_sheet(self, value):
    person = None
    try:
      person = Person.objects.get(first_name=value)
    except Person.DoesNotExist:
      person = Person()
      person.first_name = value
      person.save()

    self.value = person

  def update_from_sheet(self, value):
      pass

#Connection between project and a project owner
class ProjectOwnerDimension (AssociatedPersonDimension):
    history = HistoricalRecords()

#Connection between project and a project manager
class ProjectManagerDimension (AssociatedPersonDimension):
    history = HistoricalRecords()

#Storing the project dependencies as list of project IDs
class ProjectDependenciesDimension(Dimension):
    dependencies = models.ManyToManyField(Project)

    def set_dependencies(self, dependencies, when=None):
        self.dependencies.set(dependencies)
        self.save()

    # def from_sheet(self, value):
    #   pass

    # def update_from_sheet(self, value):
    #   if value:
    #     self.dependencies.set([Project.objects.get(pk=value)])

#Task class
#Is person completing task essential?
class Task (Dimension):
    task_description = models.TextField()
    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

#Project size in money
class SizeMoneyDimension (DecimalDimension):
  history = HistoricalRecords()

#Project size in man-days
class SizeManDaysDimension(DecimalDimension):
  history = HistoricalRecords()

#Project size as effect
class SizeEffectDimension(TextDimension):
  history = HistoricalRecords()

#Technologies used in project
class TechnologyDimension(TextDimension):
  history = HistoricalRecords()

#Development model used in project
class DevelopmentModelDimension(TextDimension):
  history = HistoricalRecords()

#Description of the project
class DescriptionDimension(TextDimension):
  history = HistoricalRecords()

class Supplier(models.Model):
  name = models.CharField(max_length=50)

#Deliverer of the project
class SuppliersDimension(Dimension):
  suppliers = models.ManyToManyField(Supplier)

  def set_suppliers(self, suppliers, when=None):
      self.suppliers.set(suppliers)
      self.save()

#Customer of the project
class CustomerDimension(TextDimension):
  history = HistoricalRecords()

#Phase of the project as a list of Milestone IDs
class PhaseDimension (TextDimension):
  history = HistoricalRecords()

class OwningOrganizationDimension (TextDimension):
  history = HistoricalRecords()

class DateDimension (Dimension):
  value = models.DateTimeField()
  
  def from_sheet(self, value):
    self.value = pytz.utc.localize(datetime.strptime(value, '%d/%m/%Y'))

  def update_from_sheet(self, value):
      pass

class StartDateDimension (DateDimension):
  history = HistoricalRecords()

class EndDateDimension (DateDimension):
  history = HistoricalRecords()

class DepartmentDimension (TextDimension):
  history = HistoricalRecords()

class VendorDimension (TextDimension):
  history = HistoricalRecords()

class NameDimension (TextDimension):
  history = HistoricalRecords()


