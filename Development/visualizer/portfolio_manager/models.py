from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import reversion
from reversion.models import Version

# Create your models here.

class Organization (models.Model):
  name = models.CharField(max_length=50, primary_key=True)

class Project (models.Model):
  name = models.CharField(max_length=50)
  parent = models.ForeignKey("Organization", null=True)

class ProjectDimension (models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dimensions')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_object = GenericForeignKey('content_type', 'object_id')
   
class Dimension (models.Model):
  class Meta:
    abstract = True

  name = models.CharField(max_length=64)
  
  def get_content_type(self):
    return ContentType.objects.get_for_model(self).id   

@reversion.register()
class NumericDimension (Dimension):

  value = models.IntegerField()

  def update_value(self, value, when):
    with reversion.create_revision():
      self.value = value
      self.save()
      reversion.set_date_created(when)
 
class NumericDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='milestones')
  value = models.IntegerField()

  def on_schedule(self, deadline):
    versions = Version.objects.get_for_object(self.numeric_dimension)
    versions = versions.filter(revision__date_created__lte=deadline)

    dimension_value = self.numeric_dimension.value
    try:
        dimension_value = versions[0].field_dict["value"]
    except IndexError:
      pass

    return self.value <= dimension_value


@reversion.register(follow=['milestones_dimensions'])
class ProjectMilestone (models.Model):
  deadline = models.DateTimeField()
  
  def on_schedule(self):
    for dimension_milestone in self.dimension_milestones.all():
      if not dimension_milestone.dimension_milestone_object.on_schedule(self.deadline):
        return False

    return True

@reversion.register(follow=['milestones'])
class MilestonesDimension (Dimension):

  milestones = models.ManyToManyField(ProjectMilestone, related_name='milestones_dimensions')

  def set_milestones(self, milestones):
    with reversion.create_revision():
      self.milestones.set(milestones)

class ProjectMilestoneDimensionMilestone (models.Model):
  project_milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='dimension_milestones')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_milestone_object = GenericForeignKey('content_type', 'object_id')

@reversion.register()
class Person (models.Model):
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64)

@reversion.register()
class MembersDimension(Dimension):
  members = models.ManyToManyField(Person)

  def set_members(self, members, when=None):
    with reversion.create_revision():
      self.members.set(members)
      if (when != None):
        reversion.set_date_created(when)

