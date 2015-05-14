We implemented Ansible Tower in our Advanced Technology Center and needed to make some changes to run these modules under Tower.

After implementing Tower, do the following:

1. Edit `/etc/ansible/ansible.cfg`
   add (or uncomment) the line
   `library        = /usr/share/ansible/`

2. Download the modules in the directory `/usr/share/ansible/`
   in my deployment, the directory exists, but is empty.
   
3. The files are owned/group by `root root` and are `-rw-r--r--`
