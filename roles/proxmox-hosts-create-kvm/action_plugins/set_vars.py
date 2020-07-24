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

     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         inventory_hostname = task_vars['inventory_hostname']
         hostvars = task_vars['hostvars']
         groups = task_vars['groups']

         ansible_facts={}
         host = hostvars[inventory_hostname]

         if 'kvm_host_group' in hostvars:
            kvm_host_group = hostvars['kvm_host_group']
            if not kvm_host_group in groups:
                result['changed'] = False
                result['failed'] = True
                result['msg'] = "kvm_host_group '"+kvm_host_group+"' does not exist in groups"
                return result
         else:
            kvm_host_group = 'all'

         kvm_host_array = groups[kvm_host_group]

         kvm_host_list = []
         for kvm_host_item in kvm_host_array:
             item = hostvars[kvm_host_item]
             if 'kvm_host' not in item:
                 continue
             kvm_host = item['kvm_host']
             if kvm_host != inventory_hostname:
                 continue
             kvm_host_list.append(kvm_host_item)

         ansible_facts['kvm_host_list'] = kvm_host_list
 
         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False
         return result
