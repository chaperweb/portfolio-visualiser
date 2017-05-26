from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import MaxValueValidator, MinValueValidator
from simple_history.models import HistoricalRecords
from datetime import datetime
import pytz
from simple_history import register
from dateutil.parser import parse
from django.db.models.signals import pre_delete


####        BASES       ####

class BaseDimensionHistory(models.Model):
    class Meta:
        abstract = True

    def string(self):
        return str(self.value)


class BaseHistoricalMilestone(models.Model):
    class Meta:
        abstract = True

    def __getattr__(self, attrname):
        if attrname == 'dimensions':
            return DimensionMilestone.objects.filter(milestone_id=self.id)

        return super(BaseHistoricalMilestone, self).__getattr__(attrname)


####        FIRST LEVEL MODELS          ####

class GoogleSheet (models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(blank=False)


class Project (models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey('Organization', null=True,on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return self.name


class ProjectDimension (models.Model):
    project = models.ForeignKey(Project, null=False, on_delete=models.CASCADE, related_name='dimensions')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    dimension_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return str(self.dimension_object.__class__.__name__)

    def dimension_type(self):
        return self.dimension_object.__class__.__name__

def dimension_cleanup(sender, instance, *args, **kwargs):
    instance.dimension_object.delete()

pre_delete.connect(dimension_cleanup, sender=ProjectDimension)

class Organization (models.Model):
    name = models.CharField(max_length=50, primary_key=True)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.name)


class Person (models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    def __str__(self):
        return str(self.first_name + " " + self.last_name)


class ProjectTemplate(models.Model):
    name = models.CharField(max_length=50)
    organization = models.ForeignKey(Organization, null=False, on_delete=models.CASCADE, related_name='templates')


class ProjectTemplateDimension(models.Model):
    template = models.ForeignKey(ProjectTemplate, null=False, on_delete=models.CASCADE, related_name='dimensions')
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey(ContentType, null=False, on_delete=models.CASCADE)


class Dimension (models.Model):
    class Meta:
        abstract = True

    name = models.CharField(max_length=64)

    def get_content_type(self):
        return ContentType.objects.get_for_model(self)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        self.value = value
        self._history_date = history_date


####        MILESTONES        ####

class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    history = HistoricalRecords(bases=[BaseHistoricalMilestone])
    due_date = models.DateTimeField()
    __history_date = None


class DecimalMilestone(models.Model):
    value = models.DecimalField(max_digits = 20, decimal_places=2)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value):
        self.value = value


class DimensionMilestone(models.Model):
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='dimensions')
    project_dimension = models.ForeignKey(ProjectDimension, on_delete=models.CASCADE, related_name='milestones')
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    dimension_milestone_object = GenericForeignKey('content_type', 'object_id')

def milestone_cleanup(sender, instance, *args, **kwargs):
    instance.dimension_milestone_object.delete()

pre_delete.connect(milestone_cleanup, sender=DimensionMilestone)


####        DIMENSIONS        ####

class TextDimension (Dimension):
    value = models.TextField()
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None


class DecimalDimension (Dimension):
    value = models.DecimalField(max_digits = 20, decimal_places = 2)
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None


class DateDimension (Dimension):
    value = models.DateTimeField()
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None

    def update_date(self, value):
        d = parse(value, dayfirst=True)
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            d = d.replace(tzinfo=pytz.utc)
        self.value = d

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        d = parse(value, dayfirst=True)
        if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
            d = d.replace(tzinfo=pytz.utc)
        self.value = d
        self._history_date = history_date


class AssociatedOrganizationDimension (Dimension):
    value = models.ForeignKey(Organization, null=True)
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        organization = None
        try:
            organization = Organization.objects.get(name=value)
        except Organization.DoesNotExist:
            organization = Organization()
            organization.name = value
            organization.save()

        self.value = organization
        self._history_date = history_date


class AssociatedPersonDimension (Dimension):
    value = models.ForeignKey(Person, null=True)
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        person = None
        try:
            person = Person.objects.get(first_name=value)
        except Person.DoesNotExist:
            person = Person()
            person.first_name = value
            person.save()
        self.value = person
        self._history_date = history_date


class AssociatedPersonsDimension(Dimension):
    persons = models.ManyToManyField(Person)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        self.save()
        self.persons.set([])
        for part in value.split(','):
            person_first_name = part.strip()
            person = None
            try:
                person = Person.objects.get(first_name=person_first_name)
            except Person.DoesNotExist:
                person = Person()
                person.first_name = person_first_name
                person.save()
            self.persons.add(person)

    def __str__(self):
        return str(', '.join([' '.join([ n for n in [p.first_name, p.last_name] if n]) for p in self.persons.all()]))

    def string(self):
        return self.__str__()


class AssociatedProjectsDimension(Dimension):
    projects = models.ManyToManyField(Project)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        self.save()
        self.projects.set([])
        for part in value.split(','):
            project_id = part.strip()
            project = None
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                project = Project()
                project.id = project_id
                project.save()
            self.projects.add(project)

    def string(self):
        return ', '.join([p.name for p in self.projects.all()])
