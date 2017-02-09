from rest_framework import serializers
from models import *


class DimensionObjectRelatedField(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, DecimalDimension):
            serializer = DecimalDimensionSerializer(value)
        elif isinstance(value, TextDimensio):
            serializer = TextDimensionSerializer(value)
        else:
            raise Exception('Unexpected type of dimesion object')

        return serializer.data

class DecimalDimensionMilestoneSerializer(serializers.ModelSerializer):
  class Meta:
    model = DecimalDimensionMilestone
    fields = ('id', 'value', 'at')

class DecimalDimensionHistorySerializer(serializers.ModelSerializer):

  value = serializers.DecimalField(max_digits=20, decimal_places=2, coerce_to_string=False)

  class Meta:
    model = HistoricalDecimalDimension
    fields = ('id', 'value', 'history_date')

class DecimalDimensionSerializer(serializers.ModelSerializer):

  milestones = DecimalDimensionMilestoneSerializer(many=True)
  history = DecimalDimensionHistorySerializer(many=True)

  class Meta:
    model = DecimalDimension
    fields = ('id', 'name', 'milestones', 'history')

class ProjectDimensionSerializer(serializers.ModelSerializer):

    dimension_object = DimensionObjectRelatedField(read_only=True)

    class Meta:
        model = ProjectDimension
        fields = ('id', 'dimension_object')

class ProjectSerializer(serializers.ModelSerializer):

    dimensions = ProjectDimensionSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'dimensions')