#!/usr/bin/env python
#
# Promnesia - Syslog Replayer
# The feeling of Deja Vu
# Written by: Jr Aquino <tanawts@gmail.com>

import os, re, datetime, time, fileinput, logging, logging.handlers, sys, types, socket, optparse
from logging.handlers import SysLogHandler

class progressbarClass: 
    def __init__(self, finalcount, progresschar=None):
        import sys
        self.finalcount=finalcount
        self.blockcount=0
        #
        # See if caller passed me a character to use on the
        # progress bar (like "*").  If not use the block
        # character that makes it look like a real progress
        # bar.
        #
        if not progresschar: self.block=chr(178)
        else:                self.block=progresschar
        #
        # Get pointer to sys.stdout so I can use the write/flush
        # methods to display the progress bar.
        #
        self.f=sys.stdout
        #
        # If the final count is zero, don't start the progress gauge
        #
        if not self.finalcount : return
        self.f.write('\n------------------ % Progress -------------------1\n')
        self.f.write('    1    2    3    4    5    6    7    8    9    0\n')
        self.f.write('----0----0----0----0----0----0----0----0----0----0\n')
        return

    def progress(self, count):
        #
        # Make sure I don't try to go off the end (e.g. >100%)
        #
        count=min(count, self.finalcount)
        #
        # If finalcount is zero, I'm done
        #
        if self.finalcount:
            percentcomplete=int(round(100*count/self.finalcount))
            if percentcomplete < 1: percentcomplete=1
        else:
            percentcomplete=100
            
        #print "percentcomplete=",percentcomplete
        blockcount=int(percentcomplete/2)
        #print "blockcount=",blockcount
        if blockcount > self.blockcount:
            for i in range(self.blockcount,blockcount):
                self.f.write(self.block)
                self.f.flush()
                
        #if percentcomplete == 100: self.f.write("\n")
        self.blockcount=blockcount
        return

def main(options, args):
    # Main Execution of Code

    # Mr Fox, what time is it?
    now = datetime.datetime.now()
    today = now.strftime("%Y%m%d")
    lasthour = now.strftime("%b %Oe %H:")
        
    filename = [options.logfile]

    hostname = options.hostname
    port = options.port

    # Write out to a debuging log
    debug = open('/tmp/dejavu.debug', 'w')
    
    if not options.time_period:
        options.time_period = lasthour
    
    # Set the Search Criteria
    logmatch = re.compile(r'%s.*%s' % (options.time_period, options.regex))
            
    # The Logger Setup
    logger = logging.getLogger()
    logger.setLevel( logging.INFO )    
    address = (hostname, port)
    facility = 1

    # Define Protocol   
    if options.tcp:
        socktype = socket.SOCK_STREAM
    else:
        socktype = socket.SOCK_DGRAM

    # Handler
    try:       
        handler = SysLogHandler(address, facility, socktype)
        logger.addHandler( handler )
    except:
        print('Connection refused: %s:%s' % (hostname, port))
    # Start your engines!
    
    if options.progress:

        # Get Total Filesize
        filesize = 0
        for file in filename:
            filesize += float(os.path.getsize(file))
        total = 0
        # Show the Progress
        sys.stdout.write(os.popen('clear').read())
        pb=progressbarClass(filesize,'*')
        start_time = time.time()
        for logline in fileinput.input(filename):
            match = logmatch.search(logline)
            if match:
                debug.write(logline)
                logger.info(logline)
            total += len(logline)
            if total > filesize:
                for file in filename:
                    pass
            else:
                pb.progress(total)

    else:
        start_time = time.time()
        for logline in fileinput.input(filename):
            match = logmatch.search(logline)
            if match:
                debug.write(logline)
                logger.info(logline)
    debug.close()
    end_time = time.time()
    duration =  end_time - start_time
    print('\nCompleted in %.2f seconds.' % duration)
        
def parseOptions():
    "The Options engine; some options are not optional"

    parser = optparse.OptionParser("Usage: %prog (-l logfile) (-H <hostname>) [-p <port>] [-tTP]")
    parser.add_option("-l", "--logfile", dest="logfile",
                    default=None, type="string", help="specify a log file to read.")

    parser.add_option("-H", "--hostname", dest="hostname",
                    default=None, type="string", help="specify a destination syslog server hostname.")
                    
    parser.add_option("-p", "--port", dest="port",
                    default=514, type="int", help="specify a port to send to.")
                    
    parser.add_option("-t", "--tcp", dest="tcp",
                    action="store_true", default=False, help="specify tcp protocol.")

    parser.add_option("-T", "--time_period", dest="time_period",
                    default='.*', type="string", help="specify a regex time period in strftime to match on.")

    parser.add_option("-r", "--regex", dest="regex",
                    default='', type="string", help="specify a regular expression string to match on.")

    parser.add_option("-P", "--progress", dest="progress",
                    action="store_true", default=False, help="display a progress meter.")
  
    (options, args) = parser.parse_args()

    if not (options.logfile or options.hostname):
        parser.error("You must specify an option. Use -h for help.")
    return options, args

if __name__ == '__main__':
    options, args = parseOptions()
    main(options, args)
