import os
import subprocess
import shutil
import Levenshtein
import zipfile
import re

fileFolder = "/files"
extractedFolder = "/extracted"
compiledFolder = "/bin"
logFolder = "/log"
logFileName = "log.txt"
inputFileTemplate = "input"
outputFileTemplate = "output"

def compileCode(fileName, folderLoc, compiledLoc):
	# Copy elif to add new extensions
	if (fileName[1] == "py"):
		shutil.copyfile(folderLoc+"/"+fileName[2], compiledLoc+"/"+fileName[2])
	elif (fileName[1] == "cpp"):
		# Compile
		result = subprocess.run(["g++", folderLoc+"/"+fileName[2], "-o", compiledLoc+"/"+fileName[0].strip()+".bin"],capture_output=True)
		
		# Logging
		if(result.returncode != 0):
			writeLog("[ERR] " + fileName[2] + " compile failed with error:\n" + str(result.stderr) + "\n")
		else:
			# shutil.move(folderLoc+"/"+fileName[0]+".bin", os.curdir + compiledFolder + "/"+ fileName[0]+".bin")
			writeLog("[INFO] " + fileName[2] + " compile success!" )

	elif (fileName[1] == "f90" or fileName[1] == "f95"):
		# Compile
		result = subprocess.run(["gfortran", folderLoc+"/"+fileName[2], "-o", compiledLoc+"/"+fileName[0].strip()+".bin"],capture_output=True)
		
		# Logging
		if(result.returncode != 0):
			writeLog("[ERR] " + fileName[2] + " compile failed with error:\n" + str(result.stderr) + "\n")
		else:
			# shutil.move(folderLoc+"/"+fileName[0]+".bin", os.curdir + compiledFolder + "/"+ fileName[0]+".bin")
			writeLog("[INFO] " + fileName[2] + " compile success!" )

def runCode(filename, location, inputText, outputFile):
	outputText = open(outputFile, "r+").read().lower()
	filenamearr = splitFileName(filename)

	runlogfilename = os.curdir+logFolder+"/"+filenamearr[0]+".txt"
	writeLog("Grading with "+ inputText +" : ", runlogfilename)
	writeLog("Output expected : ", runlogfilename)
	writeLog(outputText, runlogfilename)
	writeLog("...", runlogfilename)

	name = filenamearr[0]
	fileExt = filenamearr[1]
	# Run Process
	if(fileExt == "py"):
		proc = subprocess.Popen(["python", location+"/"+filename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		proc2 = subprocess.Popen(["python3", location+"/"+filename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
	elif(fileExt == "bin"):
		proc = subprocess.Popen([location+"/"+filename], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		proc2 = None
	else:
		proc = None

	timeoutSec = 0.5

	# Communicate with process
	if(proc != None):
		returnCode = 0
		try:
			outs,errs = proc.communicate(timeout=timeoutSec,input=bytes(inputText,"ascii"))
			returnCode = proc.returncode
			# Handle Python3 code
			if(proc2 != None and proc.returncode != 0):
				outs,errs = proc2.communicate(timeout=timeoutSec,input=bytes(inputText,"ascii"))
				returnCode = proc.returncode
				writeLog("Python3 - exit code : "+ str(proc2.returncode), runlogfilename)
			elif(proc2 != None):
				writeLog("Python2 - exit code : "+ str(proc.returncode), runlogfilename)
			else:
				writeLog("BinaryFile - exit code : "+ str(proc.returncode), runlogfilename)

		# Handle timeout
		except subprocess.TimeoutExpired:
			writeLog(" : "+ str(proc2.returncode), runlogfilename)
			writeLog("[INFO] "+name + " reached timeout of " + str(timeoutSec) + " seconds\n", runlogfilename)
			proc.kill()
			outs,errs = proc.communicate()
			returnCode = proc.returncode
		
		# Write logs : result, return code, error message, score
		resultUpper = outs.decode('ascii').lower()
		writeLog(file + " : \n" + resultUpper, runlogfilename)
		writeLog("***\n\n", runlogfilename)
		writeLog("ReturnCode : " + str(returnCode), runlogfilename)
		
		if(returnCode != 0):
			writeLog("[ERR] " + errs.decode('ascii'), runlogfilename)

		writeLog("Score : ", runlogfilename)
		writeLog("==================================\n\n", runlogfilename)


def createFolder(path, folderName, delete=False):
	listed = listFiles(path)
	if(delete):
		if(folderName in listed["dirs"]):
			shutil.rmtree(path+folderName)
		os.mkdir(path+folderName)
	else :
		if(folderName not in listed["dirs"]):
			os.mkdir(path+folderName)

def unzipFiles(fullpathFile, destinationFolder):
	file = zipfile.ZipFile(fullpathFile,"r")
	file.extractall

def listFiles(relativePath):
	walkTuple = os.walk(os.curdir+relativePath)
	listItem = list(map(list,walkTuple))
	listItem = listItem[0]

	return {
		"dirs" : listItem[1],
		"files" : listItem[2]
	}

# [name, ext, fullname]
def splitFileName(fullname):
	fileName = fullname.split(".")
	fileName.append(fullname)
	return fileName

def writeLog(text, logDest=logFileName):
	logFile = open(logDest,"a+").read()
	logFile.write(str(text)+"\n")

# main
if __name__ == "__main__":
	homeFolders = listFiles("")

	uploadedFolders = listFiles(fileFolder)
	print(uploadedFolders)

	# Extract file
	for folder in uploadedFolders:
		fileList = listFiles(fileFolder+"/"+folder)
		for file in fileList["files"]:
			if(splitFileName(file)[1] == "zip"):
				try :
					unzipFiles(fileFolder+"/"+folder+"/"+file, extractedFolder)
				except zipfile.BadZipFile:
					writeLog("[ERR] Failed to extract "+file)
	
	# Compile all files
	extractedFiles = listFiles(extractedFolder)
	for file in extractedFiles["files"]:
		compileCode(file, os.curdir+extractedFolder, os.curdir+compiledFolder)

	# Run, categorize, and write log
	compiledFiles = listFiles(compiledFolder)
	for file in compiledFiles["files"]:
		filenamearr = splitFileName(file)
		filename = filenamearr[0].split("-")
		nim = filename[1]
		probno = filename[-1:]

		r = re.compile("input"+str(int(probno))+"[a-z].*")
		inputFiles = list(filter(r.match, homeFolders["files"]))

		for inputfile in inputFiles:
			print(inputfile)
			runCode(file, os.curdir+compiledFolder, inputFileTemplate+str(int(probno))+".txt", outputFileTemplate+str(int(probno))+".txt")
		
		createFolder(compiledFolder, str(nim))
		shutil.move(os.curdir+compiledFolder+"/"+str(nim)+"/"+file, os.curdir + compiledFolder + "/"+ file)

	