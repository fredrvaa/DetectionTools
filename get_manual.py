import os
import shutil

for d in [x for x in os.listdir('datasets') if not x.startswith('C') and x != 'D0' and x != 'manual']:
    for e,i in enumerate([y for y in os.listdir(f'datasets/{d}') if not y.endswith('.json')]):
        if not e%20:
            shutil.copy(os.path.join('datasets',d,i), os.path.join('datasets','manual'))