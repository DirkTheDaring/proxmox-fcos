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
         host = hostvars[inventory_hostname]
         failed=False
         missing_attr_list = []
         for attr in [ 'kvm_host', 'kvm_id', 'flash', 'os_name', 'disk0' ]:
             if attr in host:
                 continue
             failed=True
             missing_attr_list= missing_attr_list + [ attr ]

         if failed:
            result['changed'] = False
            result['failed'] = failed
            result['msg'] = "mandatory attribute(s) missing: "+ " ".join(missing_attr_list)
            return result


         flash = host['flash']
         if not isinstance(flash, bool):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "flash is not a bool"
            return result

         os_name = host['os_name']
         if not isinstance(os_name, str):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "os_name is not a string"
            return result


         kvm_host = host['kvm_host']
         if kvm_host not in hostvars:
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "kvm_host is not in inventory: " + kvm_host
            return result

         kvm_id = host['kvm_id']
         if not isinstance(kvm_id, str):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "kvm_id is not a string"
            return result

         if not kvm_id.isnumeric():
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "kvm_id is not numeric: "+kvm_id
            return result

         flash = host['flash']
         if not isinstance(flash, bool):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "flash is not a bool"
            return result

         os_name = host['os_name']
         if not isinstance(os_name, str):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "os_name is not a string"
            return result

         disk0 = host['disk0']
         if not isinstance(disk0, int):
            result['changed'] = False
            result['failed'] = True
            result['msg'] = "disk0 is not a integer"
            return result

         # optional string attr
         for attr in [ 'os_version', 'os_variant' ]:
             if not attr in host:
                 continue
             value = host[attr]
             if isinstance(value, str):
                 continue
             result['changed'] = False
             result['failed'] = True
             result['msg'] = value + " is not a string"
             return result

         # optional int attr
         for attr in [ 'disk1', 'disk2', 'disk3' ]:
             if not attr in host:
                 continue
             value = host[attr]
             if isinstance(value, int):
                 continue
             result['changed'] = False
             result['failed'] = True
             result['msg'] = value + " is not a integer"
             return result

         ansible_play_hosts_all = task_vars['ansible_play_hosts_all'] 
         other_hosts_in_play = ansible_play_hosts_all.copy() 
         other_hosts_in_play.remove(inventory_hostname)
         for hostname in other_hosts_in_play:
             other_host=hostvars[hostname]
             if other_host['kvm_id'] == host['kvm_id']:
                result['changed'] = False
                result['failed'] = True
                result['msg'] = "duplicate kvm_id in host: "+hostname
                return result

         #print(other_hosts_in_play) 
         
         result['changed'] = False
         result['failed'] = failed
         return result
