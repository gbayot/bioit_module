import argparse
import re
import os
from pathlib import Path


class CommandParser:
    def __init__(self, version, default_install_config=None, need_parameters=True, need_pipeline_parameters=False):
        """
        :param version: script version
        :param default_install_config: if None, the -c argument isn't required
        :param need_parameters: if True, the -p argument is required
        :param need_pipeline_parameters: if True, the --pipe-params and --reference_dir argument are required.
        """
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-v", "--version", action="version", version=version)
        self.set_default_option()
        self.set_custom_option()
        if default_install_config:
            self.set_install_config_option(default_install_config)
        if need_parameters:
            self.set_parameters_option()
        if need_pipeline_parameters:
            self.set_pipeline_parameters()

    def set_default_option(self):
        """
        Set default argument.
        Should not be override.
        """
        self.parser.add_argument(
            "-o",
            "--out-prefix",
            dest="prefix",
            required=True,
            help="Prefix use to name output files (ex: output_dir/sample_1).",
            type=self._is_valid_filename
        )
        self.parser.add_argument(
            "-l",
            "--log",
            dest="logfile",
            required=False,
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
        """"
        Override this to add new argument
        """
        pass

    def set_install_config_option(self, default_install_config=None):
        if default_install_config:
            self.parser.add_argument(
                "-c",
                "--config",
                dest="config",
                required=False,
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

    def set_pipeline_parameters(self):
        self.parser.add_argument(
            "--pipe_params",
            dest="pipe_params",
            required=True,
            help="Pipeline parameters file.",
            type=self._is_valid_file
        )
        self.parser.add_argument(
            "--reference_dir",
            dest="reference_dir",
            required=True,
            help="Reference directory.",
            type=self._is_valid_dir
        )

    def parse(self):
        return self.parser.parse_args()

    @staticmethod
    def _is_valid_filename(filename):
        """
        argparse type: check if a filename has valid character
        """
        reg = re.compile(r"[^\w\s/\.@_\-+~$*=]")
        if re.search(reg, filename):
            raise argparse.ArgumentTypeError("Invalid filename '{}' contains illegal characters.".format(filename))
        return filename

    @staticmethod
    def _is_valid_file(filename):
        """
        argparse type: check if file exist
        """
        if not os.path.isfile(filename):
            raise argparse.ArgumentTypeError("Invalid filename '{}' doesn't exist.".format(filename))
        return filename

    @staticmethod
    def _is_valid_integer(num):
        if not re.match(r"^\d+$", num):
            raise argparse.ArgumentTypeError(
                "Invalid number '{}' contains illegal characters.".format(num)
            )
        return int(num)

    @staticmethod
    def _is_valid_dir(directory):
        if not Path(directory).is_dir():
            raise argparse.ArgumentTypeError("{} is not a valid directory.".format(directory))
        return directory

    @staticmethod
    def _is_valid_extension(extensions):
        def is_valid_extension(f):
            CommandParser._is_valid_file(f)
            for extension in extensions:
                if f.endswith(extension):
                    return f
            raise argparse.ArgumentTypeError("{} need to end with {}".format(f, extensions))
        return is_valid_extension

