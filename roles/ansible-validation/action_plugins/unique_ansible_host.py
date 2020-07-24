from ansible.plugins.action import ActionBase

class ActionModule(ActionBase):


     def print_fail(msg):
         print(msg)

     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         hostvars = task_vars['hostvars']
         group_all = task_vars['groups']['all']

         ansible_host_dict   = {}
         #print(group_all)

         for inventory_name in group_all:
             #print(inventory_name)
             host=hostvars[inventory_name] 
             if 'ansible_host' in host:
                 ansible_host = host['ansible_host']
                 #print(" XX " + ansible_host)
              
                 if ansible_host in ansible_host_dict:
                    #print("duplicate ansible_host attribute '"+ansible_host+"' at " + inventory_name + ": already set in "+ ansible_host_dict[ansible_host] )
                    print(inventory_name + ":  ansible_host not not unique ('"+ansible_host+"'), already set in host "+ ansible_host_dict[ansible_host] )
                    result['changed'] = False
                    result['failed'] = True
                    return result
                 else:
                    ansible_host_dict[ansible_host] = inventory_name
             else:
                 print("ansible_host not set in inventory host: " + inventory_name)
                 result['changed'] = False
                 result['failed'] = True
                 return result

         # put validation code here... you can for example use
         # all this host variables in task_vars, and for example
         # compare with task_vars['hostvars'], which contains all
         # variables of all hosts
         #
         # if something is wrong, raise an error as follows:
         # result['failed'] = True
         # result['msg'] = 'Duplicate IP found: ...'    return result
         result['changed'] = False
         result['failed'] = False 
         return result
