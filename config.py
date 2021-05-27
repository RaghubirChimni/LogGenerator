RESOURCE_TYPES = {
    'physical': 'physical',
    'human': 'human'
}

DAYS = {
    0: 'Mon',
    1: 'Tue',
    2: 'Wed',
    3: 'Thu',
    4: 'Fri',
    5: 'Sat',
    6: 'Sun'
}

PRIORITY_TYPES = {
    'low': 'low',
    'normal': 'normal',
    'high': 'high'
}

PRIORITY_VALUES = {
    'low': 0,
    'normal': 1,
    'high': 2
}

GATEWAY_TYPES = {
    'merge': 'merge',
    'choice': 'choice',
    'parallel': 'parallel',
    'rule': 'rule'
}

MERGE_OUTPUT = 'out'

DATA_TYPES = {
    'form': 'form'
}

#example = 'support'
example = 'moonlight/model1'
dot_example = 'moonlight.model1'
#example = 'moonlight/model2'
#dot_example = 'moonlight.model2'
#example = 'moonlight/XXX'
#dot_example = 'moonlight.XXX'

DEFAULT_PATHS = {
    'activities': 'input/'+example+'/activities.xml',
    'data':  'input/'+example+'/data.xml',
    'models': 'input/'+example+'/models.xml',
    'resources': 'input/'+example+'/resources.xml',
    'log': 'output/',
    'rules_function': 'input.'+dot_example+'.rules',
    'data_function': 'input.'+dot_example+'.data'
}

FILE_ROOT = {
    'activities': 'Activity',
    'data':  'DataObject',
    'models': 'Model',
    'resources': 'Resource'
}

SUPPORTED_FORMATS = {
    'json': 'json'
}