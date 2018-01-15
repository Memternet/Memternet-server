import json
import os

__config = {}


def config(name, default=None):
    global __config
    if name in __config:
        return __config[name]

    os.makedirs('configs', exist_ok=True)
    filename = 'configs/{}_config.json'.format(name)

    try:
        with open(filename, 'r') as file:
            __config[name] = json.loads(''.join(file.readlines()))
    except IOError as e:
        if default is not None:
            try:
                with open(filename, 'w') as file:
                    file.write(json.dumps(default, indent=2))
                    __config[name] = default
            except IOError as e:
                print('Can\'t save default config file {}!'.format(filename))
                raise e
        else:
            print('Can\'t load config file {}!'.format(filename))
            raise e

    return __config[name]
