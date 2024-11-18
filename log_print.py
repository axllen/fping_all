import time
from termcolor import cprint


def log_print(level, module_name, log_message):
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')
    if level == 'info':
        cprint('[%s]%s:%s' % (time_str, module_name, log_message))
    elif level == 'success':
        cprint('[%s]%s:%s' % (time_str, module_name, log_message), 'green', attrs=['bold'])
    elif level == 'error':
        cprint('[%s]%s:%s' % (time_str, module_name, log_message), 'red')
    else:
        cprint('[%s]%s:%s' % (time_str, module_name, log_message))
