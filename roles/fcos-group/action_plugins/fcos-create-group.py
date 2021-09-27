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

     def parse_flash(self, task_vars):
         if 'flash' not in task_vars:
             return []
         flash = task_vars['flash']
         flash_selector = [ x.strip() for x in flash.split(',') ]
         return flash_selector

     def match(self, group, flash_selectors):
         result = []
         if len(flash_selectors) == 0: 
             return []
         for item in flash_selectors:
             for host in group:
                 if fnmatch.fnmatch(host,item) and host not in result:
                     result.append(host)
         return result


     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)

         #inventory_hostname = task_vars['inventory_hostname']
         #hostvars = task_vars['hostvars']
         groups = task_vars['groups']

         flash_selectors = self.parse_flash(task_vars)
         fedora_coreos_machines = groups['fedora_coreos_machines']
         dynamic_fedora_coreos_machines_result = self.match(fedora_coreos_machines, flash_selectors)

         #groups['dynamic_fedora_coreos_machines'] = dynamic_fedora_coreos_machines
         #print(groups)

         ansible_facts={}
         ansible_facts['dynamic_fedora_coreos_machines_result'] = dynamic_fedora_coreos_machines_result

         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False
         return result
