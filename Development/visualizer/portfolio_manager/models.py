from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import abc
import datetime

# Create your models here.

class Organization (models.Model):
  name = models.CharField(max_length=50, primary_key=True)

class Project (models.Model):
  name = models.CharField(max_length=64)

  def on_schedule(self, when):
    for dimension in self.dimensions.all():
      for milestone in dimension.dimension_object.milestones.all():
        if milestone.deadline <= when:
          if not milestone.on_schedule(when):
            return False

    return True

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

class DimensionProgress(models.Model):
  class Meta:
    abstract = True

  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  comment = models.CharField(max_length=256)

class DimensionMilestone (models.Model):
  class Meta:
    abstract = True
    
  deadline = models.DateTimeField()

class NumericDimension (Dimension):

  initial_value = models.IntegerField()

  def update_progress(self, when, change):
    nd_progress = NumericDimensionProgress()
    nd_progress.change = change
    nd_progress.numeric_dimension = self
    nd_progress.created_at = when
    nd_progress.save()

  def set_milestone(self,when, value):
    milestone = NumericDimensionMilestone()
    milestone.numeric_dimension = self
    milestone.value = value
    milestone.deadline = when
    milestone.save()

  def get_status(self):
    return self.initial_value + sum(x.change for x in self.progressions.all())


class NumericDimensionProgress (DimensionProgress):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='progressions')
  change = models.IntegerField()


class NumericDimensionMilestone (DimensionMilestone):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='milestones')
  value = models.IntegerField()

  def on_schedule(self, when):
    progression = 0;
    for progress in self.numeric_dimension.progressions.all():
      if progress.created_at <= when:
        progression += progress.change

    return self.value <= self.numeric_dimension.initial_value + progression





