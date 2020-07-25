# validation of ansible variables
# Precondition: proxmox-cluster acttion was run: proxmox_cluster exists

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
     def validate(self, table, hostvar, result, hostvars):
         for attr_row in table:
             length = len(attr_row)
             mandatory = attr_row[0]
             attr_name = attr_row[1]
             attr_type = attr_row[2]
 
             if not attr_name in hostvar:
                 if mandatory:
                     result['failed'] = True
                     result['msg'] = "mandatory attribute  missing: " + attr_name
                     return result
                 else:
                     continue
             value = hostvar[attr_name]
             if attr_type == 'str' and not isinstance(value, str):
                 result['failed'] = True
                 result['msg'] = "attribute must be a string: " + attr_name
                 return result
 
             elif attr_type == 'int' and not isinstance(value, int):
                 result['failed'] = True
                 result['msg'] = "attribute must be a int: " + attr_name
                 return result

             if length <= 3:
                continue
 
             attr_subtype = attr_row[3]
 
             if attr_subtype == 'numeric':
                 if not value.isnumeric():
                     result['failed'] = True
                     result['msg'] = "string value of '"+attr_name+"' is not numeric: "+ attr_name
                     return result
             elif attr_subtype == 'set':
                 allowed_values = attr_row[4]
                 if value not in allowed_values:
                     result['failed'] = True
                     result['msg'] = "string value of '"+attr_name+"' is not one: " + ", ".join(allowed_values)
                     return result

             elif attr_subtype == 'valid_host_list':
                 array = value.split(",")
                 for name in array:
                     name = name.strip()
                     if name not in hostvars:
                        result['failed'] = True
                        result['msg'] = "host in "+attr_name+" does not exist: "+name
                     return result

         result['failed'] = False
         return result
 
 
     def run(self, tmp=None, task_vars=None):
         if task_vars is None:
            task_vars = dict()

         result = super(ActionModule, self).run(tmp, task_vars)
         result['changed'] = False

         inventory_hostname = task_vars['inventory_hostname']
         hostvars = task_vars['hostvars']
         groups = task_vars['groups']
         ansible_play_hosts_all = task_vars['ansible_play_hosts_all'] 

         hostvar = hostvars[inventory_hostname]

         for required_var in [ 'proxmox_cluster', 'proxmox_guests_group' ]:
             if required_var in hostvar:
                 continue
             result['failed'] = True
             result['msg'] = "variable '"+required_var+"' does not exist"
             return result

         proxmox_cluster = hostvar['proxmox_cluster']
         proxmox_guests_group = hostvar['proxmox_guests_group']
         if proxmox_guests_group not in groups:
             result['failed'] = True
             result['msg'] = "group defined in proxmox_guests_group does not exist: " + proxmox_guests_group
             return result

         proxmox_guests_group_list = groups[proxmox_guests_group]

        # col0 = attribute mandatory or not
        # col1 = attribute name
        # col2 = attribute type
        # cal3 = attribute subtype
        # cal4 = attribute subtype parameters

         table = [
         [ True,  'kvm_host', 'str' ],
#         [ True,  'kvm_id',   'str','numeric'],
         [ True,  'kvm_id',   'int'],
         [ True,  'disk0',    'int'],
         [ False, 'disk1',    'int'],
         [ False, 'disk2',    'int'],
         [ False, 'disk3',    'int'],
         [ True,  'cores',    'int'],
         [ True,  'arch',     'str', 'set', ['x86_64','aarch64']],
         [ True,  'os_type',  'str', 'set', ['linux', 'windows']],
         [ False, 'os_name',  'str'],
         [ False, 'os_version', 'str'],
         [ False, 'os_variant', 'str'],
         [ False, 'net0_macaddr', 'str'],
         [ False, 'net1_macaddr', 'str'],
         [ False, 'net2_macaddr', 'str'],
         [ False, 'net3_macaddr', 'str'],
         [ False, 'flash_list', 'str', 'valid_host_list'],
         [ False, 'destroy_list', 'str', 'valid_host_list' ]

         ]
         for name in proxmox_guests_group_list:
             guest_hostvar = hostvars[name]
             self.validate(table,guest_hostvar,result,hostvars)
             if result['failed']:
                 msg = result['msg']
                 msg = name + ": " + msg
                 result['msg'] = msg
                 return result

         # check if virtual machines in configuration are assigned to the same host like the real configuration (proxmox_cluster) 
         for name in proxmox_guests_group_list:
             guest_hostvar = hostvars[name]
             kvm_host = guest_hostvar['kvm_host']

             # all hosts must be in the current playbroup otherwise all the checks make limited sense

             if kvm_host not in ansible_play_hosts_all:
                 result['failed'] = True
                 result['msg'] = name + ":  The guest references a kvm_host which is not in current ansible play group: " + kvm_host
                 return result

             # Now check config vs reality

             kvm_id = guest_hostvar['kvm_id']
             if kvm_id not in proxmox_cluster:
                 # does not exist (yet)
                 continue
             kvm_host_real = proxmox_cluster[kvm_id]['kvm_host']
             if kvm_host_real != kvm_host:
                 result['failed'] = True
                 result['msg'] = name + ": kvm_host on proxmox is '"+kvm_host_real+"' but configuration specifies '"+kvm_host+"'. Please correct this"
                 return result

         return result
