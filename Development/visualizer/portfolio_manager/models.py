from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import reversion
from reversion.models import Version
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

#Model for a Organization
#Id generated automatically
class Organization (models.Model):
  name = models.CharField(max_length=50, primary_key=True)

#Model for a Project instance
#Id generated automatically
class Project (models.Model):
  name = models.CharField(max_length=50)
  parent = models.ForeignKey(Organization, null=True)

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
    with reversion.create_revision():
      self.value = value
      self.save()
      if (when != None):
        reversion.set_date_created(when)  

#Dimensions for Integer, Decimal and Text inputs
#update_value adds timestamp when edited
@reversion.register()
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


@reversion.register(follow=['milestones_dimensions'])
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


@reversion.register(follow=['milestones'])
class MilestonesDimension (Dimension):

  milestones = models.ManyToManyField(ProjectMilestone, related_name='milestones_dimensions')

  def set_milestones(self, milestones):
    with reversion.create_revision():
      self.milestones.set(milestones)

#Model for
class ProjectMilestoneDimensionMilestone (models.Model):
  project_milestone = models.ForeignKey(ProjectMilestone, on_delete=models.CASCADE, related_name='dimension_milestones')
  content_type = models.ForeignKey(ContentType)
  object_id = models.PositiveIntegerField()
  dimension_milestone_object = GenericForeignKey('content_type', 'object_id')

@reversion.register()
class Person (models.Model):
  first_name = models.CharField(max_length=64)
  last_name = models.CharField(max_length=64)

  def __unicode__(self):
    return self.first_name+" "+self.last_name

  def __str__(self):
    return unicode(self).encode('utf-8')

#Dimension for project participant management
@reversion.register()
class MembersDimension(Dimension):
  members = models.ManyToManyField(Person)

  def set_members(self, members, when=None):
    with reversion.create_revision():
      self.members.set(members)
      if (when != None):
        reversion.set_date_created(when)

@reversion.register()
class DecimalDimension (Dimension):
    value = models.DecimalField(max_digits = 20, decimal_places = 2)

#model for comparisons between milestones and DecimalDimension values
class DecimalDimensionMilestone (models.Model):
  numeric_dimension = models.ForeignKey(DecimalDimension, on_delete=models.CASCADE, related_name='decimal_milestones')
  value = models.IntegerField()

@reversion.register()
class TextDimension (Dimension):
    value = models.TextField()

@reversion.register()
class AssociatedPersonDimension (Dimension):
  value = models.ForeignKey(Person, null=True)

#Connection between project and a project owner
@reversion.register(follow=['associatedpersondimension_ptr'])
class ProjectOwnerDimension (AssociatedPersonDimension):
    pass

#Connection between project and a project manager
@reversion.register(follow=['associatedpersondimension_ptr'])
class ProjectManagerDimension (AssociatedPersonDimension):
    pass

#Storing the project dependencies as list of project IDs
@reversion.register()
class ProjectDependenciesDimension(Dimension):
    dependencies = models.ManyToManyField(Project)

    def set_dependencies(self, dependencies, when=None):
      with reversion.create_revision():
        self.dependencies.set(dependencies)
        self.save()
        if (when != None):
          reversion.set_date_created(when)

#Task class
#Is person completing task essential?
class Task (Dimension):
    task_description = models.TextField()
    value = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])

#Project size in money
@reversion.register(follow=['decimaldimension_ptr'])
class SizeMoneyDimension (DecimalDimension):
  pass

#Project size in man-days
@reversion.register(follow=['decimaldimension_ptr'])
class SizeMd(DecimalDimension):
  pass

#Project size as impact
@reversion.register(follow=['textdimension_ptr'])
class SizeImpactDimension(TextDimension):
  pass

#Technologies used in project
@reversion.register(follow=['textdimension_ptr'])
class TechnologyDimension(TextDimension):
  pass

#Development model used in project
@reversion.register(follow=['textdimension_ptr'])
class DevelopmentMethodDimension(TextDimension):
  pass

#Description of the project
@reversion.register(follow=['textdimension_ptr'])
class DescriptionDimension(TextDimension):
  pass

class Supplier(models.Model):
  name = models.CharField(max_length=50)

#Deliverer of the project
@reversion.register()
class SuppliersDimension(Dimension):
  suppliers = models.ManyToManyField(Supplier)

  def set_suppliers(self, suppliers, when=None):
    with reversion.create_revision():
      self.suppliers.set(suppliers)
      self.save()
      if (when != None):
        reversion.set_date_created(when)

#Customer of the project
@reversion.register(follow=['textdimension_ptr'])
class CustomerDimension(TextDimension):
  pass

#Phase of the project as a list of Milestone IDs
@reversion.register(follow=['textdimension_ptr'])
class PhaseDimension (TextDimension):
  pass

@reversion.register(follow=['textdimension_ptr'])
class OwningOrganizationDimension (TextDimension):
  pass

@reversion.register()
class StartTimeDimension (Dimension):
  value = models.DateTimeField()