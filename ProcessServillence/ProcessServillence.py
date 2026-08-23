#python ProcessServillence.py  2 ProcessServillenceLog
#python ProcessServillence.py  time_interval  Folder_Name
#                 0                1            2

import psutil
import sys
import os
import time
import schedule

def ProcessScan():
    listProcess = list()

    for proc in psutil.process_iter():
        info = proc.as_dict(attrs=["pid","name","username","status"])
        info["cpu_percent"] = proc.cpu_percent(None)
        info["memory_percent"] = proc.memory_percent()

        listProcess.append(info)

    return listProcess


def PlatformSurvillance(FolderName):
    Border = "-"*50

    Ret = False

    Ret = os.path.exists(FolderName)

    if Ret == True:
        Ret = os.path.isdir(FolderName)

        if Ret == False:
            print("Unable to proceed as directory name is existing but it's not directory.")
            return
    else:
        os.mkdir(FolderName)
        print("Directory for log file created sucessfully") 

    timeStamp = time.strftime("%Y-%m-%d_%H_%M_%S")
    FileName = os.path.join(FolderName,"SystemServillence_%s.log"%timeStamp)
    fobj = open(FileName,"w")
    print(f"Logs file gets successfully created with name {FileName}.")

    fobj.write(Border+"\n")
    fobj.write("---Platform Survillence System----\n")
    fobj.write("Log file gets created at : "+timeStamp+"\n")
    fobj.write(Border+"\n\n")
    fobj.write("-------------System Report-------------\n")

    #CPU Info
    fobj.write("Number of active CPU cores are : %s\n" %psutil.cpu_count())
    fobj.write("CPU Usage : %s %%\n" %psutil.cpu_percent())
    fobj.write(Border+"\n")

    #RAM Info
    mobj = psutil.virtual_memory()
    fobj.write("Ram Usage : %s %%\n"%mobj.percent)
    fobj.write("Total Ram available : %s\n"%mobj.total)
    fobj.write(Border+"\n")

    #Disk Info
    fobj.write("Disk Usage Report\n")
    for partition in psutil.disk_partitions():
        try:
            dobj = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            # Some mountpoints (e.g. removable media) may not be ready/accessible
            continue

        fobj.write("Drive : %s\n" % partition.device)
        fobj.write("Mountpoint : %s\n" % partition.mountpoint)
        fobj.write("File System Type : %s\n" % partition.fstype)
        fobj.write("Total Size : %.2f GB\n" % (dobj.total / (1024**3)))
        fobj.write("Used : %.2f GB\n" % (dobj.used / (1024**3)))
        fobj.write("Free : %.2f GB\n" % (dobj.free / (1024**3)))
        fobj.write("Usage : %s %%\n" % dobj.percent)
        fobj.write("-"*20+"\n")

    diskIO = psutil.disk_io_counters()
    if diskIO is not None:
        fobj.write("Disk Read : %.2f MB\n" % (diskIO.read_bytes / (1024*1024)))
        fobj.write("Disk Write : %.2f MB\n" % (diskIO.write_bytes / (1024*1024)))
    fobj.write(Border+"\n")

    #Network info
    netobj = psutil.net_io_counters()
    fobj.write("Network Usage Report\n")
    fobj.write("Sent : %.2f MB\n"%(netobj.bytes_sent / ( 1024 * 1024)))
    fobj.write("Receive : %.2f MB\n"%(netobj.bytes_recv / (1024 * 1024)))
    fobj.write(Border+"\n")

    #Process Log
    data = ProcessScan()

    for info in data:
        fobj.write("PID : %s\n" %info.get("pid"))
        fobj.write("Name : %s\n" %info.get("name"))
        fobj.write("UserName : %s\n" %info.get("username"))
        fobj.write("Status : %s\n" %info.get("status"))
        fobj.write("CPU Usage : %.4f %%\n" %info.get("cpu_percent"))
        fobj.write("RAM Usage: %.4f %%\n" %info.get("memory_percent"))
        fobj.write(Border+"\n")

    fobj.write(Border+"\n")

    fobj.write("-------------End of Log File-------------\n")
 
    fobj.write(Border+"\n")

    fobj.close()


def main():
    Border = "-"*50
    print(Border)
    print("---Platform Survillence System----")
    print(Border)

    #--h and --u handeling
    if(len(sys.argv) == 2):
        if(sys.argv[1].lower() == "--h"):
            print("This automation script is used to perform : ")
            print("1 : It fetch the information of running processess.")
            print("2 : It fetch the information about the primary storage as RAM.")
            print("3 : It fetch the information about the secondary storage as HDD.")
            print("4 : It fetch the information about the microprocessor.")
            print("5 : It maintains all records into log file.")
            print("6 : It gets  auto schedule periodically.")
            print("7 : It sends the log file through mail periodically.")
        elif(sys.argv[1].lower() == "--u"):
            print("Use automation script as : ")
            print(f"python {sys.argv[0]} Time_Interval Folder_Name")
            print("Time_Interval : Time in minute for periodic execution.")
            print("Folder_Name : Name of the folder for the log file creation.")
        else:
            print("Unable to proceed as there is no matching arguments")
            print("Please use --h or --u flag for getting more details")


    #Actual project code
    elif(len(sys.argv) == 3):
        # print("CPU Usage : ",psutil.cpu_percent())
        print("Schedular started successfully")
        print("Press Ctrl + C to abort the automation script")
        schedule.every(int(sys.argv[1])).minute.do(PlatformSurvillance,sys.argv[2])

        while True:
            schedule.run_pending()
            time.sleep(1)
            
    else:
        print("Invalid number of  arguments")
        print("Unable to proceed as there is no matching arguments")
        print("Please use --h or --u flag for getting more details")
     

    print(Border)
    print("--Thank you for using our automation System----")
    print(Border)

if __name__  == "__main__":
    main()
