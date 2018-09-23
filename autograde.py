import os
import subprocess
import shutil
import Levenshtein
import zipfile

def compileCode(fileName):
	logFile = open("log.txt","w")
	if (fileName[1] == "py"):
		shutil.copyfile(fileName[2],"./bin/"+ fileName[2])
	elif (fileName[1] == "cpp"):
		print(["gcc", fileName[2], "-o "+ fileName[0]+".bin"])
		result = subprocess.run(["g++", fileName[2], "-o"+ fileName[0].strip()+".bin"],capture_output=True)
		print(fileName[2] + ":" + str(result.returncode))

		if(result.returncode != 0):
			logFile.write(fileName[2] + ":" + str(result.stderr))
		else:
			shutil.move(fileName[0]+".bin","./bin/"+fileName[0]+".bin")
	elif (fileName[1] == "f90" or fileName[1] == "f95"):
		print(["gcc", fileName[2], "-o "+ fileName[0]+".bin"])
		result = subprocess.run(["g++", fileName[2], "-o"+ fileName[0].strip()+".bin"],capture_output=True)
		print(fileName[2] + ":" + str(result.returncode))

		if(result.returncode != 0):
			logFile.write(fileName[2] + ":" + str(result.stderr))
		else:
			shutil.move(fileName[0]+".bin","./bin/"+fileName[0]+".bin")

	
	logFile.close()


def runCode(inputText, outputText):
	runLog = open('runLog.txt',"w")
	outputText = outputText.lower()
	maxScore = Levenshtein.distance('',outputText)
	runLog.write("Maximum Score : "+str(maxScore)+"\n")
	runLog.write("=================================\n")

	# List all files in folder
	binList = os.walk(os.path.relpath("bin",start=os.getcwd()))
	listItem = list(map(list,binList))
	listItem = listItem[0]
	files = listItem[2]
	
	scoring = []

	for file in files:
		fileExt = file.split(".")[1]        
		# Run Process
		if(fileExt == "py"):
			proc = subprocess.Popen(["python", file], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			proc2 = subprocess.Popen(["python3", file], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
		elif(fileExt == "bin"):
			proc = subprocess.Popen(["./bin/"+file], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
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
					print(file + " using python3 and returns " + str(proc2.returncode))

			# Handle timeout
			except subprocess.TimeoutExpired as e:
				runLog.write(file + " reached timeout of " + str(timeoutSec) + " seconds\n")
				proc.kill()
				outs,errs = proc.communicate()
				returnCode = proc.returncode
			
			# Write logs : result, return code, error message, score
			if(len(outs)<=1000):
				resultUpper = outs.decode('ascii').lower()
				runLog.write(file + " : \n" + resultUpper + "\n")
			runLog.write("***\n\n")
			
			runLog.write("ReturnCode : " + str(returnCode)+"\n")
			
			if(returnCode != 0):
				runLog.write("Error : " + errs.decode('ascii')+"\n")
			
			score = maxScore - Levenshtein.distance(resultUpper,outputText)

			runLog.write("Score : " + str(score)+"\n")
			runLog.write("==================================\n\n")

			# Append for csv
			nim = str(file.split("-")[2])
			scoring.append([str(nim).split(".")[0], str(returnCode), str(score)])

	runLog.write("nim, returnCode, score\n")
	for s in scoring:
		runLog.write(s[0]+","+s[1]+","+s[2]+"\n")
	runLog.close()


def createFolder(path, folderName, dirlist):
	if(folderName in dirs):
		shutil.rmtree(path+folderName)
	os.mkdir(path+folderName)

# main
if __name__ == "__main__":
	walkTuple = os.walk(os.curdir)
	listItem = list(map(list,walkTuple))
	listItem = listItem[0]

	files = listItem[2]
	dirs = listItem[1]

	if(not("input.txt" in files)):
		raise ValueError("input.txt not found")

	#createFolder("./", "bin", dirs)

	for file in files:
		fileName = file.split(".")
		fileName.append(file)
		#compileCode(fileName)
	
	inputText = open("input.txt","r").read()
	outputText = open("output.txt","r").read()
	runCode(inputText, outputText)

	