#import netaddr
from netaddr import IPAddress
import collections

class FilterModule(object):
    '''
    custom jinja2 filters for working with collections
    '''
    def filters(self):
        return {
            'cidr_to_netmask': cidr_to_netmask,
            'netmask_to_cidr': netmask_to_cidr,
            'duplicate':       duplicate
        }

def duplicate(a):
    if isinstance(a, collections.Hashable):
        c = set(a)
    else:
        s = {}
        c = []
        for x in a:
            if x not in s:
                s[x] = 1
            else:
                if s[x] == 1:
                    c.append(x)
                s[x] += 1
    return c

def cidr_to_netmask(collection):
    len = collection
    result = '.'.join([str((0xffffffff << (32 - len) >> i) & 0xff)
                    for i in [24, 16, 8, 0]]) 
    return result

def netmask_to_cidr(collection):
    return netaddr.IPAddress(collection).netmask_bits()
