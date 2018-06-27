# ansible-aci
Using Ansible for Cisco ACI Deployment and Orchestration.

## Overview
This is demonstration of Ansible, an open source automation tool, which is used to configure a Cisco Application Centric Infrastructure (ACI) fabric. 

## Prior Work

This repo has been revised to reflect the changes and enhancements in the Cisco ACI modules released first in Ansible 2.4 and later releases. I have created a [deprecated](https://github.com/joelwking/ansible-aci/tree/deprecated) branch with the original work, and have revised the master branch to focus on using the ACI modules released with Ansible.

## Playbooks

### aci_tenant_demo
This playbook adds or deletes an ACI Tenant.

### aci_contracts_filters
This playbook adds or deletes the Contract, Subject, Filter, Filter entries for a tenant in an ACI fabric. The input file has been converted to YAML from the output of a Tetration ADM run. This use case was demonstrated at [DevNet Create 2018](https://www2.wwt.com/all-blog/devnet-create-2018/). 

## Author
joel.king@wwt.com
