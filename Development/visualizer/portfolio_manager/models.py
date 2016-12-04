from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

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

class ProjectMilestone (models.Model):
  deadline = models.DateTimeField()
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')

  def on_schedule(self):
    for dimension_milestone in self.dimension_milestones.all():
      if not dimension_milestone.dimension_milestone_object.on_schedule(self.deadline):
        return False

    return True

class ProjectMilestoneDimensionMilestone (models.Model):
  project_milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='dimension_milestones')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_milestone_object = GenericForeignKey('content_type', 'object_id')
   
class Dimension (models.Model):
  class Meta:
    abstract = True

  name = models.CharField(max_length=64)
  
  def get_content_type(self):
    return ContentType.objects.get_for_model(self).id

class DimensionChange(models.Model):
  class Meta:
    abstract = True

  created_at = models.DateTimeField(auto_now_add=True)
  comment = models.CharField(max_length=256)

class NumericDimension (Dimension):

  initial_value = models.IntegerField()

  def record_change(self, when, change):
    nd_change = NumericDimensionChange()
    nd_change.change = change
    nd_change.numeric_dimension = self
    nd_change.created_at = when
    nd_change.save()

  def get_status(self):
    return self.initial_value + sum(x.change for x in self.changes.all())


class NumericDimensionChange (DimensionChange):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='changes')
  change = models.IntegerField()

class NumericDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='milestones')
  value = models.IntegerField()

  def on_schedule(self, deadline):
    total_change = 0;
    for change in self.numeric_dimension.changes.all():
      if change.created_at <= deadline:
        total_change += change.change

    return self.value <= self.numeric_dimension.initial_value + total_change



