import os
import logging
from configparser import ConfigParser, NoOptionError
from bioit_module import build_logger, exit_code
from schematics.exceptions import ValidationError


class BioitLauncher:
    def __init__(self, command_parser):
        self.args = command_parser.parse()
        self.logger = self._build_logger(self.args.logfile, self.args.debug)
        self.validate_args()
        self.output_dir = os.path.sep.join(os.path.split(self.args.prefix)[:-1])
        try:
            self.logger.debug("Read install config")
            self.install_config = self.read_install_config()
            self.logger.debug("Read parameters")
            self.params = self.read_parameters()
        except NoOptionError as e:
            self.logger.exception('')
            exit(exit_code.NoOptionError)
        except ValidationError as e:
            self.logger.exception('')
            exit(exit_code.ValidationError)
        except Exception as e:
            self.logger.exception('')
            exit(exit_code.UnknownError)
        self.validate_install_config()
        self.validate_params()

    def launch(self):
        pass

    def read_install_config(self):
        return None

    def read_parameters(self):
        return None

    def validate_args(self):
        self.logger.debug("Validate args")
        try:
            self._validate_args()
        except Exception as e:
            self.logger.exception('')
            exit(exit_code.ValidationArgsError)

    def validate_install_config(self):
        self.logger.debug("Validate install config")
        try:
            self._validate_install_config()
        except Exception as e:
            self.logger.exception('')
            exit(exit_code.ValidationInstallConfigError)

    def validate_params(self):
        self.logger.debug("Validate params")
        try:
            self._validate_params()
        except Exception as e:
            self.logger.exception('')
            exit(exit_code.ValidationParamsError)

    def _build_logger(self, logfile, debug=False):
        log_level = logging.INFO
        if debug:
            log_level = logging.DEBUG
        return build_logger(logfile, level=log_level)

    def _validate_args(self):
        pass

    def _validate_install_config(self):
        pass

    def _validate_params(self):
        pass

    def _read_config_file(self, filename):
        config_parser = ConfigParser()
        config_parser.read(filename)
        return config_parser
