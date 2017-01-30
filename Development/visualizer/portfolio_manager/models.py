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

class Person (models.Model):
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64)

class DecimalDimension (Dimension):
  value = models.DecimalField(max_digits = 20, decimal_places = 2)
  history = HistoricalRecords()
  __history_date = None

class DecimalDimensionMilestone (models.Model):
  value = models.DecimalField(max_digits = 20, decimal_places=2)
  at = models.DateTimeField()
  decimal_dimension = models.ForeignKey(DecimalDimension, on_delete=models.CASCADE, related_name='milestones')
  history = HistoricalRecords()
  __history_date = None
  
class TextDimension (Dimension):
  value = models.TextField()
  history = HistoricalRecords()
  __history_date = None
    
class AssociatedOrganizationDimension (Dimension):
  value = models.ForeignKey(Organization, null=True)
  history = HistoricalRecords()

class AssociatedPersonDimension (Dimension):
  value = models.ForeignKey(Person, null=True)
  history = HistoricalRecords()
  
#Dimension for project participant management
class AssociatedPersonsDimension(Dimension):
  persons = models.ManyToManyField(Person, through='DimensionPerson', through_fields=('dimension', 'person'))

class DimensionPerson(models.Model):
  dimension = models.ForeignKey(AssociatedPersonsDimension, on_delete=models.CASCADE)
  person = models.ForeignKey(Person, on_delete=models.CASCADE)
  history = HistoricalRecords()
  __history_date = None

#Storing the project dependencies as list of project IDs
class AssociatedProjectsDimension(Dimension):
  projects = models.ManyToManyField(Project, through='DimensionProject', through_fields=('dimension', 'project'))

class DimensionProject(models.Model):
  dimension = models.ForeignKey(AssociatedProjectsDimension, on_delete=models.CASCADE)
  project = models.ForeignKey(Project, on_delete=models.CASCADE)
  history = HistoricalRecords()
  __history_date = None

class DateDimension (Dimension):
  value = models.DateTimeField()
  history = HistoricalRecords()
  


