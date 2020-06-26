def filter_child_dictionary(dictionary, key, value):
  newdict = {}
  for child_name in dictionary:
    child = dictionary[child_name]
    if not key in child:
      continue
    if str(child[key]) != str(value):
      continue
    newdict[child_name] = child
  return newdict

def filter_child_attr(dictionary, key, available):
  newdict = {}
  for child_name in dictionary:
    child = dictionary[child_name]
    keyfound = key in child
    if keyfound == available:
      newdict[child_name] = child
  return newdict

def filter_child_attr_exists(dictionary, key):
  return filter_child_attr(dictionary, key, True)

def filter_child_attr_exists_not(dictionary, key):
  return filter_child_attr(dictionary, key, False)



class FilterModule(object):
  def filters(self):
    return {
      'filter_child_dictionary': filter_child_dictionary,
      'filter_child_attr_exists':     filter_child_attr_exists,
      'filter_child_attr_exists_not': filter_child_attr_exists_not
     }
