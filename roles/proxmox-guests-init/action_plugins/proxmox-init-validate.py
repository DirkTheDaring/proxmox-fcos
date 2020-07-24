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

# Internal variable, which can be used to give warnings or else back
# msg           A string with a generic message relayed to the user.
# warnings     This key contains a list of strings that will be presented to the user.

# See https://docs.ansible.com/ansible/latest/reference_appendices/common_return_values.html#id16


#from ansible.utils.display import Display

#display = Display()


# ActionModule has a new instance per host 

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
           task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        result['changed'] = False

        inventory_hostname = task_vars['inventory_hostname']
        hostvars = task_vars['hostvars']
        groups = task_vars['groups']
        hostvar = hostvars[inventory_hostname]
        if 'proxmox_hosts_group' in hostvar:
            proxmox_hosts_group = hostvar['proxmox_hosts_group']
            if proxmox_hosts_group not in groups:
                result['failed'] = True
                result['msg'] = "proxmox_hosts_group contains non-existing group '" + proxmox_hosts_group + "'"
                return result
        else:
            #display.warning("proxmox_hosts_group not set. Falling back to group 'all'")
            result['warnings']=[ "proxmox_hosts_group not set. Falling back to group 'all'" ]
            proxmox_hosts_group = 'all'

        
        # col0 = attribute mandatory or not
        # col1 = attribute name
        # col2 = attribute type
        # cal3 = attribute subtype
        # cal4 = attribute subtype parameters

        table = [
        [ True,  'kvm_host', 'str' ],
        [ True,  'kvm_id',   'str','numeric'],
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
        [ False, 'destroy', 'bool'],
        [ False, 'net0_macaddr', 'str'],
        [ False, 'net1_macaddr', 'str'],
        [ False, 'net2_macaddr', 'str'],
        [ False, 'net3_macaddr', 'str']
        ]

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

            elif attr_type == 'bool' and not isinstance(value, bool):
                result['failed'] = True
                result['msg'] = "attribute must be a bool: " + attr_name
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

#         flash = host['flash']
#         if not isinstance(flash, bool):
#            result['failed'] = True
#            result['msg'] = "flash is not a bool"
#            return result

        kvm_host = hostvar['kvm_host']
        if not kvm_host in hostvars:
            result['failed'] = True
            result['msg'] = "kvm_host of refers to non existing host: "+kvm_host
            return result

        # every host needs to have a unique kvm_id, no duplicates!
        ansible_play_hosts_all = task_vars['ansible_play_hosts_all'] 
        other_hosts_in_play = ansible_play_hosts_all.copy() 
        other_hosts_in_play.remove(inventory_hostname)
        for hostname in other_hosts_in_play:
            other_host=hostvars[hostname]
            if other_host['kvm_id'] == hostvar['kvm_id']:
               result['failed'] = True
               result['msg'] = "duplicate kvm_id in host: "+hostname
               return result

        result['failed'] = False
        return result
