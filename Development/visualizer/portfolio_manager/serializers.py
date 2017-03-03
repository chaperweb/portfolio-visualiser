from rest_framework import serializers
from portfolio_manager.models import *


class DimensionObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, DecimalDimension):
            serializer = DecimalDimensionSerializer(value)
        elif isinstance(value, TextDimension):
            serializer = TextDimensionSerializer(value)
        elif isinstance(value, DateDimension):
            serializer = DateDimensionSerializer(value)
        elif isinstance(value, AssociatedPersonDimension):
            serializer = AssociatedPersonSerializer(value)
        elif isinstance(value, AssociatedOrganizationDimension):
            serializer = AssociatedOrganizationSerializer(value)
        elif isinstance(value, AssociatedPersonsDimension):
            serializer = AssociatedPersonsSerializer(value)
        elif isinstance(value, AssociatedProjectsDimension):
            serializer = AssociatedProjectsSerializer(value)
        else:
            raise Exception('Unexpected type of dimesion object: '+value.__class__.__name__)

        return serializer.data

class DecimalDimensionHistorySerializer(serializers.ModelSerializer):

  value = serializers.DecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)

  class Meta:
    model = HistoricalDecimalDimension
    fields = ('id', 'value', 'history_date')

class DecimalDimensionSerializer(serializers.ModelSerializer):

  history = DecimalDimensionHistorySerializer(many=True)

  class Meta:
    model = DecimalDimension
    fields = ('name', 'history')


class TextDimensionHistorySerializer(serializers.ModelSerializer):

  value = serializers.CharField()

  class Meta:
    model = HistoricalTextDimension
    fields = ('id', 'value', 'history_date')

class TextDimensionSerializer(serializers.ModelSerializer):

  history = TextDimensionHistorySerializer(many=True)

  class Meta:
    model = TextDimension
    fields = ('name', 'history')

class DateDimensionHistorySerializer(serializers.ModelSerializer):

  value = serializers.DateTimeField()

  class Meta:
    model = HistoricalDateDimension
    fields = ('id', 'value', 'history_date')

class DateDimensionSerializer(serializers.ModelSerializer):

  history = DateDimensionHistorySerializer(many=True)

  class Meta:
    model = DateDimension
    fields = ('name', 'history')

class PersonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name')

class AssociatedPersonHistorySerializer(serializers.ModelSerializer):

  value = PersonSerializer(many=False, read_only=True)

  class Meta:
    model = HistoricalAssociatedPersonDimension
    fields = ('id', 'value', 'history_date')

class AssociatedPersonSerializer(serializers.ModelSerializer):

  history = AssociatedPersonHistorySerializer(many=True)

  class Meta:
    model = AssociatedPersonDimension
    fields = ('name', 'history')


class AssociatedPersonsSerializer(serializers.ModelSerializer):

  persons = PersonSerializer(many=True, read_only=True)

  class Meta:
    model = AssociatedPersonsDimension
    fields = ('name', 'persons')

class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ('name',)

class AssociatedOrganizationHistorySerializer(serializers.ModelSerializer):

  value = OrganizationSerializer(many=False, read_only=True)

  class Meta:
    model = HistoricalAssociatedOrganizationDimension
    fields = ('id', 'value', 'history_date')

class AssociatedOrganizationSerializer(serializers.ModelSerializer):

  history = AssociatedOrganizationHistorySerializer(many=True)

  class Meta:
    model = AssociatedOrganizationDimension
    fields = ('name', 'history')

class AssociatedProjectsSerializer(serializers.ModelSerializer):

  projects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

  class Meta:
    model = AssociatedProjectsDimension
    fields = ('name', 'projects')

class ProjectDimensionSerializer(serializers.ModelSerializer):

    dimension_object = DimensionObjectRelatedField(read_only=True)

    class Meta:
        model = ProjectDimension
        fields = ('id', 'dimension_object')

class DecimalMilestoneSerializer(serializers.ModelSerializer):

  class Meta:
    model = DecimalMilestone
    fields = ('value',)

class DimensionMilestoneObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, DecimalMilestone):
            serializer = DecimalMilestoneSerializer(value)
        else:
            raise Exception('Unexpected type of dimesion milestone object: '+value.__class__.__name__)

        return serializer.data


class DimensionMilestoneSerializer(serializers.ModelSerializer):

  dimension_milestone_object = DimensionMilestoneObjectRelatedField(read_only=True)

  class Meta:
    model = DimensionMilestone
    fields = ('dimension_milestone_object', 'project_dimension')

class MilestoneHistorySerializer(serializers.ModelSerializer):

  dimensions = DimensionMilestoneSerializer(many=True)

  class Meta:
    model = HistoricalMilestone
    fields = ('history_date', 'due_date', 'dimensions')

class MilestoneSerializer(serializers.ModelSerializer):

  history = MilestoneHistorySerializer(many=True)

  class Meta:
    model = Milestone
    fields = ('history','id')

class ProjectSerializer(serializers.ModelSerializer):

    dimensions = ProjectDimensionSerializer(many=True)
    milestones = MilestoneSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'dimensions', 'milestones')





        