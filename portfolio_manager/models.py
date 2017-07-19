##
#
# Portfolio Visualizer
#
# Copyright (C) 2017 Codento
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.timezone import get_current_timezone, is_naive, make_aware
from simple_history.models import HistoricalRecords
from dateutil.parser import parse
from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

# Class for getting subclasses of a abstract base class
class GetSubclassesMixin(object):
    @classmethod
    def get_subclasses(cls):
        content_types = ContentType.objects.filter(app_label=cls._meta.app_label)
        models = [ct.model_class() for ct in content_types]
        return [model for model in models
                if (model is not None and
                    issubclass(model, cls) and
                    model is not cls)]


####        BASES       ####

class BaseDimensionHistory(models.Model):
    class Meta:
        abstract = True

    def string(self):
        try:
            return self.value.strftime("%d/%m/%Y %H:%M")
        except:
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

    def __str__(self):
        return str(self.name)

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="person", null=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return str("{} {}".format(self.first_name, self.last_name))

@receiver(post_save, sender=User)
def create_person(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(
            user=instance,
            first_name=instance.first_name,
            last_name=instance.last_name
        )


@receiver(post_save, sender=User)
def save_person(sender, instance, **kwargs):
    instance.person.save()


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

    def get_display_data(self):
        data = {
            'due_date': self.due_date,
            'dimensions': {}
        }
        for dim_miles in self.dimensions.all():
            field = dim_miles.project_dimension.dimension_object.name
            value = dim_miles.dimension_milestone_object.value
            data['dimensions'][field] = value
        return data


class NumberMilestone(models.Model):
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

    def __str__(self):
        return self.value


class NumberDimension (Dimension):
    value = models.DecimalField(max_digits = 20, decimal_places = 2)
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None

    def __str__(self):
        return str(self.value)


class DateDimension (Dimension):
    value = models.DateTimeField()
    history = HistoricalRecords(bases=[BaseDimensionHistory])
    __history_date = None

    def update_date(self, value):
        d = parse(value, dayfirst=True)
        if is_naive(d):
            d = make_aware(d)
        self.value = d

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        d = parse(value, dayfirst=True)
        if is_naive(d):
            d = make_aware(d)
        self.value = d
        self._history_date = history_date

    def __str__(self):
        return self.value.astimezone(get_current_timezone()).strftime("%d/%m/%Y %H:%M")


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


    def __str__(self):
        return str(self.value)

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


    def __str__(self):
        return str(self.value)


class AssociatedPersonsDimension(Dimension):
    value = models.ManyToManyField(Person)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        self.save()
        self.value.set([])
        for part in value.split(','):
            person_first_name = part.strip().split(' ')[0]
            try:
                person_last_name = part.strip().split(' ')[1]
            except:
                person_last_name = ''
            person = None
            try:
                person = Person.objects.get(first_name=person_first_name, last_name=person_last_name)
            except Person.DoesNotExist:
                person = Person()
                person.first_name = person_first_name
                person.last_name = person_last_name
                person.save()
            self.value.add(person)

    def __str__(self):
        return str(', '.join([str(p) for p in self.value.all()]))

    def string(self):
        return self.__str__()


class AssociatedProjectsDimension(Dimension):
    value = models.ManyToManyField(Project)

    # Updates model's value with a value drawn from a Google Sheet
    def from_sheet(self, value, history_date):
        self.save()
        self.value.set([])
        for part in value.split(','):
            project_id = part.strip()
            project = None
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                project = Project()
                project.id = project_id
                project.save()
            self.value.add(project)

    def __str__(self):
        return ', '.join([str(p) for p in self.value.all()])


####        SNAPSHOTS       ####

class Snapshot(GetSubclassesMixin, models.Model):
    SNAPSHOT_TYPES = (
        ('PA', 'Path'),
        ('FF', 'Fourfield'),
    )

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=140)
    snap_type = models.CharField(
        max_length=2,
        choices=SNAPSHOT_TYPES
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['created_at']


class PathSnapshot(Snapshot):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="pathsnapshots"
    )
    content_type_x = models.ForeignKey(ContentType, related_name="ct_x")
    object_id_x = models.PositiveIntegerField()
    dimension_object_x = GenericForeignKey('content_type_x', 'object_id_x')

    content_type_y = models.ForeignKey(ContentType, related_name="ct_y")
    object_id_y = models.PositiveIntegerField()
    dimension_object_y = GenericForeignKey('content_type_y', 'object_id_y')


class FourFieldSnapshot(Snapshot):
    x_dimension = models.CharField(max_length=64)
    y_dimension = models.CharField(max_length=64)
    radius_dimension = models.CharField(max_length=64)
    start_date = models.DateField()
    end_date = models.DateField()
    zoom = models.PositiveIntegerField()
