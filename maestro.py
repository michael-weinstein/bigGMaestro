import easyMultiprocessing
import os


## You will definitely need to fill these in a runtime to make this work. Variable names should be self-explanatory. Let me know if help is needed.
inputFile = ""
outputDirectory = "output"
nickFuryScriptPath = "dsNickFury3.3.py"
pythonCall = "/usr/bin/python3"
genomeID = "HG38"
pamSeq = "NGG"
endClip = 3


class NickFuryParallelRunner:

    def __init__(self, outputDirectory:str, pythonCall:str, nickFuryScriptPath:str, genomeID:str, pamSeq:str, endClip:int=0):
        self.outputDirectory = outputDirectory
        if not os.path.isdir(outputDirectory):
            os.mkdir(outputDirectory)
        self.pythonCall = pythonCall
        self.nickFuryScriptPath = nickFuryScriptPath
        self.genomeID = genomeID
        self.pamSeq = pamSeq
        self.endClip = endClip

    def parallelAgent(self, target:str):
        nickFuryCommand = "%s %s -g %s -p %s --endClip %s -s %s" % (self.pythonCall, self.nickFuryScriptPath, self.genomeID, self.pamSeq, self.endClip, target)
        outputFileName = "%s.txt" %target
        outputFilePath = os.path.join(self.outputDirectory, outputFileName)
        command = "%s > %s" % (nickFuryCommand, outputFilePath)
        returnStatus = os.system(command)  # ***INSECURE*** Never use this with a web-facing interface or untrusted input data, not including protections against shell injections for simplicity's sake here
        if not returnStatus == 0:
            print("***WARNING*** Target sequence %s returned a non-zero exit status of %s" % (target, returnStatus))
        return (target, returnStatus)


def getListOfTargets(inputFilePath:str, failOnBadLines:bool=True):
    if not os.path.isfile(inputFilePath):
        raise FileNotFoundError("Unable to find input file at %s" %inputFilePath)
    inputFile = open(inputFilePath)
    targetCollection = []
    validTargetCharacterSet = {"A", "T", "C", "G", "_"}
    lineNumber = 0
    for line in inputFile:
        lineNumber += 1
        if not line:
            continue
        line = line.strip()
        invalidCharacters = set(line.upper()).difference(validTargetCharacterSet)
        underscoreCount = line.count("_")
        if invalidCharacters:
            warningMessage = "Invalid target characters seen on line %s with target %s.  Invalid characters: %s" %(lineNumber, line, invalidCharacters)
            if failOnBadLines:
                raise ValueError(warningMessage)
            else:
                print("WARNING: SKIPPING LINE. %s" % warningMessage)
                continue
        if underscoreCount != 1:
            warningMessage = "Targets should have one and only one underscore to separate guide and PAM sequences. Line %s target %s was not valid." % (lineNumber, line)
            if failOnBadLines:
                raise ValueError(warningMessage)
            else:
                print("WARNING: SKIPPING LINE. %s" % warningMessage)
                continue
        targetCollection.append(line)
    inputFile.close()
    print("Found %s targets in file %s" %(len(targetCollection), inputFilePath))
    return targetCollection


def main():
    nickFuryRunner = NickFuryParallelRunner(outputDirectory, pythonCall, nickFuryScriptPath, genomeID, pamSeq, endClip)
    targets = getListOfTargets(inputFile)
    results = easyMultiprocessing.parallelProcessRunner(nickFuryRunner.parallelAgent, targets)
    for target, returnCode in results:
        if not returnCode == 0:
            print("Target %s exited with non-zero status of %s" %(target, returnCode))
    return True


if __name__ == "__main__":
    main()
