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

         ansible_facts={}
         
         ansible_play_hosts_all = task_vars['ansible_play_hosts_all'] 
         inventory_hostname = task_vars['inventory_hostname']

         global_fcos_channel = task_vars['fcos_channel']
         if global_fcos_channel not in ['stable', 'testing', 'next']:
              result['msg'] = "global variable fcos_channel is set to '"+fcos_channel+"' is not one of [stable, testing,next]"
              result['changed'] = False
              result['failed'] = True
              return result

         hostvars = task_vars['hostvars']
         groups = task_vars['groups']
         
         if 'kvm_host_group' in hostvars:
            kvm_host_group = hostvars['kvm_host_group']
         else:
            kvm_host_group = 'all'

         if 'fcos_host_group' in hostvars:
            fcos_host_group = hostvars['fcos_host_group']
         else:
            fcos_host_group = 'all'

         if kvm_host_group in groups:
             kvm_host_group_list = groups[kvm_host_group]
         else:
             result['msg'] = "kvm_host_group was set to '"+kvm_host_group+"'. Not found in groups"
             result['changed'] = False
             result['failed'] = True
             return result

         if fcos_host_group in groups:
             fcos_host_group_list = groups[fcos_host_group]
         else:
             result['msg'] = "fcos_host_group was set to '"+fcos_host_group+"'. Not found in groups"
             result['changed'] = False
             result['failed'] = True
             return result

         kvm_array = []
         for other_inventory_hostname in kvm_host_group_list:
              other_host = hostvars[other_inventory_hostname]
              if 'kvm_host' in other_host and other_host['kvm_host'] == inventory_hostname:
                  kvm_array.append(other_inventory_hostname)

         ansible_facts['kvm_host_list']=kvm_array

         for other_inventory_hostname in kvm_array:
              other_host = hostvars[other_inventory_hostname]
              if not 'fcos_channel' in other_host:
                  continue
              fcos_channel = other_host['fcos_channel']
              if fcos_channel in ['stable', 'testing', 'next']:
                  continue
              result['msg'] = "fcos_channel '"+fcos_channel+"' is  not one of  [stable, testing,next]"
              result['changed'] = False
              result['failed'] = True
              return result



         # fcos is a subset of kvm_array
         fcos_array = [] 
         for other_inventory_hostname in kvm_array:
              other_host = hostvars[other_inventory_hostname]
              if 'os_name' in other_host and other_host['os_name'] == 'fcos':
                  fcos_array.append(other_inventory_hostname)

         ansible_facts['fcos_host_list']=fcos_array

         # download_list subset of fcos_host_list  or from kvm_host list, or from flash list?
         fcos_flash_array = [] 
         for other_inventory_hostname in fcos_array:
              other_host = hostvars[other_inventory_hostname]
              if 'flash' in other_host and other_host['flash'] == True:
                  fcos_flash_array.append(other_inventory_hostname)

         ansible_facts['fcos_host_flash_list']=fcos_flash_array

         # need default_chnannel and or set channel
         fcos_os_version_list = [] 
         fcos_os_version_list2 = [] 
         for other_inventory_hostname in fcos_flash_array:
              other_host = hostvars[other_inventory_hostname]
              if not 'os_version' in other_host:
                  continue
              os_version = other_host['os_version']
              if os_version in fcos_os_version_list:
                  continue
              fcos_os_version_list.append(os_version)
              if 'fcos_channel' in other_host:
                   fcos_channel = other_host['fcos_channel']
              else:
                   fcos_channel = global_fcos_channel
              my_dict = {} 
              my_dict['fcos_channel']=fcos_channel
              my_dict['os_version']=os_version
              fcos_os_version_list2.append(my_dict)

         ansible_facts['fcos_os_version_list']=fcos_os_version_list2

         result['ansible_facts'] = ansible_facts
         result['changed'] = False
         result['failed'] = False

         return result
