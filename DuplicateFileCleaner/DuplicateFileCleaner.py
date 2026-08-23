#################################################################################
#
#  Importing Required Libraries
#
#################################################################################

import sys
import schedule
import time
import os
import hashlib
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


#################################################################################
#
# Function Name : LoadEnvironment
# Input :         None
# Description :   Loads the sender email address, app password, and receiver
#                 email address from the .env file
# Return Value :  Email configuration details
# Date :          27-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def LoadEnvironment():
    load_dotenv()

    SENDER = os.getenv("EMAIL_SENDER")
    APP_PASSWORD = os.getenv("EMAIL_PASSWORD")
    RECEIVER = os.getenv("EMAIL_RECEIVER")

    if not SENDER or not APP_PASSWORD or not RECEIVER:
        print("Automation Error : Email configuration is missing or incomplete in .env file.")
        print("Please set EMAIL_SENDER, EMAIL_PASSWORD and EMAIL_RECEIVER before running the script.")
        sys.exit(1)

    return SENDER, APP_PASSWORD, RECEIVER


SENDER, APP_PASSWORD, RECEIVER = LoadEnvironment()


#################################################################################
#
# Function Name : send_mail
# Input :         subject, body, attachment
# Description :   Sends an email with the specified subject, body, and
#                 attachment using the Gmail SMTP server
# Return Value :  None
# Date :          27-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def send_mail(subject, body, attachment=None):
    try:
        msg = EmailMessage()

        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg["Subject"] = subject

        msg.set_content(body)

        if attachment is not None:
            with open(attachment, "rb") as f:
                data = f.read()

            msg.add_attachment(
                data,
                maintype="application",
                subtype="octet-stream",
                filename=os.path.basename(attachment)
            )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER, APP_PASSWORD)
            smtp.send_message(msg)

        print("Email sent successfully.")
    except Exception as e:
        print(f"Automation Error : Unable to send email : {e}")


#################################################################################
#
# Function Name : CalculateCheckSum
# Input :         FileName
# Description :   Calculates and returns the MD5 checksum of the specified file
# Return Value :  MD5 checksum in hexadecimal format, or None if the file
#                 could not be read
# Date :          26-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def CalculateCheckSum(FileName):
    try:
        fObj = open(FileName, "rb")
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
# Function Name : FindDuplicate
# Input :         DirectoryName
# Description :   Scans the specified directory and identifies duplicate files
#                 using their MD5 checksum
# Return Value :  Dictionary containing checksum as key and list of duplicate
#                 file paths as value. Returns None if DirectoryName is
#                 invalid.
# Date :          26-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def FindDuplicate(DirectoryName):
    Ret = os.path.exists(DirectoryName)

    if (Ret == True):
        Ret = os.path.isdir(DirectoryName)

        if (Ret == False):
            print("Unable to proceed as directory name is existing but it's not directory.")
            return None
    else:
        print("Unable to proceed as there is no such directory with name ", DirectoryName)
        return None

    Duplicate = dict()

    for FolderName,SubFolderName,FileName in os.walk(DirectoryName):
        for fName in FileName:
            fName = os.path.join(FolderName,fName)

            CheckSum = CalculateCheckSum(fName)

            if CheckSum is None:
                # File could not be read, skip it
                continue

            if CheckSum in Duplicate:
                Duplicate[CheckSum].append(fName)
            else:
                Duplicate[CheckSum] = [fName]

    return Duplicate


#################################################################################
#
# Function Name : DeleteDuplicate
# Input :         DirectoryName, SaveLogFolder
# Description :   Deletes duplicate files from the specified directory and
#                 creates a log file containing the details of the operation
# Return Value :  None
# Date :          26-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def DeleteDuplicate(DirectoryName,SaveLogFolder):
    Border = "-"*80

    MyDict = FindDuplicate(DirectoryName)

    if MyDict is None:
        # DirectoryName was invalid, FindDuplicate already printed the reason
        return

    if not os.path.exists(SaveLogFolder):
        os.mkdir(SaveLogFolder)
        print("Log directory created successfully.")
    elif not os.path.isdir(SaveLogFolder):
        print("Automation Error: Log path is not a directory.")
        return

    timeStamp = time.strftime("%Y-%m-%d_%H_%M_%S")
    FileName = os.path.join(SaveLogFolder,"Log%s.log"%timeStamp)

    fobj = open(FileName,"w")
    print(f"Logs file gets successfully created with name {FileName}.")
    fobj.write(Border + "\n")
    fobj.write("Duplicate File Removal Automation Script\n")
    fobj.write(f"Date : {timeStamp}\n")
    fobj.write(f"Directory Scanned : {DirectoryName}\n")
    fobj.write("Log file gets created at : "+timeStamp+"\n")
    fobj.write(Border+"\n\n")

    totalDeleted = 0

    Result = list(filter(lambda x : len(x) > 1,MyDict.values()))
    fobj.write("Deleted files:\n")

    for value in Result:
        Count = 0
        for subValue in value:
            Count += 1
            if Count > 1:
                try:
                    os.remove(subValue)
                    totalDeleted += 1
                    fobj.write(subValue + "\n")
                except Exception as e:
                    fobj.write(f"Unable to delete {subValue}: {e}\n")

    fobj.write(Border+"\n")
    fobj.write(f"Total Duplicate files found and deleted : {totalDeleted}\n")
    fobj.write(Border+"\n")
    fobj.write("------------- End of Log File -------------\n")
    fobj.write("\n"+Border+"\n")
    fobj.close()
    send_mail(subject="Duplicate File Removal Report",body="Please find the attached log file.",attachment=FileName)


#################################################################################
#
# Function Name : main
# Input :         Command line arguments
# Description :   It controls the script
# Date :          26-July-2026
# Author :        Shubham Namdev Shitole
#
#################################################################################

def main():
    Border = "-" * 80
    print(Border)
    print(" Duplicate File Removal Automation Script ")
    print(Border)

    if len(sys.argv) == 2:
        if sys.argv[1].lower() == "--h":
            print("This automation script is used to:")
            print("1. Scan the specified directory for duplicate files.")
            print("2. Remove duplicate files automatically.")
            print("3. Save the operation log in the specified log directory.")
            print("4. Execute the scan repeatedly after the given time interval.")
            print("Use --u flag to see the correct usage.")

        elif sys.argv[1].lower() == "--u":
            print("Usage:")
            print("python FileName.py <TimeInterval> <DirectoryName> <LogDirectory>")
            print()
            print("Arguments:")
            print("TimeInterval : Time interval in minutes.")
            print("DirectoryName : Absolute path of the directory to scan.")
            print("LogDirectory : Absolute path where the log file will be saved.")
            print()
            print("Example:")
            print("python FileName.py 5 C:\\Users\\Admin\\Documents C:\\Logs")

        else:
            print("Invalid option. Use --h or --u.")

    elif len(sys.argv) == 4:
        # Validate DirectoryName upfront so errors surface immediately
        # instead of on the first scheduled run.
        if not os.path.exists(sys.argv[2]) or not os.path.isdir(sys.argv[2]):
            print(f"Automation Error : {sys.argv[2]} is not a valid directory.")
        elif not sys.argv[1].isdigit():
            print("Automation Error : TimeInterval must be a number.")
        else:
            print("Schedular started successfully")
            print("Press Ctrl + C to abort the automation script")

            schedule.every(int(sys.argv[1])).minutes.do(DeleteDuplicate,sys.argv[2],sys.argv[3])

            while True:
                schedule.run_pending()
                time.sleep(1)

    else:
        print("Invalid number of arguments.")
        print("Use --h or --u for help.")

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