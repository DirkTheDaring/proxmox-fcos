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
         hostvars = task_vars['hostvars']
         inventory_hostname = task_vars['inventory_hostname']
         host = hostvars[inventory_hostname]
         missing_attr_list = []
         failed = False

         for attr in [ 'flash', 'os_name', 'os_version' ]:
             if attr in host:
                 continue
             failed=True
             missing_attr_list = missing_attr_list + [ attr ]

         if failed:
            result['changed'] = False
            result['failed'] = failed
            result['msg'] = "mandatory attribute(s) missing: "+ " ".join(missing_attr_list)
            return result

         flash_array=[]
         if 'flash_list' in task_vars:
             flash_list = task_vars['flash_list']
             flash_array = flash_list.split(',')
             for item in flash_array:
                 item = item.strip()
                 if item == "":
                     continue
                 if item in hostvars:
                     continue
                 result['changed'] = False
                 result['failed'] = True
                 result['msg'] = "host provided in flash_list does not exist in inventory: " + item
                 return result

         ansible_facts={}
         inventory_hostname = task_vars['inventory_hostname']
         if inventory_hostname in flash_array:
             ansible_facts['flash'] = True

         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = failed
         return result
