#!/usr/bin/env python2.7

#This program assumes you already ran these commands on the server (the cp and chown commands make the modules available to the correct python):
#sudo pip install cm_client
#sudo yum install -y python-pip
#sudo pip install cm_client
#sudo pip install sh
#sudo cp sudo cp -r /lib/python2.7/site-packages/cm_client /opt/cloudera/parcels/Anaconda/lib/python2.7/site-packages/
#sudo chown -R cloudera-scm:cloudera-scm /opt/cloudera/parcels/Anaconda/lib/python2.7/site-packages/cm_client
#sudo cp -r /lib/python2.7/site-packages/sh* /opt/cloudera/parcels/Anaconda/lib/python2.7/site-packages/
#sudo chown -R cloudera-scm:cloudera-scm /opt/cloudera/parcels/Anaconda/lib/python2.7/site-packages/sh*

import os
import time
import subprocess
import logging
import sys
import psutil
import commands

#Setup CM API Client - This program only works with the newer CM 6 API
import cm_client
from cm_client.rest import ApiException
from pprint import pprint

# Configure HTTP basic authorization: basic
cm_client.configuration.username = 'admin'
cm_client.configuration.password = 'admin'
api_host = 'http://localhost.localdomain'
port = '7180'
api_version = 'v30'
api_url = api_host + ':' + port + '/api/' + api_version
api_client = cm_client.ApiClient(api_url)
cluster_api_instance = cm_client.ClustersResourceApi(api_client)

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

  #debug
  #output the entire response
  #logger.info(output)

  global service_status

  #parse the output
  service_check_list = output.split(" ")

  #the parsed value for dead services can vary, this does a "contains" check
  global servicedead
  servicedead = "unknown"
  if any("dead" in s for s in service_check_list):
    servicedead = "yes"

  #debug
  #logger.info(service_check_list)

  if (service_check_list.count('(running)') > 0 and service_check_list.count('active') > 0):
    logger.info(service_name + ' is running')
    time.sleep(3)
    service_status = "running"
  elif (servicedead == "yes" and service_check_list.count('inactive') > 0):
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

    #debug
    #logger.info('HERE is the command about to be run: ' + os_service_restart)

    #run the restart action
    process = subprocess.Popen(os_service_restart.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    #debug
    #output the entire response
    #logger.info(output)

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

    logger.info('Verifying CM Server is now running...')
    cm_server_status = return_os_service_status('cloudera-scm-server')
    logger.info('CM server is ' + cm_server_status )

    #check cpu utization of the cloudera-scm-server process and wait til it goes below some %
    #
    #p1 = subprocess.Popen(["sudo", "netstat", "-tulpn"], stdout=subprocess.PIPE)
    #p2 = subprocess.Popen(["grep", "7180"], stdin=p1.stdout, stdout=subprocess.PIPE)
    #p1.stdout.close()
    #p2.communicate()
    cmserver_pid = 0.0
    while cmserver_pid == 0.0:
        time.sleep(5)
        cmserver_pid=commands.getoutput('sudo netstat -tulpn | grep 7180 | gawk \'{ print $7}\' | cut -d \'/\' -f1')

    cmserver_process = psutil.Process(float(cmserver_pid))
    cmserver_mem_usage = cmserver_process.memory_percent()

    while cmserver_mem_usage > 20.0:
        time.sleep(5)
        logger.info('CM server is still starting. Memory usage is ' + str(cmserver_mem_usage) + " percent.")

  #CM AGENT #
  logger.info('Check if CM Agent is running...')
  cm_agent_status = return_os_service_status('cloudera-scm-agent')
  logger.info('CM agent is ' + cm_agent_status )

  if (cm_agent_status == 'dead' or cm_agent_status == 'failed'):

    logger.info('Restarting CM Agent...')
    cm_agent_restart = restart_os_service('cloudera-scm-agent')

    logger.info('Verifying CM Agent is now running')
    cm_agent_status = return_os_service_status('cloudera-scm-agent')
    logger.info('CM agent is ' + cm_agent_status )
def get_cluster_info():
    api_response = cluster_api_instance.read_clusters(view='SUMMARY')
    global cluster
    for cluster in api_response.items:
        logger.info('Cluster name: ' +  cluster.name)
        logger.info('Cluster version: ' + cluster.full_version)

    if cluster.name == '':
        logger.info('No cluster found, exiting')
        sys.exit()

    if cluster.full_version.startswith("6."):
        global services_api_instance
        services_api_instance = cm_client.ServicesResourceApi(api_client)

        #get a list of the deployed services)
        services = services_api_instance.read_services(cluster.name, view='FULL')
        global service
        for service in services.items:
            #print service.display_name, "-", service.type
            logger.info('service display name: ' + service.display_name +  ", Service type: " + service.type)

            #uncomment these lines to see role info
            #roles = services_api_instance.read_roles(cluster.name, service.name)
            #for role in roles.items:
            #   print "Role name: %s\nState: %s\nHealth: %s\nHost: %s" % (role.name, role.role_state, role.health_summary, role.host_ref.host_id)

            #create handles for services
            if service.type == 'HDFS':
                global hdfs
                global hdfs_service_state
                hdfs = service.name
                hdfs_service_state = service.service_state
            elif service.type == 'HIVE':
                global hive
                global hive_service_state
                hive = service.name
                hive_service_state = service.service_state
            elif service.type == 'SPARK_ON_YARN':
                global sparkOnYarn
                global sparkOnYarn_service_state
                sparkOnYarn = service.name
                sparkOnYarn_service_state = service.service_state
            elif service.type == 'ZOOKEEPER':
                global zookeeper
                global zookeeper_service_state
                zookeeper = service.name
                zookeeper_service_state = service.service_state
            elif service.type == 'OOZIE':
                global oozie
                global oozie_service_state
                oozie = service.name
                oozie_service_state = service.service_state
            elif service.type == 'KAFKA':
                global kafka
                global kafka_service_state
                kafka = service.name
                kafka_service_state = service.service_state
            elif service.type == 'KUDU':
                global kudu
                global kudu_service_state
                kudu = service.name
                kudu_service_state = service.service_state
            elif service.type == 'HUE':
                global hue
                global hue_service_state
                hue = service.name
                hue_service_state = service.service_state
            elif service.type == 'IMPALA':
                global impala
                global impala_service_state
                impala = service.name
                impala_service_state = service.service_state
            elif service.type == 'YARN':
                global yarn
                global yarn_service_state
                yarn = service.name
                yarn_service_state = service.service_state
            elif service.type == 'HBASE':
                global hbase
                global hbase_service_state
                hbase = service.name
                hbase_service_state = service.service_state
            else:
                logger.info('No services found.')

def restart_clock():
    logger.info('Restarting Oozie service...')
    restart_clock = commands.getoutput('sudo systemctl restart chronyd')
    time.sleep(5)

def deploy_stale_configs():
    logger.info('Restarting Oozie service...')
    restartOozie = services_api_instance.restart_command(cluster.name, oozie)
    logger.info ('Restart of Oozie still in progress? ' + str(restartOozie.active))

    logger.info('Restarting Kudu service...')
    restartKudu = services_api_instance.restart_command(cluster.name, kudu)
    logger.info ('Restart of Kudu still in progress? ' + str(restartKudu.active))

    logger.info('Verifying Oozie successfully restarted...')

def wait(restartOozie, timeout=None):
    SYNCHRONOUS_COMMAND_ID = -1
    if restartOozie.id == SYNCHRONOUS_COMMAND_ID:
        return restartOozie

    SLEEP_SECS = 5
    if timeout is None:
        deadline = None
    else:
        deadline = time.time() + timeout

    try:
        cmd_api_instance = cm_client.CommandsResourceApi(api_client)
        while True:
            global restartOozie
            restartOozie = cmd_api_instance.read_command(long(restartOozie.id))
            pprint(restartOozie)
            if not restartOozie.active:
                return restartOozie

            if deadline is not None:
                now = time.time()
                if deadline < now:
                    return restartOozie
                else:
                    time.sleep(min(SLEEP_SECS, deadline - now))
            else:
                time.sleep(SLEEP_SECS)
    except ApiException, e:
        print "Exception reading and waiting for command %s\n" %e

    #print "Active: %s. Success: %s" % (restartOozie.active, restartOozie.success)


    #while restartOozie.active == True:
    #   time.sleep(5)
    #   logger.info('restart still in progress')
    #for service in services.items:
    #   logger.info('action completed, now verifying success')
    #   if service.type == 'OOZIE':
    #       oozie_service_state = service.service_state
    #       logger.info('oozie_service_state = ' + oozie_service_state)
    #if str(oozie_service_state) != "STARTED":
    #   logger.warn('ISSUE: Oozie failed to start. It has status' + oozie_service_state)



def final_message():
    logger.info('NOTE: It may take up to three minutes after this script has completed \
        running before all service show a healthy status in Cloudera Manager. Please \
        give it time.')

#call the functions
start_log()
output_time('Started')
start_scm_server_and_all_agents()
get_cluster_info()
restart_clock()
deploy_stale_configs()
wait(restartOozie)
output_time('Ended')
logger.info('\n\n')
                                                                        
