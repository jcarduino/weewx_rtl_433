#!/usr/bin/python
#import sys
import subprocess
import time
import threading
import signal
import Queue
import os.path
import syslog

# Class begin ========================
class AsynchronousFileReader(threading.Thread):
    #
    #Helper class to implement asynchronous reading of a file
    #in a separate thread. Pushes read lines on a queue to
    #be consumed in another thread.
    #
    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        #The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            self._queue.put(line)

    def eof(self):
        #Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()
# End Class ===========================
def printdebug(str):
    global debug
    if debug:
        syslog.syslog(str)
    return
#       
# PROCESS DATA ========================
#
 
def process_data(msg):
    global data
    global rain
    print ("Process data: "+msg)
    sline=msg.split()
    #AlectoV1 Wind Sensor 43: Wind speed 0 units = 0.00 m/s: Wind gust 0 units = 0.00 m/s: Direction 90 degrees: Battery OK
    if 'AlectoV1 Wind Sensor' in msg:
        device=sline[5]
        device=device.rstrip(':')
        data['windDir']=sline[21]
        data['windSpeed']=sline[11]
        data['windGust']=sline[18]
        print "Updated: wind data: "+ data['windDir']+" "+  data['windSpeed']+" "+  data['windGust'] 
    if 'LaCrosse TX Sensor' in msg:
                #2015-07-02 06:37:34 LaCrosse TX Sensor 3c: Temperature 20.0 C / 68.0 F
                #2015-07-02 12:22:37 LaCrosse TX Sensor 3f: Humidity 58.0%
                device=sline[5]
                device=device.rstrip(':')
                d_data=sline[7]
                d_data=d_data.rstrip('%')
                print ("LaCrosse TX Sensor")
                #sensordata = (device,sline[6],d_data,'')
                if device=="3f" and sline[6]=='Temperature':
                    data['outTemp']==d_data
                    print "Updated: 3f outTemp: "+ data['outTemp']
                if device=="7e" and sline[6]=='Temperature':
                    data['inTemp']=d_data
                    print "Updated: 7e inTemp: "+ data['inTemp']
                if device=="3f" and sline[6]=='Humidity':
                    data['out_Humidity']=d_data
                    print "Updated: 3f outHum: "+ data['outHumidity']
                    
#3f buiten 7e binnen hum temp
    if 'AlectoV1 Sensor' in msg:
        #2015-07-02 12:56:37 AlectoV1 Sensor 43 Channel 1: Temperature 29.3 C: Humidity 49 : Battery OK    
        device=sline[4]
        device=device.rstrip(':')
        print("AlectoV1 Sensor")
        if device== "43" and sline[7]=='Temperature':#zolder
            data["extraTemp1"]=sline[8]
            print "Updated: 43 extraTemp1: "+ data['extraTemp1']
        if device== "43" and sline[10]=='Humidity':#zolder
            data["extraHumid1"]=sline[11]
            print "Updated: 43 extraHumid1: "+ data['extraHumid1']
        if device== "247" and sline[7]=='Temperature':#kelder
            data["extraTemp2"]=sline[8]
            print "Updated: 247 extraTemp2: "+ data['extraTemp2']
        if device== "247" and sline[10]=='Humidity':#kelder
            data["extraHumid2"]=sline[11]
            print "Updated: 247 extraHumid2: "+ data['extraHumid2'] 
    if 'AlectoV1 Rain Sensor' in msg:
        #2015-07-02 12:23:42 AlectoV1 Rain Sensor 133: Rain 0.00 mm/m2: Battery OK
        print "rain sensor!!!"
        device=sline[5]
        device=device.rstrip(':')
        data["rain"]=sline[7]
        print "Updated: rain: "+ data['rain']
    #print data
#====================================
#End data handler
#
def signal_handler(signal, frame):
        global process
        os.kill(process.pid, 9)#signal.SIGUSR1)
        # sys.exit(0)
        #Continue exit process main loop

if __name__ == '__main__':
    #capture control-c and kill signal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    rain="0.0"
    debug=1
    command=["/usr/bin/rtl_433","-R16","-R08"]
    data={'outTemp':"", 'inTemp':"", 'outHumidity':"", 'rain':"", 'extraHumid1':"", 'extraTemp1':"", 'windDir':"", 'windGust':"", 'windSpeed':"", 'altimeter':"", 'barometer':"", 'pressure':"", 'extraHumid2':"", 'extraTemp2':""}
    process = subprocess.Popen(command, stdout=subprocess.PIPE, preexec_fn=os.setsid)
    # Launch the asynchronous readers of the process' stdout and stderr.
    stdout_queue = Queue.Queue()
    stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
    stdout_reader.start()
    
    #main queue loop
    # Check the queues if we received some output (until there is nothing more to get).
    while not stdout_reader.eof():
        # Show what we received from standard output.
        while not stdout_queue.empty():
            process_data(stdout_queue.get())    
        # Sleep a bit before asking the readers again.
        time.sleep(.1)
    # end main loop
    
    syslog.syslog("Normal exitchain")
    # Let's be tidy and join the threads we've started.
    stdout_reader.join()
    # Close subprocess' file descriptors.
    process.stdout.close()
    syslog.syslog("Exit program")
