#!/usr/bin/env python

"""
     Copyright (c) 2014 World Wide Technology, Inc. 
     All rights reserved. 

     Revision history:
     21 April 2015  |  1.0 - initial release
 
   
"""

DOCUMENTATION = '''
---
module: aci_gather_facts
author: Joel W. King, World Wide Technology
version_added: "1.0"
short_description: query the APIC controller for facts about a specified class or managed object
description:
    - This module issues a class or managed object query and returns the answer set as facts for use in a playbook

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

    query-target-fltr: 
        description:
            - a logical filter to be applied to the response
        required: false

    URI:
        description:
            - The URL required by APIC to issue the request.
        required: true

'''

EXAMPLES = '''
       
    export PYTHONPATH=/home/administrator/ansible/lib:/home/administrator/ansible/lib/ansible/modules/extras/network/
    
    ./bin/ansible prod-01 -m aci_gather_facts.py  -a "query-target-fltr=eq(aaaUser.descr,'aci_trainer') URI=/api/class/aaaUser.json host=10.255.23.121 username=admin password=FOO"


'''

import sys
import time
import logging
import httplib
import json

import AnsibleACI

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logfilename = __name__
logger = logging.getLogger(logfilename)
hdlrObj = logging.FileHandler("/tmp/%s_%s.log" % (logfilename, time.strftime("%j")))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlrObj.setFormatter(formatter)
logger.addHandler(hdlrObj)
logger.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# PROCESS
# ---------------------------------------------------------------------------

def process(cntrl, xml):
    """ We have all are variables and parameters set in the object, attempt to 
        login and post the data to the APIC
    """

    if cntrl.aaaLogin() != 200:
        return (1, "Unable to login to controller")

    rc = cntrl.genericGET()
    if rc == 200:
        return (0, "%s: %s" % (rc, httplib.responses[rc]))
    else:
        return (1, "%s: %s %s" % (rc, httplib.responses[rc], format_content(cntrl.get_content())))


# ---------------------------------------------------------------------------
# FORMAT_CONTENT
# ---------------------------------------------------------------------------
def format_content(content):
    """ formats the content into an Ansible fact  class : [ mo : 'attributes', mo : 'attributes', ...]
    """
    aci_facts = {}
    content = json.loads(content)["imdata"]                # remove the IMDATA wrapper
    for item in content:                                   # content is a list of one or more elements return for the class query
        d_item = dict(item)
        for key in d_item.keys():                          # should be only one element
            try:
                aci_facts[key]
            except KeyError:
                aci_facts[key] = []                        # create a dictionary with the class as the first key and an empty list as the value
            break
        
        mo = d_item[key]["attributes"]["dn"]
        attributes = d_item[key]["attributes"]
        aci_facts[key].append({mo: attributes})
    return aci_facts
        

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():

    module = AnsibleModule(
        argument_spec = dict(
            query-target-fltr = dict(required=False),
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

    if query-target-fltr:
        query-target-fltr = "?" + query-target-fltr

    cntrl.setgeneric_URL("%s://%s" + module.params["URI"] + query-target-fltr)
                                  
    code, response = process(cntrl)

    if code == 1:
        logger.error('DEVICE=%s STATUS=%s MSG=%s' % (module.params["host"], code, response))
        module.fail_json(msg=response)
    else:
        logger.info('DEVICE=%s STATUS=%s' % (module.params["host"], code))
        module.exit_json(changed=False, content=response)

    cntrl.aaaLogout()  
    return code


from ansible.module_utils.basic import *
main()


