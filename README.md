# ansible-aci
Using Ansible for Cisco ACI deployment

This is demonstration of Ansible, an open source automation tool, which is used to configure a Cisco Application Centric Infrastructure (ACI) fabric. Ansible playbooks are used to call a python module (aci_install_config.py) I developed which configures the fabric through the ACI controller (APIC) northbound REST API interface.

This video clip illustrates building a tenant configuration
https://youtu.be/PGBYIxEsqU8

Additionally, a second module (aci_gather_facts.py) has been developed to issue class queries to the controller and return the results as ansible_facts. The playbook apply_security_policy_filter.yml illustrates how to gather facts about the configured tenants, (ignoring the common, infra and mgmt tenants), and then push a security policy filter (TCP_SMALL_SERVERS.xml) to the list of tenants returned.

The aci_gather_facts module can return managed object queries, see aci_mo_example.yml as an example of how to use this feature.
