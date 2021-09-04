import sys
import os
import traceback
from typing import List
from importlib import util

from ConfigValidator.CustomErrors.BaseError import BaseError
from ConfigValidator.CLIRegister.CLIRegister import CLIRegister
from ConfigValidator.Config.Validation.ConfigValidator import ConfigValidator
from ConfigValidator.CustomErrors.ConfigErrors import ConfigInvalidClassNameError
from ExperimentOrchestrator.Experiment.ExperimentController import ExperimentController

def is_no_argument_given(args: List[str]): return (len(args) == 1)
def is_config_file_given(args: List[str]): return (args[1][-3:] == '.py')
def load_and_get_config_file_as_module(args: List[str]):
    module_name = args[1].split('/')[-1].replace('.py', '')
    sys.path.append(os.path.dirname(os.path.realpath(args[1]))) # Add experiment folder to path to support imports.
    spec = util.spec_from_file_location(module_name, args[1]) 
    config_file = util.module_from_spec(spec)
    spec.loader.exec_module(config_file)
    return config_file

if __name__ == "__main__":
    try: 
        if is_no_argument_given(sys.argv):
            sys.argv.append('help')
            CLIRegister.parse_command(sys.argv)
        elif is_config_file_given(sys.argv):                                # If the first arugments ends with .py -> a config file is entered
            config_file = load_and_get_config_file_as_module(sys.argv)

            if hasattr(config_file, 'RobotRunnerConfig'):
                config = config_file.RobotRunnerConfig()                    # Instantiate config from injected file
                ConfigValidator.validate_config(config)                     # Validate config as a valid RobotRunnerConfig
                ExperimentController(config).do_experiment()                # Instantiate controller with config and start experiment
            else:
                raise ConfigInvalidClassNameError
        else:                                                               # Else, a utility command is entered
            CLIRegister.parse_command(sys.argv)
    except BaseError as e:                                                  # All custom errors are displayed in custom format
        print(f"\n{e}")
    except:                                                                 # All non-covered errors are displayed normally
        traceback.print_exc()