from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import reversion
from reversion.models import Version


#Model for a Organization
#Id generated automatically
class Organization (models.Model):
  name = models.CharField(max_length=50, primary_key=True)

#Model for a Project instance
#Id generated automatically
class Project (models.Model):
  start_date = models.DateTimeField
  name = models.CharField(max_length=50)
  parent = models.ForeignKey(Organization, null=True)

#Model for a project dimension
class ProjectDimension (models.Model):
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='dimensions')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_object = GenericForeignKey('content_type', 'object_id')

#Model for a Milestone
class ProjectMilestone (models.Model):
  id = models.IntegerField(max_length = 64)
  deadline = models.DateTimeField()
  project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')

  def on_schedule(self):
    for dimension_milestone in self.dimension_milestones.all():
      if not dimension_milestone.dimension_milestone_object.on_schedule(self.deadline):
        return False

    return True

#Model for
class ProjectMilestoneDimensionMilestone (models.Model):
  project_milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='dimension_milestones')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_milestone_object = GenericForeignKey('content_type', 'object_id')

#model for comparisons between milestones and NumericDimension values
class NumericDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(NumericDimension, on_delete=models.CASCADE, related_name='numeric_milestones')
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

#model for comparisons between milestones and DecimalDimension values
class DecimalDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(DecimalDimension, on_delete=models.CASCADE, related_name='decimal_milestones')
  value = models.IntegerField()

#Model for a person
@reversion.register()
class Person (models.Model):
    ID = models.CharField(max_length=11)
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64)

#model for a Dimension to use in comparisons
class Dimension (models.Model):
  class Meta:
    abstract = True

  name = models.CharField(max_length=64)

  def get_content_type(self):
    return ContentType.objects.get_for_model(self).id

#Dimension for project participant management
@reversion.register()
class MembersDimension(Dimension):
  members = models.ManyToManyField(Person)

  def set_members(self, members, when=None):
    with reversion.create_revision():
      self.members.set(members)
      if (when != None):
        reversion.set_date_created(when)

#Dimensions for Integer, Decimal and Text inputs
#set_value needs some minor fixes
#update_value adds timestamp when edited
@reversion.register()
class NumericDimension (Dimension):

  value = models.IntegerField()

  def set_value(self, value, when=None):
    with reversion.create_revision():
      self.value.set(value)
      if (when != None):
        reversion.set_date_created(when)

  def update_value(self, value, when):
    with reversion.create_revision():
      self.value = value
      self.save()
      reversion.set_date_created(when)

@reversion.register()
class DecimalDimension (Dimension):
    value = models.DecimalField(max_digits = 20, decimal_places = 2)

    def set_value(self, value, when=None):
      with reversion.create_revision():
        self.value.set(value)
        if (when != None):
          reversion.set_date_created(when)

    def update_value(self, value, when):
        with reversion.create_revision():
          self.value = value
          self.save()
          reversion.set_date_created(when)

@reversion.register()
class TextDimension (Dimension):
    value = models.TextField()

    def set_value(self, value, when=None):
      with reversion.create_revision():
        self.value.set(value)
        if (when != None):
          reversion.set_date_created(when)

    def update_value(self, value, when):
        with reversion.create_revision():
          self.value = value
          self.save()
          reversion.set_date_created(when)

#Connection between project and a project manager
class ProjectManager(Dimension):
    manager = models.CharField(Person.ID)
    project = models.IntegerField(Project)

#Phase of the project as a list of Milestone IDs
class Phase(Dimension):
    value = models.ManyToManyField(ProjectMilestone.id)

#Storing the project dependencies as list of project IDs
class ProjectDependencies(Dimension):
    value = models.ManyToManyField(Project)

#Task class
#Is person completing task essential?
class Task(NumericDimension):
    task_description = models.TextField()
    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

 #Project size in money
 class SizeMoney(DecimalDimension):

 #Project size in man-days
 class SizeMd(DecimalDimension):

#Project size as impact
class SizeImpact(TextDimension):

#Technologies used in project
class Technology(TextDimension):

#Development model used in project
class DevelopmentMethod(TextDimension):

#Description of the project
class Description(TextDimension):

#Deliverer of the project
class Deliverer(TextDimension):

#Customer of the project
class Customer(TextDimension):
