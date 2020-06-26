from netaddr import IPAddress

class FilterModule(object):
    '''
    custom jinja2 filters for working with collections
    '''

    def filters(self):
        return {
            'cidr_to_netmask': cidr_to_netmask,
            'netmask_to_cidr': netmask_to_cidr
        }

def cidr_to_netmask(collection):
    len = collection
    result = '.'.join([str((0xffffffff << (32 - len) >> i) & 0xff)
                    for i in [24, 16, 8, 0]]) 
    return result

def netmask_to_cidr(collection):
    return IPAddress(collection).netmask_bits()
