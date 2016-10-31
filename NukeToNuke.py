# NukeToNuke.py
# v0.01
# by Joshua Krause
# ---------------------------------
# This post-job script grabs the output information from a Nuke image-sequence render
# and resubmits it to Nuke for re-processing into sRGB and DNxHD movie files.

from System.IO import *
from Deadline.Scripting import *
from Deadline.Jobs import *
from Deadline.Plugins import *
import sys
import os
import subprocess
import re

DEADLINE_REPOSITORY = '//VFXLS/DeadlineRepository7/'
DEADLINE_TEMP = ('%s/AppData/Local/Thinkbox/Deadline7/temp/' % os.path.expanduser('~'))

def __main__( *args ):
	debugOutput("\n---------------------------------------\n")
	# Find the current job.
	deadlinePlugin = args[0]
	job = deadlinePlugin.GetJob()
	
	# Get general job information.	
	jobId = job.JobId
	jobName = job.JobName.rsplit('.')[0]
	if job.JobWhitelistFlag:
		whitelist = job.JobListedSlaves
	else:
		whitelist = []
	for each in whitelist:
		debugOutput("Whitelist: %s" % each)
		
	# Get output directories and files.
	outputDirectory = cleanPath(job.JobOutputDirectories[0])
	outputFileName = job.JobOutputFileNames[0]
	
	# Get frame information.
	firstFrame = job.JobFramesList[0]
	lastFrame = job.JobFramesList[-1]
	
	# Create the Nuke file.
	nukeFilePath = cleanPath(DEADLINE_REPOSITORY +'jobs/'+ jobId +'/'+ jobName +'_MOV.nk')
	inputPath = cleanPath(outputDirectory + '/' + outputFileName)
	outputPath = cleanPath(outputDirectory.rsplit('/', 1)[0])
	
	# Check to see which license to use.
	interactiveList = deadlinePlugin.GetConfigEntryWithDefault( 'InteractiveSlaves', '' ).split( ',' )
	for each in interactiveList:
		debugOutput("Interactive: %s" % each)
	
	for interactive in interactiveList:
		for white in whitelist:
			debugOutput(interactive +' : '+ white)
			if interactive == white:
				debugOutput("Interactive license detected.")
				interactiveLicense = True
			else:
				interactiveLicense = False
			
	# Assemble and save the Nuke arguments.
	nukeArgumentsOutput = cleanPath(DEADLINE_TEMP + 'nukeArguments.txt')
	argumentList = [nukeFilePath, inputPath, outputPath, jobName, str(firstFrame), str(lastFrame), str(interactiveLicense)]
	nukeArguments = open(nukeArgumentsOutput, 'w')
	
	for argument in argumentList:
		nukeArguments.write(argument +',\n')
	nukeArguments.close()
	debugOutput("Arguments output to: %s" % nukeArgumentsOutput)
	
	# Get the proper version of Nuke.
	version = deadlinePlugin.GetPluginInfoEntry('Version')
	debugOutput('Nuke version: %s' % str(version))
	executables = deadlinePlugin.GetConfigEntryWithDefault( "RenderExecutable" + str(version).replace( ".", "_" ), "this version is not supported yet" )
	nukePath = FileUtils.SearchFileList(executables).rsplit('/', 1)[0]
	debugOutput("Nuke path: %s" % nukePath)
	nukePythonExe = nukePath + '/python.exe'
	debugOutput('Nuke executable: %s' % nukePythonExe)
	
	# Find the CreateNukeFile.py script and submit it to Nuke's python command line.
	createNukePath = DEADLINE_REPOSITORY + 'scripts/SDE/CreateNukeFile.py'
	debugOutput("Accessed CreateNukeFile.py: %s" % createNukePath)
	
	createNukeCommand = '"'+ nukePythonExe +'" "'+ createNukePath +'"'
	debugOutput("Submitted Nuke command: %s" % createNukeCommand)
	subprocess.call(createNukeCommand)
	
	# Create the job text files.
	plugInInfo = assemblePluginInfo(firstFrame, lastFrame)
	jobInfo = assembleJobInfo(jobName, ','.join(whitelist), outputPath)
	
	# Generate the command and call it.
	command = generateCommand(plugInInfo, jobInfo, nukeFilePath)
	debugOutput("Submitted Deadline command: %s" % command);
	subprocess.call(command)
	
def generateCommand(plugInInfo, jobInfo, nukeFilePath):
	deadlineCommand = os.environ['DEADLINE_PATH'] + '/deadlineCommand.exe'
	return '"'+ deadlineCommand +'" "'+ jobInfo +'" "'+ plugInInfo +'" "'+ nukeFilePath +'"'
	
def cleanPath(path):
	# Replace backslashes with forward slashes.
	return path.replace('\\', '/')
	
def assemblePluginInfo(firstFrame, lastFrame):
	# Write the PlugInInfo file.
	plugFile = unicode(DEADLINE_TEMP, 'utf-8') + (u'nukeToNuke_plugin_info.job')
	pf = open(plugFile, 'w')
	
	pf.write('Version=9.0\n')
	pf.write('Threads=0\n')
	pf.write('RamUse=0\n')
	pf.write('BatchMode=True\n')
	pf.write('BatchModeIsMovie=False\n')
	pf.write('WriteNodesAsSeparateJobs=True\n')
	pf.write('WriteNode0=Write_ProResLT_mov\n')
	pf.write('WriteNode0StartFrame=%s\n' % str(firstFrame))
	pf.write('WriteNode0EndFrame=%s\n' % str(lastFrame))
	pf.write('WriteNode1=Write_DNxHD_LogC_mov\n')
	pf.write('WriteNode1StartFrame=%s\n' % str(firstFrame))
	pf.write('WriteNode1EndFrame=%s\n' % str(lastFrame))
	pf.write('NukeX=False\n')
	pf.write('UseGpu=False\n')
	pf.write('ProxyMode=False\n')
	pf.write('EnforceRenderOrder=False\n')
	pf.write('ContinueOnError=False\n')
	pf.write('PerformanceProfiler=False\n')
	pf.write('PerformanceProfilerDir=\n')
	pf.write('Views=\n')
	pf.write('StackSize=0\n')
	
	# Close the file and return its name.
	pf.close()
	return plugFile
	
def assembleJobInfo(jobName, whitelist, parentDirectory):	
	# Write the job info file.
	jobFile = unicode(DEADLINE_TEMP, 'utf-8') + (u'nukeToNuke_submit_info.job')
	jf = open(jobFile, 'w')
	
	jf.write('Plugin=Nuke\n')
	jf.write('Name=%s_MOV.nk\n' % jobName)
	jf.write('Comment=\n')
	jf.write('Department=\n')
	jf.write('Pool=none\n')
	jf.write('SecondaryPool=\n')
	jf.write('Group=none\n')
	jf.write('Priority=50\n')
	jf.write('MachineLimit=0\n')
	jf.write('TaskTimeoutMinutes=0\n')
	jf.write('EnableAutoTimeout=False\n')
	jf.write('ConcurrentTasks=1\n')
	jf.write('LimitConcurrentTasksToNumberOfCpus=True\n')
	jf.write('LimitGroups=nuke\n')
	jf.write('JobDependencies=\n')
	jf.write('OnJobComplete=Nothing\n')
	jf.write('ForceReloadPlugin=True\n')
	jf.write('Frames=0-1\n')
	jf.write('ChunkSize=1\n')
	jf.write('Whitelist=%s\n' % whitelist)
	jf.write('OutputDirectory0={}/{}_sRGB.mov\n'.format(parentDirectory, jobName))
	jf.write('OutputDirectory1={}/{}_DNxHD.mov\n'.format(parentDirectory, jobName))
	num = 0
	while num <= 9:
		jf.write('ExtraInfo%s=\n' % str(num))
		num += 1

	# Close the file and return its name.
	jf.close()
	return jobFile

def debugOutput(string):
	debugOutputFile = open(DEADLINE_REPOSITORY +'/scripts/SDE/debugSubmissionFile.txt', 'a')
	debugOutputFile.write(string)
	debugOutputFile.write('\n')
	debugOutputFile.close()
