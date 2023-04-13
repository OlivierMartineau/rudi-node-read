from configparser import ConfigParser
from os import environ
from os.path import exists

from utils.err import IniMissingValueException, IniUnexpectedValueException, MissingEnvironmentVariableException
from utils.log import log_d

ENVIRONMENT_CONF_PATH = 'RUDI_TOOLS_PATH'


class IniReader:
    _environment_var = None

    def __init__(self, file_path):
        if not exists(file_path):
            raise FileNotFoundError(f"This configuration file was not found: '{file_path}'")
        self.config = ConfigParser()
        self.config.read(file_path)

    def get(self, section: str, param: str = None, is_mandatory_msg: str = None, accepted_values: list = None):
        if param is None:
            return self.config[section]
        else:
            try:
                param_val = self.config[section][param]
            except KeyError:
                param_val = None
            if is_mandatory_msg and param_val is None:
                raise IniMissingValueException(section, param, is_mandatory_msg)
            if accepted_values and param_val not in accepted_values:
                raise IniUnexpectedValueException(
                    section, param, f"Value expected: {'|'.join(accepted_values)}. Got: '{param_val}'")
            return param_val

    @staticmethod
    def get_environment_var(var_name: str = ENVIRONMENT_CONF_PATH, var_use: str = ''):
        if not IniReader._environment_var:
            try:
                environment_path = environ[var_name]
            except KeyError:
                raise MissingEnvironmentVariableException(var_name, var_use)
            log_d('get_environment_var', 'environment_path', environment_path)
            IniReader._environment_var = IniReader(environment_path)
        return IniReader._environment_var


if __name__ == '__main__':
    local_conf_reader = IniReader.get_environment_var(
        ENVIRONMENT_CONF_PATH, 'to define the path for the INI file that stores the connectors URL')
    log_d('Environment', 'Local conf', f"{local_conf_reader.config.sections()}")
