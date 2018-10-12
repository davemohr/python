#!/usr/bin/env python2.7
import os
#from time import localtime, strftime, sleep
import time
import subprocess
import logging
import sys

def start_log():
	#logging details- this will log to cluster.log and also display logger.info output in the terminal
	global logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	# create a file handler
	handler = logging.FileHandler("{0}/{1}.log".format('.', 'cluster')) #will log to cluster.log in current dir
	handler.setLevel(logging.INFO)
	# create a logging format
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	# add the handlers to the logger
	logger.addHandler(handler)
	# stream handler 
	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

def output_time(startorend):
	now = time.localtime()
	#min pulls string out of a set (these sets only have one item each)
	logger.info('================================================')
	logger.info(startorend + " running " + min({__file__}) + " at " + min({time.strftime('%X', now)}))
	logger.info('================================================')

def return_os_service_status(service_name):
  """
  Takes OS service name as a string, returns the service status.
  Assumes systemd (CentOS/RHEL 7).
  """
  os_service_check = "sudo systemctl status " + service_name
  #run the query
  process = subprocess.Popen(os_service_check.split(), stdout=subprocess.PIPE)
  output, error = process.communicate()

  #output the entire response
  logger.info(output)
  
  global service_status

  #parse the output
  service_check_list = output.split(" ")
  
  #the parsed value for dead services can vary, this does a "contains" check
  if any("dead" in s for s in service_check_list):
	dead = "yes"

  #debug
  logger.info(service_check_list)

  if (service_check_list.count('(running)') > 0 and service_check_list.count('active') > 0):
    logger.info(service_name + ' is running')
    time.sleep(3)
    service_status = "running"
  elif (dead == "yes" and service_check_list.count('inactive') > 0):
    logger.info(service_name + ' is not running')
    time.sleep(3)
    service_status = "dead"
  elif (service_check_list.count('failed') > 0 ):
	logger.warn(service_name + ' failed')
	service_status = "failed"
  	time.sleep(3)
  return service_status

def restart_os_service(service_name):
	"""
	Takes OS service name as a string, restarts the service.
	Assumes systemd (CentOS/RHEL 7).
	"""
	os_service_restart = "sudo systemctl restart " + service_name
	logger.info('HERE is the command about to be run: ' + os_service_restart)
	#run the restart action
	process = subprocess.Popen(os_service_restart.split(), stdout=subprocess.PIPE)
	output, error = process.communicate()
 	#output the entire response
	logger.info(output)

def start_scm_server_and_all_agents():
  logger.info('-------------------------------------')
  logger.info('Restarting CM Server and CM Agents...')
  logger.info('-------------------------------------')

  #CM SERVER	
  logger.info('Check if CM Server is running...')
  cm_server_status = return_os_service_status('cloudera-scm-server')
  logger.info('CM server is ' + cm_server_status )
  
  if (cm_server_status == 'dead' or cm_server_status == 'failed'):
	
	logger.info('Restarting CM Server...')
	cm_server_restart = restart_os_service('cloudera-scm-server')
	
	logger.info('Verifying CM Server is now running')
	cm_server_status = return_os_service_status('cloudera-scm-server')
	logger.info('CM server is ' + cm_server_status )

  #CM AGENT	
  logger.info('Check if CM Agent is running...')
  cm_agent_status = return_os_service_status('cloudera-scm-agent')
  logger.info('CM agent is ' + cm_agent_status )
  
  if (cm_agent_status == 'dead' or cm_agent_status == 'failed'):
        
    logger.info('Restarting CM Agent...')
    cm_agent_restart = restart_os_service('cloudera-scm-agent')
        
    logger.info('Verifying CM Agent is now running')
    cm_agent_status = return_os_service_status('cloudera-scm-agent')
    logger.info('CM agent is ' + cm_agent_status )


#call the functions
start_log()
output_time('Started')
start_scm_server_and_all_agents()
output_time('Ended')
logger.info('\n\n')

