#!/usr/bin/env python

"""Multi thread nikto scan in parallel"""

__author__      = "0x25"
__copyright__   = "GNU General Public Licence"

import shlex, subprocess, time, sys, os, argparse
from multiprocessing import Process, Queue

# configuration
niktoPath="/usr/bin/nikto"

# child process
def scan(procId,jobs,cmd):
        try:
                while True:
                        jobData = jobs.get_nowait()
                        ip = jobData['ip']
                        print "[%s] start scan : %s"%(procId,ip)

                        fname =  "scan/%s.log"%(ip)
                        cmd = "%s %s -ask no -o scan/%s.csv -h %s"%(niktoPath,cmd,ip,ip)

                        args = shlex.split(cmd)
                        p = subprocess.Popen(args,stdout=open(fname, 'w'))

                        while p.poll() is None:
                                print "[%s]  process scan : %s"%(procId,ip)
                                time.sleep(5)
        except:
                pass # when job empty
                #print "Unexpected error:", sys.exc_info()[0]
                #raise


def main():
        if not os.path.exists(niktoPath):
                print "Nikto not found\nPlease install it to continue !"
                exit(2)
        if len(sys.argv) <= 1:
                print "Use -h to see help"
                exit(2)

        defaultNiktoCmd = '-T x6 -p 80,443 -until 45m'
        defaultThread = 4

        description ="\033[1;31m Parallel scan with nikto. Default value : thread [%s] nikto cmd [%s] \033[0m"%(defaultThread,defaultNiktoCmd)
        epilog="\033[0;35m If you like this tool you can send me some monero \o/ { 4Ahnr36hZQsJ3P6jowXvs7cLkSVbkq2KyfQBVURYVftcj9tDoA592wT1jskroZEk2QDEZFPYMLqVvJWZHecFwQ9nL15SzRG } \033[0m"

        # parse args
        parser = argparse.ArgumentParser(description=description, epilog=epilog)
        parser.add_argument('-t','--thread', type=int, default=defaultThread, help='Number of concurent thread')
        parser.add_argument('-f','--file',required=True, help='File with one URL/IP line by line')
        parser.add_argument('-c','--cmd',default=defaultNiktoCmd, help='Set nikto parameters (don\'t add output). Use quote !')
        args = parser.parse_args()

        filename = args.file
        nbProcess = args.thread
        cmd = args.cmd

        # start code
        jobs = Queue()
        pool=[]

        for procId in range(nbProcess):
                print "start process [%s/%s]"%(procId,nbProcess)
                pool.append(Process(target=scan, args=(procId,jobs,cmd)))

        with open(filename) as f:
                ips = f.read().splitlines()

        for ip in ips:
                jobs.put({'ip': ip})

        print "load %s jobs in queue"%(jobs.qsize())

        for proc in pool:
                proc.start()

        for proc in pool:
                proc.join()


# main
if __name__ == '__main__':
        main()
