import argparse
import re
import os


class CommandParser:
    def __init__(self, version, default_install_config=None, need_parameters=True):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", "--version", action="version", version=version)
        self.set_default_option()
        self.set_custom_option()
        if default_install_config:
            self.set_install_config_option(default_install_config)
        if need_parameters:
            self.set_parameters_option()

    def set_default_option(self):
        self.parser.add_argument(
            "-o",
            "--out-prefix",
            dest="prefix",
            required=True,
            help="Prefix use to name output files (ex: output_dir/sample_1). "
            "If it doesn't exist, output directory will be created.",
            type=self._is_valid_filename
        )
        self.parser.add_argument(
            "-l",
            "--log",
            dest="logfile",
            required=True,
            help="Log file, STDOUT if not defined.",
            type=self._is_valid_filename
        )
        self.parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            default=False,
            action="store_true",
            help="Set log level to debug.",
        )

    def set_custom_option(self):
        pass

    def set_install_config_option(self, default_install_config=None):
        if default_install_config:
            self.parser.add_argument(
                "-c",
                "--config",
                dest="config",
                required=True,
                default=default_install_config,
                help="Use a specific install configuration file.",
                type=self._is_valid_file
            )

    def set_parameters_option(self):
        self.parser.add_argument(
            "-p",
            "--params",
            dest="params",
            required=True,
            help="Module parameters file.",
            type=self._is_valid_file
        )

    def parse(self):
        return self.parser.parse_args()

    @staticmethod
    def _is_valid_filename(filename):
        reg = re.compile(r"[^\w\s/\.@_\-+~$*=]")
        if re.search(reg, filename):
            raise argparse.ArgumentTypeError("Invalid filename '{}' contains illegal characters.".format(filename))
        return filename

    @staticmethod
    def _is_valid_file(filename):
        if not os.path.isfile(filename):
            raise argparse.ArgumentTypeError("Invalid filename '{}' doesn't exist.".format(filename))
        return filename
