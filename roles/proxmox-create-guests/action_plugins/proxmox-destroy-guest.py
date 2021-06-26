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


     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         inventory_hostname = task_vars['inventory_hostname']
         hostvars = task_vars['hostvars']
         groups = task_vars['groups']

         ansible_facts={}
         hostvar = hostvars[inventory_hostname]
          
         for var in ['proxmox_guests_group', 'proxmox_cluster']:
             if var not in hostvar:
                 result['msg'] = "mandatory var not set: " + var
                 result['failed'] = True
                 return result

         proxmox_guests_group = hostvar['proxmox_guests_group']
         proxmox_cluster      = hostvar['proxmox_cluster']

         flash_selector = []
         if 'flash' in task_vars:
             flash = task_vars['flash']
             flash_selector = [ x.strip() for x in flash.split(',') ]
         print(flash_selector) 

         proxmox_guests_array = groups[proxmox_guests_group]

         destroy_guest_list = []
         for proxmox_guests_item in proxmox_guests_array:
             item = hostvars[proxmox_guests_item]
             if 'kvm_id' not in item:
                 continue
             kvm_id = str(item['kvm_id'])
             if kvm_id not in proxmox_cluster:
                 continue
             entry =  proxmox_cluster[kvm_id]
             if 'kvm_host' not in entry:
                 continue
             kvm_host = entry['kvm_host']
             if kvm_host != inventory_hostname:
                 continue
             if proxmox_guests_item in flash_selector:
                 destroy_guest_list.append(proxmox_guests_item)
                 continue
             #print("step 6")
             #print(kvm_host, inventory_hostname, flash_selector, proxmox_guests_item)
             for item in flash_selector:
                 if fnmatch.fnmatch(proxmox_guests_item,item):
                     destroy_guest_list.append(proxmox_guests_item)
                     break
                     

         ansible_facts['destroy_guest_list'] = destroy_guest_list


         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False
         return result
