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
#from ansible.utils.display import Display

#display = Display()


# ActionModule has a new instance per host 

class ActionModule(ActionBase):

     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         inventory_hostname = task_vars['inventory_hostname']
         hostvars = task_vars['hostvars']
         groups = task_vars['groups']
         hostvar = hostvars[inventory_hostname]

         #if 'kvm_group' in hostvar:
         #   kvm_group = hostvar['kvm_group']
         #else:
         #   display.warning('xxx: warns!')
         #   kvm_group = 'all'

         result['msg'] = "OK"
         result['changed'] = False
         result['failed'] = False
         return result
