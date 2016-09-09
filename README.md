# ansible-aci
Using Ansible for Cisco ACI Deployment and Orchestration.

## Modules
This is demonstration of Ansible, an open source automation tool, which is used to configure a Cisco Application Centric Infrastructure (ACI) fabric. 

These modules have been tested on APIC Version: 1.2(1m)

### ACI Clone Tenant

This module (aci_clone_tenant.py)  creates a new tenant based on a reference, or template tenant. You specify the new tenant name and a description. All references to the template tenant are changed to refer to the new tenant name. This module has been updated to reference an input and output fabric, so tenants can be moved from a test or dev environment to production.

This video clip illustrates the concept of cloning a tenant configuration
https://youtu.be/vl_saLaP1y8

### ACI Install Config

Ansible playbooks are used to call a python module (aci_install_config.py) Which configures the fabric through the ACI controller (APIC) northbound REST API interface.

This video clip illustrates building a tenant configuration
https://youtu.be/PGBYIxEsqU8

### ACI Gather Facts

Additionally, a second module (aci_gather_facts.py) has been developed to issue class queries to the controller and return the results as ansible_facts. A sample playbook for this module is aci_gather_facts.yml

This video - https://youtu.be/Ec_ArXjgryo  demonstrates how both modules can be used together in a playbook to gather facts from the APIC and then using the variables returned, modify the configuration of the fabric based on the results.

Our use case is to meet the requirements of the network security administrator, implementing security policy filters (TCP_SMALL_SERVERS.xml) on all end-user tenants (ignoring the common, infra and mgmt tenants).   The playbook (security_policy_filter.yml) applies a Service Contract to a single tenant for testing, and then illustrates how we can use the ACI fabric to return the operating system version of a specific VM attached to the fabric.

The aci_gather_facts module can return managed object (MO) queries, see aci_mo_example.yml as an example of how to use this feature.

## Installation
Assuming you are running this playbook from userid 'administrator'  with sudo permissions, download the the Ansible modules to /usr/share/ansible.
```
sudo rm -rf /usr/share/ansible
sudo mkdir /usr/share/ansible
sudo chown administrator  /usr/share/ansible
sudo chgrp administrator  /usr/share/ansible
```
The ansible.cfg file should specify the directory in the library variable:
```
library        = /usr/share/ansible/
```
You may also need to run `dos2unix` on the downloaded module(s)

## Presentation

Theses modules were demonstrated at the Ansible Durham Meetup on 17 June 2015, the slides are located at http://www.slideshare.net/joelwking/ansible-durham-meetup

Presentation for the vNPUG: Configuration Management Series w/Ansible 
http://www.npug.net/past-events/
http://www.slideshare.net/joelwking/one-tool-two-fabrics-ansible-and-nexus-9000

## Press Releases
Red Hat Brings DevOps to the Network with New Ansible Capabilities https://www.redhat.com/en/about/press-releases/red-hat-brings-devops-network-new-ansible-capabilities
