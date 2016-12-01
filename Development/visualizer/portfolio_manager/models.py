from __future__ import unicode_literals

from django.db import models

# Create your models here.

#example model
class Organization (models.Model):
    name = models.CharField(max_length=50, primary_key=True)

class Project (models.Model):
    name = models.CharField(max_length=50)
    parent = models.ForeignKey("Organization")

    #startTime = models.DateTimeField(auto_now_add = True)
    #duration = models.IntegerField(default = 0)
