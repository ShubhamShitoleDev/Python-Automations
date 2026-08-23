#################################################################################
#
#  Importing Required Libraries
#
#################################################################################
import os
import time
import sys
import schedule

#################################################################################
#
# Function Name : DirectoryScanner
# Input :         Name of Directory
# Description :   Scans given directory recursively, logs details of every
#                 file, and deletes files whose size is zero bytes
# Date :          23-Aug-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################
def DirectoryScanner(DirectoryPath):
    Border = "-"*80

    Ret = os.path.exists(DirectoryPath)
    if(Ret == False):
        print("Automation Error : There is no such directory with name ", DirectoryPath)
        return

    Ret = os.path.isdir(DirectoryPath)
    if(Ret == False):
        print("Automation Error : It is not a directory with name ", DirectoryPath)
        return

    timeStamp = time.strftime("%Y-%m-%d_%H_%M_%S")
    LogFileName = "CleanFiles_%s.log" % timeStamp

    print("Log file gets created with name : ", LogFileName)

    fObj = open(LogFileName, "w")
    fObj.write(Border+"\n")
    fObj.write("Empty File Cleanup Automation Script\n")
    fObj.write("Log file gets created at : "+timeStamp+"\n")
    fObj.write(Border+"\n\n")
    fObj.write("Files from the Directory are : \n\n")
    fObj.write(Border+"\n")

    TotalFiles = 0
    EmptyFiles = 0

    for FolderName, SubFolder, FileName in os.walk(DirectoryPath):
        for fname in FileName:
            TotalFiles = TotalFiles + 1
            fname = os.path.join(FolderName, fname)

            fObj.write(f"{fname} : {os.path.getsize(fname)} bytes\n")

            if(os.path.getsize(fname) == 0):
                EmptyFiles = EmptyFiles + 1
                try:
                    os.remove(fname)
                except Exception as e:
                    fObj.write(f"Unable to delete {fname} : {e}\n")

    fObj.write(Border+"\n")
    fObj.write(f"Total files scanned : {TotalFiles}\n")
    fObj.write(f"Total empty files found and deleted : {EmptyFiles}\n")
    fObj.write(Border+"\n")
    fObj.write("------------- End of Log File -------------\n")
    fObj.write(Border+"\n")
    fObj.close()


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
    print(" Empty File Cleanup Automation Script ")
    print(Border)

    if(len(sys.argv) == 2):
        if(sys.argv[1].lower() == "--h"):
            print("This automation script is used to :")
            print("1 : Recursively scan a given directory.")
            print("2 : Log details of every file found (name and size).")
            print("3 : Detect and delete files with zero byte size.")
            print("4 : Repeat the scan periodically at a given time interval.")
        elif(sys.argv[1].lower() == "--u"):
            print("Please execute the script as : ")
            print(f"python {sys.argv[0]} Time_Interval Directory_Path")
            print("Time_Interval : Time in minutes for periodic execution.")
            print("Directory_Path : Absolute path of the directory to scan.")
        else:
            print("Unable to proceed as there is no matching arguments")
            print("Please use --h or --u flag for getting more details")

    elif(len(sys.argv) == 3):
        print("Schedular started successfully")
        print("Press Ctrl + C to abort the automation script")

        schedule.every(int(sys.argv[1])).minutes.do(DirectoryScanner, sys.argv[2])

        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        print("Invalid number of arguments")
        print("Please use --h or --u for more info")

    print(Border)
    print(" Thank you for using Automation Script ")
    print(Border)

#################################################################################
#
#  Starter of the automation script
#
#################################################################################
if __name__ == "__main__":
    main()
