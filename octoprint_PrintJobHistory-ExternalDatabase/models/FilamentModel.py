# coding=utf-8
from __future__ import absolute_import

from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from octoprint_PrintJobHistory.models.BaseModel import BaseModel
# from octoprint_PrintJobHistory.models.PrintJobModel import PrintJobModel
from peewee import CharField, Model, DecimalField, FloatField, DateField, DateTimeField, TextField, ForeignKeyField




class FilamentModel(BaseModel):

	printJob = ForeignKeyField(PrintJobModel, backref='filaments', on_delete='CASCADE')

	vendor = CharField(null=True)
	diameter = FloatField(null=True)
	density = FloatField(null=True)
	material = CharField(null=True)
	spoolName = CharField(null=True)	#datetime 2 char
	spoolCost = FloatField(null=True)	#Char -> FloatField #datetime 2 char not visible, just for the archive
	# spoolCostUnit = CharField(null=True) removed in version 7
	weight = FloatField(null=True)	#char 2 float
	usedLength = FloatField(null=True)
	calculatedLength = FloatField(null=True)
	usedWeight = FloatField(null=True)
	usedCost = FloatField(null=True)
	toolId = CharField(null=True) # since V4

# TODO colorName, density, diameter, spoolWeight -> rename weight
