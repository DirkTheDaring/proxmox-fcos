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
         result['changed'] = False

         ansible_facts={}
         
         ansible_play_hosts_all = task_vars['ansible_play_hosts_all'] 
         groups = task_vars['groups']
         hostvars = task_vars['hostvars']
         inventory_hostname = task_vars['inventory_hostname']
         hostvar = hostvars[inventory_hostname]
 
         if 'fcos_channels' in task_vars:
             global_fcos_channel_list = task_vars['fcos_channels']
         else:
             result['msg'] = "fcos_channels global variable not set - required"
             result['failed'] = True
             return result
 
         if 'fcos_channel' in task_vars:
             global_fcos_channel = task_vars['fcos_channel']
         else:
             result['msg'] = "fcos_channel global variable not set - required"
             result['failed'] = True
             return result

         if global_fcos_channel not in global_fcos_channel_list:
              result['msg'] = "global variable fcos_channel is set to '"+fcos_channel+"' is not one of " + ",".join(global_fcos_channel_list)
              result['failed'] = True
              return result

         if 'proxmox_guests_list' in task_vars:
             proxmox_guests_list = task_vars['proxmox_guests_list']
         else:
             result['msg'] = "mandatory variable not found: proxmox_guest_list"
             result['failed'] = True
             return result

         # validated in other module
         proxmox_guests_group = hostvar['proxmox_guests_group']
         proxmox_guests = groups[proxmox_guests_group]

         collect_os_version = {}
         for proxmox_guest_name in proxmox_guests:
             proxmox_guest = hostvars[proxmox_guest_name]
#             if 'kvm_host' in proxmox_guest and proxmox_guest['kvm_host'] == inventory_hostname and 'os_name' in proxmox_guest and  proxmox_guest['os_name'] == 'fcos':

             if 'kvm_host' in proxmox_guest and 'os_name' in proxmox_guest and proxmox_guest['os_name'] == 'fcos':
                 #print("Found: " + proxmox_guest_name)

                 if 'fcos_channel' in proxmox_guest:
                     channel=proxmox_guest['fcos_channel']
                     if channel not in global_fcos_channel_list:
                         result['msg'] = proxmox_guest_name + ": fcos_channel '"+fcos_channel+"' value can be one of:  " + " ".join(global_fcos_channel_list)
                         result['failed'] = True
                         return result
                 else:
                     channel=global_fcos_channel

                 if 'os_version' in proxmox_guest:
                     #print("Found3: " + proxmox_guest_name)
                     os_version = proxmox_guest['os_version']
                     label = channel + "_" + os_version
                     if label not in collect_os_version:
                         collect_os_version[label]={'channel': channel, 'os_version': os_version }

         #print(collect_os_version)

         # now create fcos_os_version_list
         fcos_os_version_list = []
         for key,value in collect_os_version.items():
             fcos_os_version_list.append(value)
         ansible_facts['fcos_os_version_list']=fcos_os_version_list
         result['ansible_facts'] = ansible_facts
          
         result['failed'] = False
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
              result['msg'] = "fcos_channel '"+fcos_channel+"' value can be 'stable' or 'testing' or 'next'"
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
         result['failed'] = False

         return result
