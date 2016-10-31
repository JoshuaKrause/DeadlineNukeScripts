import sys
import os

def createNukeFile():
	debugOutput("\n---------------------------------------\n")
	debugOutput("CreateNukeFile.py initiated.")
	
	# Job arguments are stored in a text file in the temp folder.
	deadlineTemp = ('%s/AppData/Local/Thinkbox/Deadline7/temp/' % os.path.expanduser('~'))
	nukeArguments = deadlineTemp + 'nukeArguments.txt'
	f = open (nukeArguments, 'r')
	arguments = f.read()
	argumentList = arguments.split(',')
	
	nukeFilePath = argumentList[0].strip()
	inputPath = argumentList[1].strip()
	outputPath = argumentList[2].strip()
	fileName = argumentList[3].strip()
	firstFrame = int(argumentList[4].strip())
	lastFrame = int(argumentList[5].strip())
	interactive = bool(argumentList[6])
	debugOutput("CreateNukeFile.py arguments received.")
	
	# License check.
	if interactive: 
		os.environ['NUKE_INTERACTIVE'] = '1'
	import nuke
	
	nuke.pluginAddPath('./plugins')
	
	# Create a read node. 
	r = nuke.nodes.Read(file=inputPath, first=firstFrame, last=lastFrame, colorspace='AlexaV3LogC')
	
	# Create the sRGB write node.
	w1 = nuke.nodes.Write(file_type = 'mov')
	w1['name'].setValue('Write_ProResLT_mov')
	w1['file'].setValue(outputPath +'/'+ fileName + '_sRGB.mov')
	w1['colorspace'].setValue('sRGB')
	w1['mov32_pixel_format'].setValue({{0} "default (YCbCrA 8-bit 444 Biased (r408))" "RGBA  8-bit" "YCbCrA 8-bit 444 Biased (r408)" "YCbCr  8-bit 422 (2vuy)"})
	w1['mov32_fps'].setValue(23.976)
	w1['mov64_fps'].setValue(23.976)
	w1['meta_codec'].setValue('apcs')
	w1['mov64_write_timecode'].setValue(True)
	w1['checkHashOnRead'].setValue(False)
	w1.setInput(0, r)
	
	# Create the Avid write node.
	w2 = nuke.nodes.Write(file_type = 'mov')
	w2['name'].setValue('Write_DNxHD_LogC_mov')
	w2['file'].setValue(outputPath +'/'+ fileName + '.mov')
	w2['colorspace'].setValue('AlexaV3LogC')
	w2['meta_codec'].setValue('AVdn')
	w2['mov32_codec'].setValue('AVdn')
	w2['mov32_write_timecode'].setValue(True)
	w2['mov32_pixel_format'].setValue({{0} "default (YCbCr  8-bit 422 (2vuy))" "RGBA  8-bit" "RGBA  16-bit (b64a)" "YCbCrA 8-bit 444 Biased (r408)" "YCbCr  8-bit 422 (2vuy)"})
	w2['mov64_codec'].setValue('AVdn')
	w2['mov64_write_timecode'].setValue(True)
	w2['checkHashOnRead'].setValue(False)
	w2.setInput(0, r)
	
	# Save the Nuke file for rendering.
	debugOutput("CreateNukeFile.py file created.")
	nuke.scriptSave(nukeFilePath)
	debugOutput("CreateNukeFile.py file saved: %s" % nukeFilePath)

def debugOutput(string):
	debugOutputFile = open('//VFXLS/DeadlineRepository7/scripts/SDE/debugNukeFile.txt', 'a')
	debugOutputFile.write(string)
	debugOutputFile.write('\n')
	debugOutputFile.close()
	
createNukeFile()