# ansible-aci
Using Ansible for Cisco ACI Deployment and Orchestration

## Modules
This is demonstration of Ansible, an open source automation tool, which is used to configure a Cisco Application Centric Infrastructure (ACI) fabric. 

### ACI Install Config

Ansible playbooks are used to call a python module (aci_install_config.py) Which configures the fabric through the ACI controller (APIC) northbound REST API interface.

This video clip illustrates building a tenant configuration
https://youtu.be/PGBYIxEsqU8

### ACI Gather Facts

Additionally, a second module (aci_gather_facts.py) has been developed to issue class queries to the controller and return the results as ansible_facts. A sample playbook for this module is aci_gather_facts.yml

This video - https://youtu.be/Ec_ArXjgryo  demonstrates how both modules can be used together in a playbook to gather facts from the APIC and then using the variables returned, modify the configuration of the fabric based on the results.

Our use case is to meet the requirements of the network security administrator, implementing security policy filters (TCP_SMALL_SERVERS.xml) on all end-user tenants (ignoring the common, infra and mgmt tenants).   The playbook (security_policy_filter.yml) applies a Service Contract to a single tenant for testing, and then illustrates how we can use the ACI fabric to return the operating system version of a specific VM attached to the fabric.

The aci_gather_facts module can return managed object (MO) queries, see aci_mo_example.yml as an example of how to use this feature.

## Presentation

Theses modules were demonstrated at the Ansible Durham Meetup on 17 June 2015, the slides are located at http://www.slideshare.net/joelwking/ansible-durham-meetup


