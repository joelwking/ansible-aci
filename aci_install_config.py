#!/usr/bin/env python

"""
     Copyright (c) 2015 World Wide Technology, Inc. 
     All rights reserved. 

     Revision history:
     27 March 2015  |  1.0 - initial release
     30 March 2015  |  1.1 - tested version using playbook, added output of "content" to error message
     31 March 2015  |  1.2 - added documentation
      7 April 2015  |  2.0 - refactor for github
      8 April 2015  |  2.1 - added missing documentation
     28 April 2015  |  2.2 - program documenttion updates
     14 May   2015  |  2.3 - modification for running under Ansible Tower
     17 June  2015  |  2.4 - corrected cntrl.aaaLogout() placement
     31 July  2015  |  2.5 - added userid to log file name (ACI training class)
     25 Aug   2015  |  2.6 - added response requested flag 
     26 Aug   2015  |  2.7 - added idempotency logic for changed flag
      3 Sept  2015  |  2.8 - included status="deleted" as an option to trigger the change flag
   
"""

DOCUMENTATION = '''
---
module: aci_install_config
author: Joel W. King, World Wide Technology
version_added: "2.8"
short_description: Loads a configuration file to the northbound interface of a Cisco ACI controller (APIC)
description:
    - This module reads an XML configuration file and posts to the URI specified to the APIC northbound interface

      The module writes a log file to the /tmp directory and imbeds the julian date in the file name. 
      For example, this file is for day 215, e.g. /tmp/aci_install_config_kingjoe_215.log

      Refer to the Cisco APIC REST API User Guide for more info on xml and URI formats.

 
requirements:
    - The module uses the AnsibleACI python module, which must be specified in the PYTHONPATH, in the local directory
      or in the library directory specified in the ansible.cfg file (e.g. library = /usr/share/ansible/).

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

    debug:
        description:
            - Flag to indicate if output should return a response from the REST call.
        required: false

'''

EXAMPLES = '''

    When running Ansible (not using Tower) include in your PYTHONPATH the location of these modules
       
    export PYTHONPATH=/home/administrator/ansible/lib:/home/administrator/ansible/lib/ansible/modules/extras/network/

    in the above example, Ansible was installed under /home/administrator/ and these modules were placed in /extras/network
 
    
    ./bin/ansible prod-01 -m aci_install_config.py  -a "xml_file=/home/administrator/ansible/CFGS/aaaUser_Student9.xml URI=/api/mo/uni/userext/user-Student9.xml host=prod-01 username=admin password=FOO"

    ./bin/ansible-playbook ./aci.yml 


'''

import sys
import time
import logging
import httplib
import getpass

# ---------------------------------------------------------------------------
# IMPORT LOGIC 
# ---------------------------------------------------------------------------
"""
    When running under Ansible Tower, put this module and AnsibleACI in 
    /usr/share/ansible and modify /etc/ansible/ansible.cfg to include 
    library        = /usr/share/ansible/
"""
try:
    import AnsibleACI
except ImportError:
    sys.path.append("/usr/share/ansible")
    import AnsibleACI

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logfilename = 'aci_install_config'
logger = logging.getLogger(logfilename)
hdlrObj = logging.FileHandler("/tmp/%s_%s_%s.log" % (logfilename, getpass.getuser(), time.strftime("%j")))
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
        login and post the data to the APIC. If debug is enabled, we will also 
        include the content returned from the controller due to  ?rsp-subtree=modified
        provided on all POST requests.
      
        When imdata contains status="created", "modified", or "deleted", the config has changed,
        otherwise, not. This implements idempotency for this module.
    """
    response_requested = ""
    changed_msg = ['status="created"', 'status="modified"', 'status="deleted"']
    changed = False

    if xml == None:
        return (1, False, "Unable to read XML file.")              

    cntrl.setgeneric_XML(xml)
    if cntrl.aaaLogin() != 200:
        return (1, False, "Unable to login to controller")

    rc = cntrl.genericPOST()
    if rc == 200:
        if cntrl.debug:                                    # when debug enabled, include
            response_requested = cntrl.content             # response data in output 
        for item in changed_msg:
            if item in cntrl.content:
                changed = True
        return (0, changed, "%s: %s %s" % (rc, httplib.responses[rc], response_requested))
    else:
        return (1, False, "%s: %s %s" % (rc, httplib.responses[rc], cntrl.content))




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
            debug = dict(required=False, default=False, type='bool')
         ),
        check_invalid_arguments=False,
        add_file_common_args=True
    )
    
    #  Create an Connection object for the controller and set parameters
    cntrl = AnsibleACI.Connection()
    cntrl.setcontrollerIP(module.params["host"])
    cntrl.setUsername(module.params["username"])                               
    cntrl.setPassword(module.params["password"])
    cntrl.setDebug(module.params["debug"])

    cntrl.setgeneric_URL("%s://%s" + module.params["URI"] + "?rsp-subtree=modified")
    xml = readxml(module.params["xml_file"]) 

    #  Process request                     
    code, changed, response = process(cntrl, xml)
    cntrl.aaaLogout()

    if code == 1:
        logger.error('DEVICE=%s STATUS=%s MSG=%s' % (module.params["host"], code, response))
        module.fail_json(msg=response)
    else:
        logger.info('DEVICE=%s STATUS=%s CHANGED=%s MSG=%s' % (module.params["host"], code, changed, response))
        module.exit_json(changed=changed, content=response)
  
    return code


from ansible.module_utils.basic import *
main()


