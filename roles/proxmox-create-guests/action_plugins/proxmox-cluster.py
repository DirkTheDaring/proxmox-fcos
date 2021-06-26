from ansible.plugins.action import ActionBase
from ansible.utils.unsafe_proxy import AnsibleUnsafeText

# ActionModule will be instiated per host. therefore the "global variable" will be created on a per host basis

class ActionModule(ActionBase):

     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         result['changed'] = False
         inventory_hostname = task_vars['inventory_hostname']
         ansible_play_hosts_all = task_vars['ansible_play_hosts_all']
         hostvars = task_vars['hostvars']
         ansible_facts = {}
 
         proxmox_cluster = {}
         for play_host_name in ansible_play_hosts_all:
             play_host = hostvars[play_host_name]
             proxmox_host_guests = play_host['proxmox_host_guests']
             for guest_id in proxmox_host_guests:
                 if guest_id in proxmox_cluster:
                     result['msg'] = "duplicate guest id in cluster: " + guest_id
                     result['failed'] = True
                     return result
                 src_dict = proxmox_host_guests[guest_id]
                 target_dict=src_dict.copy()
                 target_dict['kvm_host'] = play_host_name
                 proxmox_cluster[guest_id] = target_dict
#
         ansible_facts['proxmox_cluster'] = proxmox_cluster

         result['ansible_facts'] = ansible_facts
         result['failed'] = False
         return result
