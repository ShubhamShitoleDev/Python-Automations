#################################################################################
#
#  Importing Required Libraries
#
#################################################################################

import os
import sys
import time
import hashlib
import shutil
import schedule


#################################################################################
#
# Function Name : CalculateCheckSum
# Input :         FileName
# Description :   Calculates and returns the MD5 checksum of the specified file
# Return Value :  MD5 checksum in hexadecimal format, or None if the file
#                 could not be read
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def CalculateCheckSum(FileName):
    try:
        fObj = open(FileName,"rb")
    except Exception as e:
        print(f"Automation Error : Unable to read {FileName} : {e}")
        return None

    hObj = hashlib.md5()

    Buffer = fObj.read(1024)
    while(len(Buffer) > 0):
        hObj.update(Buffer)
        Buffer = fObj.read(1024)

    fObj.close()

    return hObj.hexdigest()


#################################################################################
#
# Function Name : BuildFileIndex
# Input :         DirectoryPath
# Description :   Walks the given directory recursively and builds a dictionary
#                 mapping each file's relative path to its MD5 checksum
# Return Value :  Dictionary of {RelativePath : CheckSum}
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def BuildFileIndex(DirectoryPath):
    FileIndex = dict()

    for FolderName, SubFolder, FileName in os.walk(DirectoryPath):
        for fname in FileName:
            FullPath = os.path.join(FolderName, fname)
            RelativePath = os.path.relpath(FullPath, DirectoryPath)

            CheckSum = CalculateCheckSum(FullPath)
            if CheckSum is None:
                continue

            FileIndex[RelativePath] = CheckSum

    return FileIndex


#################################################################################
#
# Function Name : SyncDirectories
# Input :         SourcePath, DestPath
# Description :   Compares source and destination directories using checksums
#                 and copies new or modified files from source to destination
# Return Value :  Tuple of (NewFiles, UpdatedFiles, SkippedFiles), or None on
#                 validation failure
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def SyncDirectories(SourcePath, DestPath):
    Ret = os.path.exists(SourcePath)
    if (Ret == True):
        Ret = os.path.isdir(SourcePath)
        if (Ret == False):
            print("Unable to proceed as directory name is existing but it's not directory.")
            return None
    else:
        print("Unable to proceed as there is no such directory with name ", SourcePath)
        return None

    Ret = os.path.exists(DestPath)
    if (Ret == True):
        Ret = os.path.isdir(DestPath)
        if (Ret == False):
            print("Unable to proceed as destination name is existing but it's not directory.")
            return None
    else:
        os.mkdir(DestPath)
        print("Destination directory created successfully.")

    SourceIndex = BuildFileIndex(SourcePath)
    DestIndex = BuildFileIndex(DestPath)

    NewFiles = 0
    UpdatedFiles = 0
    SkippedFiles = 0

    for RelativePath, CheckSum in SourceIndex.items():
        if RelativePath not in DestIndex:
            SrcFile = os.path.join(SourcePath, RelativePath)
            DestFile = os.path.join(DestPath, RelativePath)
            os.makedirs(os.path.dirname(DestFile), exist_ok=True)
            shutil.copy2(SrcFile, DestFile)
            print(f"NEW : {RelativePath}")
            NewFiles += 1

        elif DestIndex[RelativePath] != CheckSum:
            SrcFile = os.path.join(SourcePath, RelativePath)
            DestFile = os.path.join(DestPath, RelativePath)
            os.makedirs(os.path.dirname(DestFile), exist_ok=True)
            shutil.copy2(SrcFile, DestFile)
            print(f"UPDATED : {RelativePath}")
            UpdatedFiles += 1

        else:
            print(f"SKIPPED : {RelativePath}")
            SkippedFiles += 1

    print(f"New : {NewFiles}, Updated : {UpdatedFiles}, Skipped : {SkippedFiles}")

    return NewFiles, UpdatedFiles, SkippedFiles


#################################################################################
#
# Function Name : DataShieldBackup
# Input :         SourcePath, DestPath, LogFolder
# Description :   Runs SyncDirectories and writes a timestamped log file
#                 containing the backup report
# Return Value :  None
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def DataShieldBackup(SourcePath, DestPath, LogFolder):
    Border = "-"*80

    Ret = os.path.exists(LogFolder)
    if (Ret == True):
        Ret = os.path.isdir(LogFolder)
        if (Ret == False):
            print("Unable to proceed as log folder name is existing but it's not directory.")
            return
    else:
        os.mkdir(LogFolder)
        print("Log directory created successfully.")

    timeStamp = time.strftime("%Y-%m-%d_%H_%M_%S")
    FileName = os.path.join(LogFolder, "Marvellous_%s.log" % timeStamp)

    Result = SyncDirectories(SourcePath, DestPath)

    if Result is None:
        print("Automation Error : Sync could not be completed, log not created.")
        return

    NewFiles, UpdatedFiles, SkippedFiles = Result

    fobj = open(FileName, "w")
    print(f"Logs file gets successfully created with name {FileName}.")

    fobj.write(Border+"\n")
    fobj.write("---Marvellous Data Shield Backup System----\n")
    fobj.write("Log file gets created at : "+timeStamp+"\n")
    fobj.write(Border+"\n\n")
    fobj.write(f"Source Directory : {SourcePath}\n")
    fobj.write(f"Destination Directory : {DestPath}\n")
    fobj.write(Border+"\n")
    fobj.write("-------------Backup Report-------------\n")
    fobj.write(f"New files copied : {NewFiles}\n")
    fobj.write(f"Updated files copied : {UpdatedFiles}\n")
    fobj.write(f"Skipped files (already synced) : {SkippedFiles}\n")
    fobj.write(Border+"\n")
    fobj.write("-------------End of Log File-------------\n")
    fobj.write(Border+"\n")

    fobj.close()


#################################################################################
#
# Function Name : main
# Input :         Command line arguments
# Description :   It controls the script
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def main():
    Border = "-"*80
    print(Border)
    print("---Marvellous Data Shield Backup System----")
    print(Border)

    if(len(sys.argv) == 2):
        if(sys.argv[1].lower() == "--h"):
            print("This automation script is used to perform : ")
            print("1 : It backs up a source directory to a destination directory.")
            print("2 : It uses MD5 checksums to detect new and modified files.")
            print("3 : It copies only new or changed files, skipping unchanged ones.")
            print("4 : It maintains all records into a log file.")
            print("5 : It gets auto scheduled periodically.")
        elif(sys.argv[1].lower() == "--u"):
            print("Use automation script as : ")
            print(f"python {sys.argv[0]} Time_Interval SourcePath DestPath LogFolder")
            print("Time_Interval : Time in minutes for periodic execution.")
            print("SourcePath : Directory to back up.")
            print("DestPath : Directory where backup will be stored.")
            print("LogFolder : Directory where log files will be saved.")
        else:
            print("Unable to proceed as there is no matching arguments")
            print("Please use --h or --u flag for getting more details")

    elif(len(sys.argv) == 5):
        if not sys.argv[1].isdigit():
            print("Automation Error : Time_Interval must be a number.")
        elif not os.path.exists(sys.argv[2]) or not os.path.isdir(sys.argv[2]):
            print(f"Automation Error : {sys.argv[2]} is not a valid source directory.")
        else:
            print("Schedular started successfully")
            print("Press Ctrl + C to abort the automation script")
            schedule.every(int(sys.argv[1])).minutes.do(DataShieldBackup, sys.argv[2], sys.argv[3], sys.argv[4])

            while True:
                schedule.run_pending()
                time.sleep(1)

    else:
        print("Invalid number of arguments")
        print("Please use --h or --u flag for getting more details")

    print(Border)
    print("--Thank you for using our automation System----")
    print(Border)


#################################################################################
#
#  Starter of the automation script
#
#################################################################################

if __name__ == "__main__":
    main()