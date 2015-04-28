#!/usr/bin/env python

"""
     Copyright (c) 2014 World Wide Technology, Inc. 
     All rights reserved. 

     Revision history:
     27 March 2015  |  1.0 - initial release
     30 March 2015  |  1.1 - tested version using playbook, added output of "content" to error message
     31 March 2015  |  1.2 - added documentation
      7 April 2015  |  2.0 - refactor for github
      8 April 2015  |  2.1 - added missing documentation
     28 April 2015  |  2.2 - program documenttion updates
   
"""

DOCUMENTATION = '''
---
module: aci_install_config
author: Joel W. King, World Wide Technology
version_added: "2.2"
short_description: Loads a configuration file to the northbound interface of a Cisco ACI controller (APIC)
description:
    - This module reads an XML configuration file and posts to the URI specified to the APIC northbound interface

      The module writes a log file to the /tmp directory and imbeds the julian date in the file name. 
      For example, this file is for day 50, e.g. /tmp/nxapi_install_config_050.log

      Refer to the Cisco APIC REST API User Guide for more info on xml and URI formats.

 
requirements:
    - The module uses the AnsibleACI python module, which must be specified in the PYTHONPATH or in the local directory

options:
    host:
        description:
            - The IP address or hostname of the ACI controller (APIC)
        required: true

    username:
        description:
            - Login username
        required: true

    password:
        description:
            - Login password
        required: true

    xml_file:
        description:
            - Path to the file containing the XML configuration data.
        required: true

    URI:
        description:
            - The URL required by APIC to issue the request.
        required: true

'''

EXAMPLES = '''
       
    export PYTHONPATH=/home/administrator/ansible/lib:/home/administrator/ansible/lib/ansible/modules/extras/network/
    
    ./bin/ansible prod-01 -m aci_install_config.py  -a "xml_file=/home/administrator/ansible/CFGS/aaaUser_Student9.xml URI=/api/mo/uni/userext/user-Student9.xml host=prod-01 username=admin password=FOO"

    ./bin/ansible-playbook ./aci.yml 


'''

import sys
import time
import logging
import httplib

import AnsibleACI

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logfilename = 'aci_install_config'
logger = logging.getLogger(logfilename)
hdlrObj = logging.FileHandler("/tmp/%s_%s.log" % (logfilename, time.strftime("%j")))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlrObj.setFormatter(formatter)
logger.addHandler(hdlrObj)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
#  READXML
# ---------------------------------------------------------------------------

def readxml(file_name):
    """" read xml files for processing """
    try:
        xmlfo = open(file_name, "r")
        data = xmlfo.read()
    except:
        return None
    return data

# ---------------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------------

def process(cntrl, xml):
    """ We have all are variables and parameters set in the object, attempt to 
        login and post the data to the APIC
    """
    if xml == None:
        return (1, "Unable to read XML file.")              

    cntrl.setgeneric_XML(xml)
    if cntrl.aaaLogin() != 200:
        return (1, "Unable to login to controller")

    rc = cntrl.genericPOST()
    if rc == 200:
        return (0, "%s: %s" % (rc, httplib.responses[rc]))
    else:
        return (1, "%s: %s %s" % (rc, httplib.responses[rc], cntrl.content))




# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():

    module = AnsibleModule(
        argument_spec = dict(
            xml_file = dict(required=True),
            URI = dict(required=True),
            host = dict(required=True),
            username = dict(required=True),
            password  = dict(required=True),
            debug = dict(required=False)
         ),
        check_invalid_arguments=False,
        add_file_common_args=True
    )
    
    cntrl = AnsibleACI.Connection()
    cntrl.setcontrollerIP(module.params["host"])
    cntrl.setUsername(module.params["username"])                               
    cntrl.setPassword(module.params["password"])
    cntrl.setgeneric_URL("%s://%s" + module.params["URI"])
    xml = readxml(module.params["xml_file"]) 
                                  
    code, response = process(cntrl, xml)

    if code == 1:
        logger.error('DEVICE=%s STATUS=%s MSG=%s' % (module.params["host"], code, response))
        module.fail_json(msg=response)
    else:
        logger.info('DEVICE=%s STATUS=%s' % (module.params["host"], code))
        module.exit_json(changed=True, content=response)

    cntrl.aaaLogout()  
    return code


from ansible.module_utils.basic import *
main()


