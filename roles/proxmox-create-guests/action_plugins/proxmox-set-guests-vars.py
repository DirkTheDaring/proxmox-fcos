# validation of ansible variables

# Action Module
# action_plugins are a special type of module, or a compliment to existing 
# modules. action_plugins get run on the ‘master’ instead of on the target,
# for modules like file/copy/template, some of the work needs to be done on
# the master before it executes things on the target. The action plugin 
# executes first and can then execute (or not) the normal module”.

# Special variables:
# https://docs.ansible.com/ansible/latest/reference_appendices/special_variables.html

from ansible.plugins.action import ActionBase
import fnmatch

# ActionModule has a new instance per host 

class ActionModule(ActionBase):
     def create_list_from_str(self, flash_list, str_list, allowed_hosts):
         array=[]
         str_list = str_list.strip()
         if str_list == "":
             return
         str_array = str_list.split(',')
         for item in str_array:
             item = item.strip()
             if item in allowed_hosts and item not in flash_list:
                flash_list.append(item)
             else:
                 for allowed_host in allowed_hosts:
                     if not fnmatch.fnmatch(allowed_host,item):
                         continue
                     # no duplicates
                     if allowed_host in flash_list:
                         continue
                     flash_list.append(allowed_host)

     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         inventory_hostname = task_vars['inventory_hostname']
         hostvars = task_vars['hostvars']
         groups = task_vars['groups']

         ansible_facts={}
         hostvar = hostvars[inventory_hostname]
         proxmox_guests_group = hostvar['proxmox_guests_group']


         proxmox_guests_array = groups[proxmox_guests_group]

         proxmox_guests_list = []
         for proxmox_guests_item in proxmox_guests_array:
             item = hostvars[proxmox_guests_item]
             if 'enabled' in item and str(item['enabled']).lower() == "false":
                 continue
             if 'kvm_host' not in item:
                 continue
             kvm_host = item['kvm_host']
             if kvm_host != inventory_hostname:
                 continue
             proxmox_guests_list.append(proxmox_guests_item)
         # proxmox_guest_list is now per host
         ansible_facts['proxmox_guests_list'] = proxmox_guests_list

         flash_list=[]
         for item in proxmox_guests_list:
             guest = hostvars[item]
             #print(guest)
             if 'flash' not in guest:
                 continue
             val = guest['flash']
             # sometimes a boolean is returned, sometimes a string --> cast it to string, as string to boolean does not what you would expect
             val = str(val)
             val = val.lower()
             if val in [ 'true' ]:
                 flash_list.append(item)

         if 'flash' in task_vars:
             str_list = task_vars['flash']
             print(str_list)
             self.create_list_from_str(flash_list, str_list, proxmox_guests_list)

         ansible_facts["flash_list"] = flash_list
         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False
         return result
