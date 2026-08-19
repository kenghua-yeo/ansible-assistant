These collections can be downloaded from various repositories:
- RHEL System Roles - https://console.redhat.com/ansible/automation-hub/collections/published/redhat/rhel_system_roles
- Red Hat Linux Upgrade (LEAPP) Automation - https://console.redhat.com/ansible/automation-hub/collections/published/redhat/leapp
- RHEL LVM Snapshots - https://console.redhat.com/ansible/automation-hub/collections/validated/infra/lvm_snapshots
- Red Hat Support Assist (support case , must gather automation) - https://console.redhat.com/ansible/automation-hub/collections/validated/infra/support_assist
- Windows Ops roles - https://console.redhat.com/ansible/automation-hub/collections/validated/infra/windows_ops

Note:
- Please install the roles in ./collections folder.
- Ask the agent to run trim_collections.py to remove collections artifacts that are not required.  
- Run the script build_catalog.py to update the catalog with the list of new roles added to the collections.
- You may need to 

For stanalone roles downloaded from Ansible Galaxy:
https://galaxy.ansible.com/ui/standalone/roles/RedHatOfficial/rhel9_cis_server_l1/
ansible-galaxy role install RedHatOfficial.rhel9_cis_server_l1 --roles-path ./collections/infra.rhel_ops/roles/

Standalone roles from Ansible Galaxy need to be reorganized to follow collection structure:
1. Creating collections/infra.rhel_ops/roles/
2. Moving collections/RedHatOfficial.rhel10_cis_server_l1/ → collections/infra.rhel_ops/roles/rhel10_cis_server_l1/
3. Moving collections/RedHatOfficial.rhel9_cis_server_l1/ → collections/infra.rhel_ops/roles/rhel9_cis_server_l1/ 
