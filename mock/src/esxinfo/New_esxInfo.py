#!/usr/bin/env python
"""
Script:  esxInfo.py
Updated: 3/15/2017 9:12
Author:  Scot Corrie & Rich Rauenzahn
         (This is a major re-write of "serverInfo.py" by Sreesaila Ganamur)

Purpose: Gathers ESX Host data: OS, Vendor, Model, CPU, Sockets, Cores, Ram, etc.

"""
import csv
import datetime
import optparse
import os
import re
import socket
import subprocess
import sys
import paramiko

Version = "0.2.0.0"
pgm = os.path.basename(sys.argv[0])

_USERS     = ['root', 'admin']
_PASSWORDS = ['ca$hc0w', 'vmware', '', '!cisco', 'Ca$hC0w', 'Ca$hc0w1', 'Vmware123!', 'Ca$hC0w1', 'Ca$hc0w2', 'Ca$hC0w2', \
        'calvin', 'st@rf1sh', 'vmware1!', 'VMware1!', 'map69meSp$']


class AllowSSHkeys(paramiko.MissingHostKeyPolicy):
    """Blindly Accept All SSH Keys"""
    def missing_host_key(self, client, hostname, key):
        return

def Usage():
    print("""
                                     USAGE STATEMENT

    NAME
       esxInfo.py

    DESCRIPTION
       Gathers ESX Host data: OS, Vendor, Model, CPU, Sockets, Cores, Ram, etc.

       Creates a spreadsheet of system information in .csv format, an error log,
       and two lists capturing ESX and Linux/Unix hosts it successfully connected to
       and the login/password combination used.

    USAGE
       esxInfo.py [-f] <filename> [options]

    OPTIONS
       -f, --hostfile           List of hosts
       -p, --prefix             Add a custom prefix to output filenames
       -u, --userfile           Provide your own "user,passwd" file (see example below)
                                (If there is not already an entry in the hosts file, the script
                                will try each combination in the password file)
       -v  --version            Display program version

    PYTHON MODULES
       Paramiko and Standard Libraries.

    EXAMPLES
       -v x                     Display program version

       -f hosts                 Hostfile (contains one or all of: host,login,password)
       (Mandatory argument)     (Example host file. All the below are valid)
                                  w3-perfsds-9191
                                  10.0.1.99
                                  w1-firefly-27,root
                                  w1-serenity-01,scorrie,cashMoney

       -f hosts -p WDC.pod1     Hostfile, and a preferred prefix for output files
                                  (Default:     20160711_100180.esxInfo.csv)
                                  (Using "-p":  WDC.pod1.20160711_100180.csv)

       -f hosts -u pws.txt      Specify a file, a prefix, and a password file
                                  ("-u" Example. All the below are valid. You must
                                  have a login and "," for "empty" passwords)
                                  root,vmware
                                  root,
                                  root,cashMoney
                                  sysadmin,cashMoney

       Example:
       esxInfo.py -f hosts -p WDC.pod1 -u pws.txt

       (Output files:)
         WDC.pod1.20160711_113041.csv
         WDC.pod1.ESX-hosts.20160711_113041.txt
         WDC.pod1.Linux-hosts.20160711_113041.txt
         WDC.pod1.Errors.20160711_113041.log

       """)

    raise SystemExit(1)


def findStr(srcFile,string):
    pattern = r'^\s+%s\s+"(.*)"' % string
    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            return match.group(1)

def findDotStr(srcFile,string):
    # ---- Could this be better? ----
    pattern = r'(\-+)%s\.+([\.|\S]+)' % string

    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            dMatch = str(match.group(2))
            result = dMatch.split()
            return result[0]
    # --------------------------------

def find2Str(srcFile,str1,str2):
    # ---- Could this be better? ----
    pattern = r'(\-+)%s\.+(\S+\s%s.)' % (str1, str2)

    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            dMatch = str(match.group(2))
            result = dMatch.split()
            return result[0]
    # --------------------------------

def findNum(srcFile,string):
    pattern = r'^\s+%s\s+(\d+)' % string
    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            return match.group(1)

def findParm(srcFile,string,isESXi):
    if isESXi:
        pattern = r'^\s*%s:\s*(\d+)' % string
    else:
        basePat = r'^\s*%s\s*:\s*(\d+)' % string
        pattern = re.compile(basePat, re.IGNORECASE)

    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            return match.group(1)

def findColParm(srcFile,string):
    pattern = r'^\s*%s:\s(.*)\s+(.*)' % string

    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            return match.group(1)

def findWWPN(srcFile):
    pattern = r'(fc\.)(\S{16,16})\:(\S{16,16})\s+(fc)'

    for line in srcFile:
        match = re.search(pattern,line)
        if match:
            wwMatch = str(match.group(2))
            result = wwMatch.split()
            return result[0]


def main():
    if len(sys.argv) < 2:
        Usage()

    opt = optparse.OptionParser()
    opt.add_option('--hostfile', '-f', action='store', default=None, help='hostfile')
    opt.add_option('--prefix', '-p', action='store', default=None, help='prefix')
    opt.add_option('--userfile', '-u', action='store', default=None, help='user,passwd file')
    opt.add_option('--version', '-v', action='store', default=None, help='version')
    options, args = opt.parse_args()

    hostList = []
    dnow = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    if options.version:
        print((pgm + " " + Version))
        raise SystemExit(2)

    if options.prefix:
        prename = str(options.prefix)
        csvFile = "%s.%s.csv" % (prename,dnow)
        esxReport = "%s.ESX-hosts.%s.txt" % (prename,dnow)
        linuxReport = "%s.Linux-hosts.%s.txt" % (prename,dnow)
        errorReport = "%s.Errors.%s.log" % (prename,dnow)
    else:
        csvFile = "%s.esxInfo.csv" % (dnow)
        esxReport = "%s.ESX-hosts.txt" % (dnow)
        linuxReport = "%s.Linux-hosts.txt" % (dnow)
        errorReport = "%s.esxInfo.Errors.log" % (dnow)

    if options.userfile:

        if not os.path.isfile(options.userfile):
            print("")
            print("     Error: user file does not exist!")
            print("")
            raise SystemExit(3)

        uFile = []
        fpws = []

        with open(options.userfile) as userFile:
            for uline in userFile:
                uFile.append([str(uf) for uf in uline.strip().split(',')])

            fusers = set([row[0] for row in uFile])
            fusers = list(fusers)
            fpws = set([row[1] for row in uFile])
            fpws = list(fpws)

    global csvReport
    csvReport = csv.DictWriter(open(csvFile, 'w'), Headings(), extrasaction='ignore') # or raise
    csvReport.writeheader()

    global esxlog
    esxlog = open(esxReport,'w')

    global linuxlog
    linuxlog = open(linuxReport,'w')

    global errorlog
    errorlog = open(errorReport,'w')
    startTime = datetime.datetime.now()
    errorlog.write('Script Start Time | %s' % startTime)
    errorlog.write('\n')

    with open(options.hostfile) as hosts:
        for hline in hosts:
            hostList.append([str(st) for st in hline.strip().split(',')])

    global connected

    for line in hostList:

        if len(line) == 12:
            hostname = line[0]
            host = line[1]
            users = [line[2]]
            passwords = [line[3]]
            ILO = line[4]
            ILOIP = line[5]
            ILOUsers = line[6]
            ILOPasswords = line[7]
            assignTo = line[8]
            testBed = line[9]
            startDate = line[10]
            endDate = line[11]

        if len(line) == 3:
            host = line[0]
            users = [line[1]]
            passwords = [line[2]]
        elif len(line) == 2 and options.userfile:
            host = line[0]
            users = [line[1]]
            passwords = fpws
        elif len(line) == 2:
            host = line[0]
            users = [line[1]]
            passwords = _PASSWORDS
        elif len(line) == 1:
            host = line[0]

            if options.userfile:
                users = fusers
                passwords = fpws
            else:
                users = _USERS
                passwords = _PASSWORDS

        if host == '':
            continue

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(AllowSSHkeys())
        connected = False

        response = os.system("ping -q -c 1 -W 2 " + host)
        print((''))

        errorData = {}

        if response != 0:
            errorlog.write('%s | System Not Pingable | Action: Verify IP!' % host)
            errorlog.write('\n')

            # "Hostname", "Username", "Password", "ILOIP", "ILOName", "ILOUser", "ILOPassword", "AssignTo", "TestBed", "StartDate", "EndDate"
            errorData['HostIP'] = host
            errorData['Status'] = 'System Not Pingable'
            errorData['Hostname'] = hostname
            errorData['Username'] = line[2]
            errorData['Password'] = line[3]
            errorData['ILOIP'] = ILOIP
            errorData['ILOName'] = ILO
            errorData['ILOUser'] = ILOUsers
            errorData['ILOPassword'] = ILOPasswords
            errorData['AssignTo'] = assignTo
            errorData['TestBed'] = testBed
            errorData['StartDate'] = startDate
            errorData['EndDate'] = endDate
            csvReport.writerow(errorData)

            continue # with next host

        for user in users:

            if connected:
                break

            for passwd in passwords:

                assert(not connected)

                try:
                    ssh.connect(host, timeout=30, username=user, password=passwd)

                    stdin, stdout, stderr = ssh.exec_command('uname')
                    nameout = stdout.readlines()
                    osVer = nameout[0].strip()
                    print(("OS Ver: " + osVer))

                    if osVer != "VMkernel" :
                        linuxlog.write('%s,%s,%s' % (host,user,passwd))
                        linuxlog.write('\n')
                    else:
                        stdin, stdout, stderr = ssh.exec_command('vim-cmd hostsvc/hostsummary | grep "fullName ="')
                        output = stdout.readlines()
                        if not output:
                            errorlog.write('%s | User: %s Password: %s - vim-cmd Failed | vim-cmd' % (host,user,passwd))
                            errorlog.write('\n')
                            break
                        else:
                            esxlog.write('%s,%s,%s' % (host,user,passwd))
                            esxlog.write('\n')
                    connected = True

                    break

                except paramiko.AuthenticationException:
                    errorlog.write('%s | User: %s Authentication Failed | Password: %s' % (host,user,passwd))
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'Authentication Failed'
                    errorData['Hostname'] = hostname
                    errorData['Username'] = line[2]
                    errorData['Password'] = line[3]
                    errorData['ILOIP'] = ILOIP
                    errorData['ILOName'] = ILO
                    errorData['ILOUser'] = ILOUsers
                    errorData['ILOPassword'] = ILOPasswords
                    errorData['AssignTo'] = assignTo
                    errorData['TestBed'] = testBed
                    errorData['StartDate'] = startDate
                    errorData['EndDate'] = endDate
                    csvReport.writerow(errorData)
                    csvReport.writerow(errorData)

                    continue # with next password

                except paramiko.SSHException:
                    errorlog.write('%s | SSHException | SSH' % host)
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'SSHException'
                    csvReport.writerow(errorData)

                    break

                except paramiko.BadAuthenticationType:
                    errorlog.write('%s | Password Authentication Not Enabled |SSH' % host)
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'Password Authentication Not Enabled'
                    csvReport.writerow(errorData)

                    break

                except paramiko.PasswordRequiredException:
                    errorlog.write('%s | Private Key Password Required |SSH' % host)
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'Private Key Password Required'
                    csvReport.writerow(errorData)
                    
                    break

                except socket.timeout:
                    errorlog.write('%s | Socket Timeout |Timeout' % host)
                    errorlog.write('\n')
                    break

                except socket.error:
                    errorlog.write('%s | Socket Error |Socket' % host)
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'Socket Error'
                    errorData['Hostname'] = hostname
                    errorData['Username'] = line[2]
                    errorData['Password'] = line[3]
                    errorData['ILOIP'] = ILOIP
                    errorData['ILOName'] = ILO
                    errorData['ILOUser'] = ILOUsers
                    errorData['ILOPassword'] = ILOPasswords
                    errorData['AssignTo'] = assignTo
                    errorData['TestBed'] = testBed
                    errorData['StartDate'] = startDate
                    errorData['EndDate'] = endDate
                    csvReport.writerow(errorData)

                    csvReport.writerow(errorData)

                    break

                except EOFError:
                    errorlog.write('%s | EOF Error |EOF' % host)
                    errorlog.write('\n')

                    errorData['HostIP'] = host
                    errorData['Status'] = 'EOF Error'
                    csvReport.writerow(errorData)

                    break

                if not connected:
                    continue # with next password

            if not connected:
                continue # with next user
            else:
                break
                
        if connected and osVer == "VMkernel":
            data = getInfo(ssh)
            if data:
                #"HostIP", "Status", "Hostname", "Username", "Password", "ILOIP", "ILOName", "ILOUser", "ILOPassword", "AssignTo", "TestBed", "StartDate", "EndDate", 
                data['HostIP'] = host
                data['Status'] = 'OK'
                data['Hostname'] = hostname
                data['Username'] = line[2]
                data['Password'] = line[3]
                data['ILOIP'] = ILOIP
                data['ILOName'] = ILO
                data['ILOUser'] = ILOUsers
                data['ILOPassword'] = ILOPasswords
                data['AssignTo'] = assignTo
                data['TestBed'] = testBed
                data['StartDate'] = startDate
                data['EndDate'] = endDate

                csvReport.writerow(data)
                ssh.close()
            else:
                ssh.close()
                break
        elif connected:
            sysInfo = subprocess.call(['/Users/scorrie/Documents/all/4.pcs/43-coding/Shell/scripts/New_RunUnixInfo.sh', 'list', 'pwfile'], stdout=subprocess.PIPE)
            print("This is it: %s" % (sysInfo.communicate()))
            ret["ESX"] = "Linux"


    endTime = datetime.datetime.now()
    errorlog.write('Script End Time | %s' % endTime)
    errorlog.write('\n')

def uptime_to_mins(utime):
    pat1 = re.compile(r".*up ([0-9]+) days, \s*([0-9]+:[0-9]+).*")
    pat2 = re.compile(r".*up ([0-9]+:[0-9]+).*")
    m = pat1.match(utime)

    if m != None:
        updays = m.group(1)
        uphhmm = m.group(2)
        l = uphhmm.split(':')
        upmins = (int(l[0]) * 60) + int(l[1]) +( int(updays) * 24 * 60)
        return "%d" % (upmins)
    else:
        m = pat2.match(utime)
        if m:
            uphhmm = m.group(1)
            l = uphhmm.split(':')
            upmins = (int(l[0]) * 60) + int(l[1])
            return "%d" % (upmins)
        else:
            upmins = 1
            return "%d" % (upmins)

## Convert minutes to days:hrs:mins
def mins_to_time(mins):
    days = mins / 1440
    mins -= 1440*days
    hrs = mins / 60
    mins -= 60*hrs
    return "%d days: %2d hrs: %2d mins" % (days,hrs,mins)

def Headings():
    ## Add in the "OS-ESX info", "ESX Release Level", and "CPU Speed" if you want to show them.
    ## Then uncomment them in the "getInfo" function section

    headings = ["HostIP","Status","Hostname","Username","Password","ILOIP","ILOName","ILOUser","ILOPassword","AssignTo","TestBed","StartDate","EndDate",
                "IPMI","ESX","ESX_Build","OEM",
                "Server_Model","CPU","CPU_Model","CPU_Speed","CPU_Codename",
                "CPU_Sockets","CPU_Cores","CPU_Threads","Memory","No._of_VMs","CPU_Usage_%","Mem_Usage_%",
                "Local_HDs","Total_NICs","Total_HBAs",
                "NIC_1_Type","NIC_1_Speed","NIC_1_Description","NIC_1_Link",
                "NIC_2_Type","NIC_2_Speed","NIC_2_Description","NIC_2_Link",
                "NIC_3_Type","NIC_3_Speed","NIC_3_Description","NIC_3_Link",
                "NIC_4_Type","NIC_4_Speed","NIC_4_Description","NIC_4_Link",
                "NIC_5_Type","NIC_5_Speed","NIC_5_Description","NIC_5_Link",
                "NIC_6_Type","NIC_6_Speed","NIC_6_Description","NIC_6_Link",
                "HBA_1_Name","HBA_1_Description","HBA_2_Name","HBA_2_Description",
                "HBA_3_Name","HBA_3_Description","HBA_4_Name","HBA_4_Description",
                "HBA_5_Name","HBA_5_Description","HBA_6_Name","HBA_6_Description",
                "HBA_7_Name","HBA_7_Description","HBA_8_Name","HBA_8_Description",
                "HBA_9_Name","HBA_9_Description","HBA_10_Description",
                "HBA_11_Name","HBA_11_Description","HBA_12_Name","HBA_12_Description",
                "HD_1_Vendor","HD_1_Description","HD_1_Model","HD_1_Size",
                "HD_2_Vendor","HD_2_Description","HD_2_Model","HD_2_Size",
                "HD_3_Vendor","HD_3_Description","HD_3_Model","HD_3_Size",
                "HD_4_Vendor","HD_4_Description","HD_4_Model","HD_4_Size",
                "HD_5_Vendor","HD_5_Description","HD_5_Model","HD_5_Size",
                "HD_6_Vendor","HD_6_Description","HD_6_Model","HD_6_Size",
                "HD_7_Vendor","HD_7_Description","HD_7_Model","HD_7_Size",
                "HD_8_Vendor","HD_8_Description","HD_8_Model","HD_8_Size",
                "HD_9_Vendor","HD_9_Description","HD_9_Model","HD_9_Size",
                "HD_10_Vendor","HD_10_Description","HD_10_Model","HD_10_Size",
                "HD_11_Vendor","HD_11_Description","HD_11_Model","HD_11_Size",
                "HD_12_Vendor","HD_12_Description","HD_12_Model","HD_12_Size",
                "HD_13_Vendor","HD_13_Description","HD_13_Model","HD_13_Size",
                "HD_14_Vendor","HD_14_Description","HD_14_Model","HD_14_Size",
                "HD_15_Vendor","HD_15_Description","HD_15_Model","HD_15_Size",
                "HD_16_Vendor","HD_16_Description","HD_16_Model","HD_16_Size",
                "HD_17_Vendor","HD_17_Description","HD_17_Model","HD_17_Size",
                "HD_18_Vendor","HD_18_Description","HD_18_Model","HD_18_Size",
                "HD_19_Vendor","HD_19_Description","HD_19_Model","HD_19_Size",
                "HD_20_Vendor","HD_20_Description","HD_20_Model","HD_20_Size",
                "HD_21_Vendor","HD_21_Description","HD_21_Model","HD_21_Size",
                "HD_22_Vendor","HD_22_Description","HD_22_Model","HD_22_Size",
                "HD_23_Vendor","HD_23_Description","HD_23_Model","HD_23_Size",
                "HD_24_Vendor","HD_24_Description","HD_24_Model","HD_24_Size",
                "HD_25_Vendor","HD_25_Description","HD_25_Model","HD_25_Size",]

    return headings

# There is a more complicated version of the below function that also captures "generation".
# (If I have time, I will rewrite this as a dictionary statement)
def cpuid_to_codename(cpuModelName, cpuidFamily, cpuidModel, cpuidStepping):

    if cpuModelName.find('Intel') >= 0:
        if cpuidFamily == 15:
            if cpuidModel == 3:
                cpuCodename = "Nocona/Prescott"
            elif cpuidModel == 4:
                if cpuidStepping == 8:
                    cpuCodename = "Paxville"
                elif cpuidStepping == 3 or cpuidStepping == 10:
                    cpuCodename = "Irwindale/Prescott"
                elif cpuidStepping == 1 or cpuidStepping == 4 or cpuidStepping == 9:
                    cpuCodename = "Cranford/Potomac"
                else:
                    cpuCodename = "Prescott-Other"
            elif cpuidModel == 6:
                if cpuidStepping == 1 or cpuidStepping == 4:
                    cpuCodename = "Dempsy"
                elif cpuidStepping == 6 or cpuidStepping == 8:
                    cpuCodename = "Tulsa"
                else:
                    cpuCodename = "CedarMill-Other"
            else:
                cpuCodename = "Intel-Other-Older"

        elif cpuidFamily == 6:
            if cpuidModel == 14:
                cpuCodename = "Sossaman"
            elif cpuidModel == 15:
                if (re.search(r'51\d\d',  cpuModelName)):
                    cpuCodename = "Woodcrest"
                elif (re.search(r'30\d\d',  cpuModelName)):
                    cpuCodename = "Conroe"
                elif (re.search(r'32\d\d',  cpuModelName)):
                    cpuCodename = "Kentsfield"
                elif (re.search(r'53\d\d',  cpuModelName)):
                    cpuCodename = "Clovertown"
                elif (re.search(r'7\d\d\d',  cpuModelName)):
                    cpuCodename = "Tigerton"
                else:
                    cpuCodename = "Merom-Other"
            elif cpuidModel == 23:
                if (re.search(r'54\d\d',  cpuModelName)):
                    cpuCodename = "Harpertown"
                elif (re.search(r'52\d\d',  cpuModelName)):
                    cpuCodename = "Wolfdale"
                elif (re.search(r'33\d\d',  cpuModelName)):
                    cpuCodename = "Yorkfield"
                else:
                    cpuCodename = "Penryn-Other"
            elif cpuidModel == 29:
                cpuCodename = "Dunnington"
            elif cpuidModel == 26:
                if (re.search(r'55\d\d',  cpuModelName)):
                    cpuCodename = "Nehalem-EP"
                else:
                    cpuCodename = "Bloomfield"
            elif cpuidModel == 30:
                cpuCodename = "Lynnfield"
            elif cpuidModel == 46:
                cpuCodename = "Nehalem-EX"
            elif cpuidModel == 37:
                cpuCodename = "Clarkdale"
            elif cpuidModel == 44:
                cpuCodename = "Westmere-EP"
            elif cpuidModel == 47:
                cpuCodename = "Westmere-EX"
            elif cpuidModel == 42:
                cpuCodename = "SandyBridge-E3/DT"
            elif cpuidModel == 45:
                cpuCodename = "SandyBridge-EP"
            elif cpuidModel == 58:
                cpuCodename = "IvyBridge-E3/DT"
            elif cpuidModel == 62:
                if (re.search(r'E7\-\d\d\d\d',  cpuModelName)):
                    cpuCodename = "IvyBridge-EX"
                else:
                    cpuCodename = "IvyBridge-EP"
            elif cpuidModel == 60:
                cpuCodename = "Haswell-DT"
            elif cpuidModel == 63:
                if (re.search(r'E7\-\d\d\d\d',  cpuModelName)):
                    cpuCodename = "Haswell-EX"
                else:
                    cpuCodename = "Haswell-EP"
            elif cpuidModel == 71:
                cpuCodename = "Broadwell-DT"
            elif cpuidModel == 77:
                cpuCodename = "Avoton"
            else:
                cpuCodename = "Intel-Other"

        else:
            cpuCodename = "Intel-Other"

    else:
        if cpuidFamily == 15:
            if cpuidModel == 3:
                cpuCodename = "Rev-A/B"
            elif cpuidModel == 5:
                cpuCodename = "Rev-C"
            elif cpuidModel == 21:
                cpuCodename = "Rev-D"
            elif cpuidModel == 33 or cpuidModel == 37:
                cpuCodename = "Rev-E"
            elif cpuidModel == 65 or cpuidModel == 67:
                cpuCodename = "Rev-F"
            else:
                cpuCodename = "AMD-Rev-Other"

        elif cpuidFamily == 16:
            if cpuidModel == 2:
                cpuCodename = "Barcelona"
            elif cpuidModel == 4:
                cpuCodename = "Shanghai"
            elif cpuidModel == 8:
                if (re.search(r'41\d\d',  cpuModelName)):
                    cpuCodename = "Lisbon"
                else:
                    cpuCodename = "Istanbul"
            elif cpuidModel == 9:
                if (re.search(r'41\d\d',  cpuModelName)):
                    cpuCodename = "Lisbon"
                else:
                    cpuCodename = "MagnyCours"
            else:
                cpuCodename = "Greyhound-Other"

        elif cpuidFamily == 21:
            if cpuidModel == 1:
                if (re.search(r'32\d\d',  cpuModelName)):
                    cpuCodename = "Zurich"
                elif (re.search(r'42\d\d',  cpuModelName)):
                    cpuCodename = "Valencia"
                elif (re.search(r'62\d\d',  cpuModelName)):
                    cpuCodename = "Interlagos"
                else:
                    cpuCodename = "Bulldozer-Other"
            elif cpuidModel == 2:
                if (re.search(r'33\d\d',  cpuModelName)):
                    cpuCodename = "Delhi"
                elif (re.search(r'43\d\d',  cpuModelName)):
                    cpuCodename = "Seol"
                elif (re.search(r'63\d\d',  cpuModelName)):
                    cpuCodename = "AbuDhabi"
                else:
                    cpuCodename = "PileDriver-Other"
            elif cpuidModel == 48:
                cpuCodename = "Berlin"
            else:
                cpuCodename = "AMD-Other"

        elif cpuidFamily == 22:
            if cpuidModel == 0:
                cpuCodename = "Kyoto"
            else:
                cpuCodename = "Jaguar-Other"

        else:
            cpuCodename = "AMD-Other"

    return "%s" % (cpuCodename)


def getInfo(ssh):
    ret = {}

    ## esxcfg-info (will be used for Serial Number, IPMI and other sections)
    stdin, stdout, stderr = ssh.exec_command('esxcfg-info -w')
    infoOut = stdout.readlines()

    ## vim-cmd (will be the resource for several parameters below)
    stdin, stdout, stderr = ssh.exec_command('vim-cmd hostsvc/hostsummary')
    vimcmd = stdout.readlines()

    if infoOut:
        ## Serial Number
        serialNum = findDotStr(infoOut,"Serial Number")
        if serialNum:
            ret['Serial_No.'] = serialNum

        ## IPMI
        ipmi = findDotStr(infoOut,"Ipmi Supported")
        if ipmi:
            ret['IPMI'] = ipmi

    if vimcmd:
        #-----------Better solution?------------
        ## "BIOS Ver." (For ESX < 6.5)
        for line in vimcmd:
            match = re.search( r'(.*) System BIOS (.*\s)', line)

            if match:
                mFull = str(match.group(2))
                fBios = mFull.split()
                bios = fBios[0].replace('-[', '').replace(']-', '')
                ret['BIOS_Ver.'] = bios
        #---------------------------------------

        ## "Uptime in Mins"
        stdin, stdout, stderr = ssh.exec_command('uptime')
        output = stdout.readlines()
        if output:
            uptime_mins = uptime_to_mins(output[0])

            ## "Uptime in Days:Hrs:Mins"
            ret['Uptime in Days:Hrs:Mins'] = mins_to_time(int(uptime_mins))

        ## "ESX Release Level"
        #stdin, stdout, stderr = ssh.exec_command('vmware -l')
        #output = stdout.readlines()
        #ret['ESX Release Level'] = output[0].strip()

        ## "OS-ESX Info"
        sOut = findStr(vimcmd,"fullName =")
        if sOut:
            esxInfo = sOut
            ## ret['OS-ESX Info'] = esxInfo

        ## "ESX"
        sOut = findStr(vimcmd,"version =")
        if sOut:
            esxBuildVer = sOut
            ret['ESX'] = esxBuildVer

            #-----------Better solution?------------
            ## "BIOS Ver." (For ESX 6.5+)
            if esxBuildVer >= '6.5' and infoOut:
                bios = findDotStr(infoOut,"BIOS Version")

                if bios:
                    ret['BIOS_Ver.'] = bios.replace('-[', '').replace(']-', '')
                else:
                    bios = "NA"
            #---------------------------------------

        ## "ESX Build"
        sOut = findStr(vimcmd,"build =")
        if sOut:
            esxBuild = sOut
            ret['ESX Build'] = esxBuild

        ## "OEM Details" (OEM details)
        sOut = findStr(vimcmd,"vendor =")
        if sOut:
            vendor = sOut
            ret['OEM'] = vendor

        ##  "Server Model"
        sOut = findStr(vimcmd,"model =")
        if sOut:
            srvModel = sOut.replace('-[', '').replace(']-', '')
            ret['Server_Model'] = srvModel

        ## "CPU Model"
        sOut = findStr(vimcmd,"cpuModel =")
        if sOut:
            cpuModel = sOut.replace('          ', '').replace('(R)', '')
            cpuModel = cpuModel.replace('(TM)', '').replace('(tm)', '')
            ret['CPU_Model'] = cpuModel

            ## "CPU"
            if cpuModel.find('Intel') >= 0:
                ret['CPU'] = "Intel"
            else:
                ret['CPU'] = "AMD"

        ## "CPU Speed"
        nOut = findNum(vimcmd,"cpuMhz =")
        if nOut:
            cpuMhz_pcore = nOut
            ret['CPU_Speed'] = cpuMhz_pcore

        ## "CPU Sockets"
        nOut = findNum(vimcmd,"numCpuPkgs =")
        if nOut:
            cpuSockets = nOut
            ret['CPU_Sockets'] = cpuSockets

        ## "CPU Cores"
        nOut = findNum(vimcmd,"numCpuCores =")
        if nOut:
            cpuCores = nOut
            ret['CPU_Cores'] = cpuCores

        ## "CPU Threads"
        nOut = findNum(vimcmd,"numCpuThreads =")
        if nOut:
            cpuThreads = nOut
            ret['CPU_Threads'] = cpuThreads

        ## "Memory"
        nOut = findNum(vimcmd,"memorySize =")
        if nOut:
            memorySize = float(nOut) / (1024 ** 3)
            mem = "%0.0f GB" % memorySize
            ret['Memory'] = "%0.0f GB" % memorySize

        ## "CPU Usage %"
        nOut = findNum(vimcmd,"overallCpuUsage =")
        if nOut:
            cUsage = nOut
            cpu_usage = "%.2f" % (( float(cUsage) * 100 ) / ( float(cpuCores) * float(cpuMhz_pcore) ) )
            ret['CPU_Usage_%'] = cpu_usage

        ## "Mem Usage %"
        nOut = findNum(vimcmd,"overallMemoryUsage =")
        if nOut:
            memUsage = "%.2f" % ((float(nOut) / float(memorySize)) *0.1 )
            ret['Mem_Usage_%'] = "%.2f" % ((float(nOut) / float(memorySize)) *0.1 )

        ## "Total NICs"
        nOut = findNum(vimcmd,"numNics =")
        if nOut:
            numNics = nOut
            ret['Total_NICs'] = numNics

        ## "Total HBAs" (Sequence repeats based on setting)
        nOut = findNum(vimcmd,"numHBAs =")
        if nOut:
            numHBAs = nOut
            ret['Total_HBAs'] = numHBAs

        # Fix ------------------------------------
        if esxInfo.find('ESXi') >=0 or esxInfo.find('esxi') >=0 :
            stdin, stdout, stderr = ssh.exec_command('vsish -e get /hardware/cpu/cpuList/0')
            vsish = stdout.readlines()

            ## "CPUID.Family"
            pOut = findParm(vsish,"Family",isESXi=True)
            if pOut:
                cpuidFamily = int(pOut)
            else:
                cpuidFamily = 0
            ret['CPUID_Fam'] = cpuidFamily


            ## "CPUID.Model"
            pOut = findParm(vsish,"Model",isESXi=True)
            if pOut:
                cpuidModel = int(pOut)
            else:
                cpuidModel = 0
            ret['CPUID_Mod'] = cpuidModel


            ## "CPUID.Stepping"
            pOut = findParm(vsish,"Stepping",isESXi=True)
            if pOut:
                cpuidStep = pOut
                cpuidStepping = int(pOut)
            else:
                cpuidStepping = 0
            ret['CPUID_Step'] = cpuidStepping

        else:
            stdin, stdout, stderr = ssh.exec_command('cat /proc/cpuinfo')
            cpuinfo = stdout.readlines()
            ## "CPUID.Family"
            pOut = findParm(cpuinfo,"cpu family",isESXi=False)
            if pOut:
                cpuidFamily = int(pOut)
            else:
                cpuidFamily = 0
            ret['CPUID_Fam'] = cpuidFamily


            ## "CPUID.Model"
            pOut = findParm(cpuinfo,"model",isESXi=False)
            if pOut:
                cpuidModel = int(pOut)
            else:
                cpuidModel = 0
            ret['CPUID_Mod'] = cpuidModel


            ## "CPUID.Stepping"
            pOut = findParm(cpuinfo,"stepping",isESXi=False)
            if pOut:
                cpuidStep = pOut
                cpuidStepping = int(pOut)
            else:
                cpuidStepping = 0
            ret['CPUID_Step'] = cpuidStepping

        ## "CPU Codename", "CPU Family/Generation" , "CPU Speed"
        Codename = cpuid_to_codename(cpuModel,cpuidFamily,cpuidModel,cpuidStepping)

        if Codename == "Intel-Other" or Codename == "AMD-Other" or None:

           if infoOut:
               cpuCodename = find2Str(infoOut,"Device Name","DMI")

               if cpuCodename:
                   ret['CPU_Codename'] = cpuCodename
               else:
                   ret['CPU_Codename'] = Codename

           else:
               ret['CPU_Codename'] = Codename
        else:
            ret['CPU_Codename'] = Codename

        ## "No. of VMs"
        #---- Wasn't this code unnecessary?-----
        #if esxBuildVer.find('5.') >=0 or esxBuildVer.find('6.') >=0 :
        #---------------------------------------
        if esxBuildVer >= '5.':
            stdin, stdout, stderr = ssh.exec_command('vm-support -V | grep Running | wc -l')
        else:
            stdin, stdout, stderr = ssh.exec_command('vm-support -x | grep id= | wc -l')
        buildOut = stdout.readlines()
        if buildOut:
            ret['No._of_VMs'] = buildOut[0].strip()

    ## "Local HDs"
    stdin, stdout, stderr = ssh.exec_command('esxcfg-scsidevs -c |grep -c "Local"')
    output = stdout.readlines()
    if output:
        ret['Local_HDs'] = output[0].strip()

    ## "LUNs"
    stdin, stdout, stderr = ssh.exec_command('esxcfg-mpath -b')
    bpathOut = stdout.readlines()

    if bpathOut:
        disks = 0
        disk = "Disk"
        lDisk = "Local"

        for i in bpathOut:

            if disk in i and lDisk not in i:
                disks += 1

        # ret['LUNs'] = disks

    ## "Paths"
    stdin, stdout, stderr = ssh.exec_command('esxcli storage core path list')
    pathsOut = stdout.readlines()

    if pathsOut:
        paths = 0
        disk = "Disk"
        lDisk = "Local"

        for i in pathsOut:

            if disk in i and lDisk not in i:
                paths += 1

        ret['Paths'] = paths

    stdin, stdout, stderr = ssh.exec_command('esxcfg-scsidevs -l')
    hdsOut = stdout.readlines()
    hd_num = 0
    is_hd = True
    if hdsOut:
        lineNum = 0
        for line in hdsOut:
            if lineNum % 14 == 0:
                if is_hd:
                    hd_num = hd_num + 1
                else:
                    is_hd = True
                v_header = "HD_%d_Vendor" % hd_num
                d_header = "HD_%d_Description" % hd_num
                m_header = "HD_%d_Model" % hd_num
                # r_header = "HD_%d_Rev." %hd_num 
                s_header = "HD_%d_Size" %hd_num 
                # ssd_header = "HD_%d_SSD" % hd_num
                # block_header = "HD_%d_Blocks" % hd_num
            hd_info = line.split()
            if hd_info[0] == 'Display':
                hd_info = hd_info[2:]
                ret[d_header] = ' '.join(hd_info)
            elif hd_info[0] == 'Vendor:':
                model_index = hd_info.index('Model:')
                rev_index = hd_info.index('Revis:')
                ret[v_header] = ' '.join (hd_info[1:model_index])
                ret[m_header] = ' '.join(hd_info[model_index + 1 : rev_index])
                # ret[r_header] = ' '.join(hd_info[rev_index + 1:])
            elif hd_info[0] == 'Size:':
                hd_info = hd_info[1:]
                hd_info[0] = str(int(hd_info[0]) / 1024)
                hd_info[1] = 'GB'
                ret[s_header] = ' '.join(hd_info)
            #elif 'SSD:' in hd_info:
                #ret[ssd_header] = hd_info[5]

            if ('CD-ROM' in hd_info) or ('USB' in hd_info):
                is_hd = False
            lineNum = lineNum + 1

    ## "NIC-# Speed", "NIC-# Description", "NIC-# Link" & "NIC-# MAC Address"
    stdin, stdout, stderr = ssh.exec_command('esxcfg-nics -l')
    nicsOut = stdout.readlines()

    if nicsOut:
        lineNum = 0

        for line in nicsOut:

            if re.search("Name", line):
                continue

            lineNum = lineNum + 1

            pattern = re.compile("\s+")
            column = pattern.split(line, 8)

            for item in column[8:9]:

                nameHeader = "NIC-%d Name" % lineNum
                nicName = column[0]
                #ret[nameHeader] = nicName

                ## "NIC-# Type" & "NIC-# Firmware"
                if nicName:
                    stdin, stdout, stderr = ssh.exec_command('esxcli network nic get -n %s' % nicName)
                    vmnicOut = stdout.readlines()

                if vmnicOut:
                    typeOut = findColParm(vmnicOut,"Cable Type")
                    firmOut = findColParm(vmnicOut,"Firmware Version")

                    if typeOut:
                        typeHeader = "NIC_%d_Type" % lineNum
                        ret[typeHeader] = typeOut

                    #if firmOut:
                        # firmHeader = "NIC_%d_Firmware" % lineNum
                        # ret[firmHeader] = firmOut

                spdHeader = "NIC_%d_Speed" % lineNum
                ret[spdHeader] = column[4]

                # macHeader = "NIC_%d_MAC_Address" % lineNum
                # ret[macHeader] = column[6]

                nicHeader = "NIC_%d_Description" % lineNum
                ret[nicHeader] = item.strip().replace(',', ' ').replace(']-', '')

                upHeader = "NIC_%d_Link" % lineNum
                ret[upHeader] = column[3]

        lineNum = 0

    ## "HBA-# Description"
    stdin, stdout, stderr = ssh.exec_command('esxcfg-scsidevs -a')
    hbaOut = stdout.readlines()

    ## "HBA-# WWPN"
    stdin, stdout, stderr = ssh.exec_command('esxcfg-mpath -m')
    mpathOut = stdout.readlines()

    if hbaOut:
        lineNum = 0

        for line in hbaOut:
            lineNum = lineNum + 1

            pattern = re.compile("\s+")
            column = pattern.split(line, 5)

            for item in column[4:5]:
                hbaHeader = "HBA_%d_Name" % lineNum
                hbaName = column[0]
                ret[hbaHeader] = hbaName

                hbaHeader = "HBA_%d_Description" % lineNum
                ret[hbaHeader] = column[5]

                # wwpnHeader = "HBA_%d_WWPN" % lineNum

                if mpathOut:

                    wwpn = findWWPN(mpathOut)

                    if wwpn:
                        ret[wwpnHeader] = wwpn

        lineNum = 0

        return ret

## --------------------------------------------------------------------
if __name__ == '__main__':
    main()
