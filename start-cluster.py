#!/usr/bin/env python2.7
import os
#from time import localtime, strftime, sleep
import time
import subprocess
import logging
import sys

#logging details- this will log to cluster.log and also display logger.info output in the terminal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
#handler = logging.FileHandler('cluster.log')
handler = logging.FileHandler("{0}/{1}.log".format('.', 'cluster')) #will log to cluster.log in current dir
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
#stream handler
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)


#display the time
now = time.localtime()
#min pulls string out of a set (these sets only have one item each)
#print ("Started running " + min({__file__}) + " at " + min({strftime('%X', now)}))
logger.info('================================================')
logger.info("Started running " + min({__file__}) + " at " + min({time.strftime('%X', now)}))
logger.info('================================================')


def cleanup():
  #remove any logs from previous restart
  #subprocess.call(['rm', '-f', 'cluster.log'])
  time.sleep(1)

def start_scm_server_and_all_agents():
  logger.info('-------------------------------------')
  logger.info('Restarting CM Server and CM Agents...')
  logger.info('-------------------------------------')

  #status=$(sudo systemctl status cloudera-scm-server.service | sed -n '3p' | cut -d ' ' -f6)
  bashCommand = "sudo systemctl status cloudera-scm-server.service"
  process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
  #output = subprocess.check_output(bashCommand, shell=True)
  output, error = process.communicate()
  
  #NEXT: parse the output
  #output = output.split("")
  logger.info(output)

#call the functions
cleanup()
start_scm_server_and_all_agents()
