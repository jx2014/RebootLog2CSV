#this is the main program for RebootLog2CSV
#
#Date: 1/12/2016

import sys
import os
import re
import csv
from collections import OrderedDict


class RL2C():
    def __init__(self, log):
        self.logFullPath = log
        if os.path.exists(log) == False:                
            self.__exit__('path does not exist: %s' % log)
        self.logDirectory = os.path.dirname(log) # c:\temp
        self.logName = os.path.basename(log)
        self.logfName, self.logExt = os.path.splitext(self.logName) # abc and .txt
        self.outputName = self.logfName + '_output.csv' # abc_output.csv"
        self.outputFullPath = self.logDirectory+ '\\' + self.outputName # c:\temp\abc_output.txt
        self.fieldNames = ["Date",
                           "Time",                                                     
                           ]
        
        #search started flag
        self.started = 0
    
    def Demo(self):
        print "This is a demo"
        print self.logFullPath
    
    def GetTimeStamp(self, line):
        '''
            i.e.
            line = Tue Aug  4 16:33:02 PDT 2015            
            return "8/4/2015", "16:33:02"
            
            if line is something else, return none
        '''
        
        Result = line.strip('\n')# ["Tue", "Aug", 4, 16, 33, 02, "PDT", 2015]
        
        #print "Result: ", Result
        weekday = re.match(r"^.{3}", Result)
        #print "day: ", day
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        Result = Result.split()
        
        if weekday is not None:        
            if weekday.group(0) in weekdays:
                
                date = {"Jan":1,
                        "Feb":2,
                        "Mar":3,
                        "Apr":4,
                        "Fri":5,
                        "Jun":6,
                        "Jul":7,
                        "Aug":8,
                        "Sep":9,
                        "Oct":10,
                        "Nov":11,
                        "Dec":12
                        }
        
                day = str(Result[2])
                month = str(date.get(Result[1]))
                year = Result[5]
                               
                date = "/".join([month, day, year]) # "8/4/2015"
                time = Result[3] # "16:33:02"
                return date, time
            else:
                return None
    
    def GetMacID(self, line, printInfo=0):
        '''
            i.e.
            line = "00:13:50:ff:fe:10:01:ab found in nodeq, reboot:   0, dev_typ:Sysvar #211 is not defined,"
            return "00:13:50:ff:fe:10:01:ab"
            
            if line is something else, return none
        '''
        
        term = re.compile("^([0-9a-z]{2}:){7}[0-9a-z]{2}") #This should match any of 00:13:50:ff:fe:10:01:ab        
               
        macid = term.match(line)
                 
        if macid is not None and "found in nodeq" in line: #Need to make sure not to match macid is "not found" list                       
            return macid.group(0)
        else:
            return None
    
    def GetRebootCntr(self, line):
        '''
            Only Call GetRebootCntr() after line if GetMacID() return a valid mac ID
            i.e.
            line = "00:13:50:ff:fe:10:01:ab found in nodeq, reboot:   0, dev_typ:Sysvar #211 is not defined,"
            return "0"
            
            if line = "00:13:50:ff:fe:10:01:ab found in nodeq, reboot:    , dev_typ:Sysvar #211 is not defined,"
            or if line = "00:13:50:ff:fe:10:04:f4 NOT found in nodeq,"
            return " "
            
            This function should never return None
        '''
        
        term = re.compile("(?<=reboot:)\s*[0-9]{1,}?(?=,)") #this should match    2 from 00:13:50:ff:fe:10:00:f5 found in nodeq, reboot:   2, dev_typ:Sysvar #211 is not defined,
                                                            #but it will ignore:        00:13:50:ff:fe:10:00:f5 found in nodeq, reboot:    , dev_typ:Sysvar #211 is not defined,
                                                            #                           00:13:50:ff:fe:10:04:f4 NOT found in nodeq,
        
        result = term.search(line)
        
        if result is not None:            
            return result.group(0).strip()
        else:
            return " "
    
    def GetFieldNames(self): #pre generate all field names by finding all valid macs, this requires the log file to have only the same amont of MAC IDs.
        with open(self.logFullPath) as dataFile:
            line = dataFile.next()                       
            while True:                
                if self.GetMacID(line) is not None:
                    self.fieldNames.append(self.GetMacID(line))
                    line = dataFile.next()
                elif ".not found." in line:
                    return # by the time it reaches ....not found...., it has serached through all mac ids
                else:
                    line = dataFile.next()
                    
            
    
    def GenCSV(self): #main flow
        self.GetFieldNames() #need to find all the macs and place them as filed name
        
        with open(self.logFullPath, 'r') as dataFile: # this is input file
            with open(self.outputFullPath, 'w') as csvfile: # this is output file
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldNames, lineterminator='\n', )
                writer.writeheader()
                          
                line = dataFile.next()
                row = OrderedDict()
                   
                while True:
                    timestamp = self.GetTimeStamp(line)
                    if timestamp is not None:
                        if self.started == 1: #if this is true, we already have row established, then we need to write it to the csv file:
                            writer.writerow(row)
                        date, time = self.GetTimeStamp(line)
                        row = OrderedDict({"Date": date, "Time": time})               
                        line = dataFile.next()
                        self.started = 1
                    else: #if this is not timestamp, need to see if this line is macid
                        macid = self.GetMacID(line)
                        if macid is not None:
                            
                            # need to find reboot counter for this mac
                            reboot = self.GetRebootCntr(line)
                            
                            #update row with reboot counter for this mac ID
                            row.update({macid:reboot})
                        try:
                            line = dataFile.next()
                        except StopIteration:
                            print "End of file. Good bye!"
                            return
                        
                            
                            
                        
                
            
        
        
         
    
    
    
    
    
    
    
    
    
    
    
