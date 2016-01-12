#
#Program name: RebootLog2CSV
#
#Description: extract mac IDs from net mgr log file, 
#             and extract reboot counter for each mac IDs,
#             output to CSV file
#
#Author:      JX
#Date:        2016-1-12
#
#




import RebootLog2CSV as RL

logfile = r"C:\Users\jxue\Documents\Projects_LocalDrive\Bridge2.0\ping_log\1_12_16\bridge20_log"

process = RL.RL2C(logfile)

process.GenCSV()


