#!/usr/bin/env python3

import subprocess
import os, signal, time

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

args = ['pg_ctl', '-D', 'radixdb', 'stop']
subprocess.run(args)

args = ['pg_ctl', '-D', 'radixdbw1', 'stop']
subprocess.run(args)

args = ['pg_ctl', '-D', 'radixdbw2', 'stop']
subprocess.run(args)

time.sleep(1)
check_kill_process('postgres')

args = ['pg_ctl', '-D', 'radixdb', '-l', 'logfile', 'start']
subprocess.run(args)

args = ['pg_ctl', '-D', 'radixdbw1', '-l', 'logfile-w1', 'start']
subprocess.run(args)
args = ['pg_ctl', '-D', 'radixdbw2', '-l', 'logfile-w2', 'start']
subprocess.run(args)
