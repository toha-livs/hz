import os

from falcon_core import management

os.environ.setdefault('FALCON_CORE_SETTINGS_MODULE', 'gusto_api.settings')

if __name__ == '__main__':
    management.execute_from_command_line()
