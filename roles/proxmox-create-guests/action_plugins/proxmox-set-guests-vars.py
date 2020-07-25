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

# ActionModule has a new instance per host 

class ActionModule(ActionBase):
     def create_list_from_str(self, str_list, allowed_hosts):
         array=[]
         str_list = str_list.strip()
         if str_list == "":
             return array
         str_array = str_list.split(',')
         result = []
         for item in str_array:
             item = item.strip()
             if item in allowed_hosts:
                result.append(item)
         return result

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
             if 'kvm_host' not in item:
                 continue
             kvm_host = item['kvm_host']
             if kvm_host != inventory_hostname:
                 continue
             proxmox_guests_list.append(proxmox_guests_item)

         # proxmox_guest_list is now per host
         ansible_facts['proxmox_guests_list'] = proxmox_guests_list
         # checking was done in validation, so no fail here
         for item in ['flash', 'destroy' ]: 
             if item in task_vars:
                 str_list = task_vars[item]
                 ansible_facts[ item + "_list"] = self.create_list_from_str(str_list,proxmox_guests_list)

         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False
         return result
