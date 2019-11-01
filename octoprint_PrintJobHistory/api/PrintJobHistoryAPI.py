# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import tornado
from flask import jsonify, request, make_response, Response, send_file
import flask

import json

import os

import cv2

from datetime import datetime

from octoprint_PrintJobHistory import PrintJobModel, CameraManager
from octoprint_PrintJobHistory.api import Transform2CSV, TransformPrintJob2JSON
from octoprint_PrintJobHistory.common import StringUtils
from octoprint_PrintJobHistory.common.SettingsKeys import SettingsKeys

from octoprint_PrintJobHistory.CameraManager import CameraManager



class PrintJobHistoryAPI(octoprint.plugin.BlueprintPlugin):

	# Converts the Model to JSON
	# def _convertPrintJobHistoryModelsToDict(self, allJobsModels):
	# 	result = []
	# 	for job in allJobsModels:
	# 		# jobAsDict = job.__dict__
	# 		jobAsDict = job.__data__
	#
	# 		jobAsDict["printStartDateTimeFormatted"] =  job.printStartDateTime.strftime('%d.%m.%Y %H:%M')
	# 		jobAsDict["printEndDateTimeFormatted"] =  job.printEndDateTime.strftime('%d.%m.%Y %H:%M')
	# 		# # Calculate duration
	# 		# duration = job.printEndDateTime - job.printStartDateTime
	# 		duration = job.duration
	# 		durationFormatted = StringUtils.secondsToText(duration)
	# 		jobAsDict["durationFormatted"] =  durationFormatted
	#
	# 		allFilements = job.getFilamentFromAssoziation()
	# 		if  allFilements != None:
	# 			filamentDict = allFilements.__data__
	# 			filamentDict["usedLength"] = StringUtils.formatSave("{:.02f}", filamentDict["usedLength"], "")
	# 			filamentDict["usedWeight"] = StringUtils.formatSave("{:.02f}", filamentDict["usedWeight"], "")
	# 			filamentDict["usedCost"] = StringUtils.formatSave("{:.02f}", filamentDict["usedCost"], "")
	# 			filamentDict["calculatedLength"] = StringUtils.formatSave("{:.02f}", filamentDict["calculatedLength"], "")
	# 			jobAsDict['filamentModel'] = filamentDict
	#
	# 		allTemperatures = job.getTemperaturesFromAssoziation()
	# 		if not allTemperatures == None and len(allTemperatures) > 0:
	# 			allTempsAsList = list()
	#
	# 			for temp in allTemperatures:
	# 				tempAsDict = dict()
	# 				tempAsDict["sensorName"] = temp.sensorName
	# 				tempAsDict["sensorValue"] = temp.sensorValue
	# 				allTempsAsList.append(tempAsDict)
	#
	# 			jobAsDict["temperatureModels"] = allTempsAsList
	#
	# 		jobAsDict["snapshotFilename"] = CameraManager.buildSnapshotFilename(job.printStartDateTime)
	#
	# 		result.append(jobAsDict)
	# 	return result

	def _updatePrintJobFromJson(self, printJobModel,  jsonData):

		printJobModel.userName = self._getValueFromDictOrNone("userName", jsonData)

		printJobModel.printStartDateTime = datetime.strptime(jsonData["printStartDateTimeFormatted"], "%d.%m.%Y %H:%M")
		printJobModel.printEndDateTime = datetime.strptime(jsonData["printEndDateTimeFormatted"], "%d.%m.%Y %H:%M")

		printJobModel.printStatusResult = self._getValueFromDictOrNone("printStatusResult", jsonData)
		printJobModel.fileName = self._getValueFromDictOrNone("fileName", jsonData)
		printJobModel.filePathName = self._getValueFromDictOrNone("filePathName", jsonData)
		printJobModel.fileSize = self._getValueFromDictOrNone("fileSize", jsonData)
		printJobModel.noteText = self._getValueFromDictOrNone("noteText", jsonData)
		printJobModel.noteDeltaFormat = json.dumps(self._getValueFromDictOrNone("noteDeltaFormat", jsonData))
		printJobModel.noteHtml = self._getValueFromDictOrNone("noteHtml", jsonData)
		printJobModel.printedLayers = self._getValueFromDictOrNone("printedLayers", jsonData)
		printJobModel.printedHeight = self._getValueFromDictOrNone("printedHeight", jsonData)

		# filamentModel = FilamentModel()
		# filamentModel.profileVendor = self._getValueFromDictOrNone("profileVendor", jsonData)
		# filamentModel.diameter = self._getValueFromDictOrNone("diameter", jsonData)
		# filamentModel.density = self._getValueFromDictOrNone("density", jsonData)
		# filamentModel.material = self._getValueFromDictOrNone("material", jsonData)
		# filamentModel.spoolName = self._getValueFromDictOrNone("spoolName", jsonData)
		# filamentModel.spoolCost = self._getValueFromDictOrNone("spoolCost", jsonData)
		# filamentModel.spoolCostUnit = self._getValueFromDictOrNone("spoolCostUnit", jsonData)
		# filamentModel.spoolWeight = self._getValueFromDictOrNone("spoolWeight", jsonData)
		# filamentModel.usedLength = self._getValueFromDictOrNone("usedLength", jsonData)
		# filamentModel.usedCost = self._getValueFromDictOrNone("usedCost", jsonData)
		# filamentModel.calculatedLength = self._getValueFromDictOrNone("calculatedLength", jsonData)
		# filamentModel.printjob_id = printJobModel.databaseId
		# printJobModel.filamentModel = filamentModel

		# temperatureModel = TemperatureModel

		return printJobModel

	# <editor-fold desc="CSV-Stuff">



	# </editor-fold>



	def _getValueFromDictOrNone(self, key, values):
		if key in values:
			return values[key]
		return None

################################################### APIs


	#######################################################################################   DEACTIVATE PLUGIN CHECK
	@octoprint.plugin.BlueprintPlugin.route("/deactivatePluginCheck", methods=["PUT"])
	def put_pluginDependencyCheck(self):
		self._settings.setBoolean([SettingsKeys.SETTINGS_KEY_PLUGIN_DEPENDENCY_CHECK], False)
		self._settings.save()

		return flask.jsonify([])


	#######################################################################################   LOAD ALL JOBS BY QUERY
	@octoprint.plugin.BlueprintPlugin.route("/loadPrintJobHistoryByQuery", methods=["GET"])
	def get_printjobhistoryByQuery(self):

		tableQuery = flask.request.values
		allJobsModels = self._databaseManager.loadPrintJobsByQuery(tableQuery)
		# allJobsAsDict = self._convertPrintJobHistoryModelsToDict(allJobsModels)
		allJobsAsDict = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)

		totalItemCount = self._databaseManager.countPrintJobsByQuery(tableQuery)
		return flask.jsonify({
								"totalItemCount": totalItemCount,
								"allPrintJobs": allJobsAsDict
							})

	#######################################################################################   LOAD ALL JOBS
	@octoprint.plugin.BlueprintPlugin.route("/loadPrintJobHistory", methods=["GET"])
	def get_printjobhistory(self):
		allJobsModels = self._databaseManager.loadAllPrintJobs()
		# allJobsAsDict = self._convertPrintJobHistoryModelsToDict(allJobsModels)
		allJobsAsDict = TransformPrintJob2JSON.transformAllPrintJobModels(allJobsModels)

		return flask.jsonify(allJobsAsDict)

	#######################################################################################   DELETE JOB
	@octoprint.plugin.BlueprintPlugin.route("/removePrintJob/<int:databaseId>", methods=["DELETE"])
	def delete_printjob(self, databaseId):
		printJob = self._databaseManager.loadPrintJob(databaseId)
		snapshotFilename = CameraManager.buildSnapshotFilename(printJob.printStartDateTime)
		self._cameraManager.deleteSnapshot(snapshotFilename)
		self._databaseManager.deletePrintJob(databaseId)
		return flask.jsonify()

	#######################################################################################   UPDATE JOB
	@octoprint.plugin.BlueprintPlugin.route("/updatePrintJob/<int:databaseId>", methods=["PUT"])
	def put_printjob(self, databaseId):
		jsonData = request.json
		printJobModel = self._databaseManager.loadPrintJob(databaseId)
		self._updatePrintJobFromJson(printJobModel, jsonData)
		self._databaseManager.updatePrintJob(printJobModel)
		# response = self.get_printjobhistory()
		# return response
		return flask.jsonify()

	#######################################################################################   GET SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/printJobSnapshot/<string:snapshotFilename>", methods=["GET"])
	def get_snapshot(self, snapshotFilename):
		absoluteFilename = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename)
		return send_file(absoluteFilename, mimetype='image/jpg')

	#######################################################################################   TAKE SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/takeSnapshot/<string:snapshotFilename>", methods=["PUT"])
	def put_snapshot(self, snapshotFilename):
		self._cameraManager.takeSnapshot(snapshotFilename)
		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})

	#######################################################################################   UPLOAD SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/upload/snapshot/<string:snapshotFilename>", methods=["POST"])
	def post_snapshot(self, snapshotFilename):

		input_name = "file"
		input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])

		if input_upload_path in flask.request.values:
			# file to restore was uploaded
			sourceLocation = flask.request.values[input_upload_path]
			targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename, False)
			os.rename(sourceLocation, targetLocation)
			pass

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})	\

	#######################################################################################   DELETE SNAPSHOT
	@octoprint.plugin.BlueprintPlugin.route("/deleteSnapshotImage/<string:snapshotFilename>", methods=["DELETE"])
	def delete_snapshot(self, snapshotFilename):

		self._cameraManager.deleteSnapshot(snapshotFilename)

		# input_name = "file"
		# input_upload_path = input_name + "." + self._settings.global_get(["server", "uploads", "pathSuffix"])
		#
		# if input_upload_path in flask.request.values:
		# 	# file to restore was uploaded
		# 	sourceLocation = flask.request.values[input_upload_path]
		# 	targetLocation = self._cameraManager.buildSnapshotFilenameLocation(snapshotFilename)
		# 	os.rename(sourceLocation, targetLocation)
		# 	pass

		return flask.jsonify({
			"snapshotFilename": snapshotFilename
		})


	@octoprint.plugin.BlueprintPlugin.route("/exportPrintJobHistory/<string:exportType>", methods=["GET"])
	def exportPrintJobHistoryData(self, exportType):

		if exportType == "CSV":
			allJobsModels = self._databaseManager.loadAllPrintJobs()
			# allJobsDict = self._convertPrintJobHistoryEntitiesToDict(allJobsEntities)
			allJobsDict = self._convertPrintJobHistoryModelsToDict(allJobsModels)

			# csvContent = self._convertPrintJobHistoryEntitiesToCSV(allJobsDict)
			csvContent = Transform2CSV.transform2CSV(allJobsDict)

			response = flask.make_response(csvContent)
			response.headers["Content-type"] = "text/csv"
			response.headers["Content-Disposition"] = "attachment; filename=OctoprintPrintJobHistory.csv" # TODO add timestamp


			return response
		else:
			print("BOOOMM not supported type")

		pass





######################################################################### Ab hier Baustelle


	def get_frame(self):

		self.cap = cv2.VideoCapture("http://192.168.178.44:8080/video")
		# self.cap = cv2.VideoCapture("http://192.168.178.44:8080/shot.jpg")
		ret, frame = self.cap.read()

		if ret:
			ret, jpeg = cv2.imencode('.jpg', frame)

			# Record video
			# if self.is_record:
			#     if self.out == None:
			#         fourcc = cv2.VideoWriter_fourcc(*'MJPG')
			#         self.out = cv2.VideoWriter('./static/video.avi',fourcc, 20.0, (640,480))

			#     ret, frame = self.cap.read()
			#     if ret:
			#         self.out.write(frame)
			# else:
			#     if self.out != None:
			#         self.out.release()
			#         self.out = None

			return jpeg.tobytes()

		else:
			return None

	global_frame = None


	def video_stream(self):
		from time import sleep
		global video_camera
		global global_frame

		# while True:
		yield "1"
		sleep(4)
		yield "2"
		sleep(4)
		yield "3"
		# if video_camera == None:
		# 	video_camera = VideoCamera()

		# while True:
		# frame = self.get_frame()
		#
		# if frame != None:
		# 	global_frame = frame
		# 	yield (b'--frame\r\n'
		# 		   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		# else:
		# 	yield (b'--frame\r\n'
		# 		   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

	from flask import stream_with_context, request, Response



	@octoprint.plugin.BlueprintPlugin.route('/stream')
	def streamed_response(self):


		# app = tornado.web.Application([
		# 	(r'/', HtmlPageHandler),
		# 	(r'/videofeed', StreamHandler)
		# ])
		# app.listen(9090)
		# pass

		def generate():
			from time import sleep
			yield "1"
			sleep(4)
			yield "2"
			sleep(4)
			yield "3"
		return Response(generate(),mimetype='text/event-stream')

	@octoprint.plugin.BlueprintPlugin.route("/myvideo")
	def video_feed(self):
		# return the response generated along with the specific media
		# type (mime type)
		return Response(self.video_stream(),
						mimetype="text/plain")
						# mimetype='multipart/x-mixed-replace; boundary=frame')





