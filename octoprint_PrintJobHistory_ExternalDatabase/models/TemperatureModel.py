# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory_ExternalDatabase.models.BaseModel import BaseModel
from octoprint_PrintJobHistory_ExternalDatabase.models.PrintJobModel import PrintJobModel
from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField


class TemperatureModel(BaseModel):

	printJob = ForeignKeyField(PrintJobModel, related_name='temperatures', on_delete='CASCADE')

	sensorName = CharField(null=False)
	sensorValue = CharField(null=False)	# TODO needs to be refactored to float

