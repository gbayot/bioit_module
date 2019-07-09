import os
import sys
import json
import logging
import re
import abc
import traceback
from configparser import ConfigParser
from optparse import OptionParser


class BaseModule(abc.ABC):
    def __init__(self, name, version, suffix, install_config=None, no_parameters=False, usage=None):
        self.name = name
        self.version = version
        self._install_config_file = install_config
        self.suffix = suffix
        self._no_parameters = no_parameters
        self._set_usage_str(usage)
        self.parser = None
        self.output_dir = None
        self.prefix = None
        self.job_id = None
        self.run_id = None
        self.install_config = None
        self.parameters = None
        self._param_file = None
        self._json_log = None

    def _set_usage_str(self, usage=None):
        if usage is not None:
            self._usage_str = usage
        else:
            self._usage_str = "Usage: %prog [options] -o prefix"
            if not self._no_parameters:
                self._usage_str += " -p parameters.ini"
            self._usage_str += " input"
        return

    def init_std_options(self):
        self.parser = OptionParser(usage=self._usage_str)
        self.parser.version = self.version
        self.parser.add_option("-o", "--out-prefix", dest="prefix", metavar="Prefix",
                               help="Prefix use to name output files (ex: output_dir/sample_1). "
                                    "If it doesn't exist, output directory will be created.")
        if not self._no_parameters:
            self.parser.add_option("-p", "--params", dest="param", help="Module parameters file.",
                                   metavar="FILE")
        if self._install_config_file is not None:
            self.parser.add_option("-c", "--config", dest="config",
                                   default=self._install_config_file, metavar="FILE",
                                   help="Use a specific install configuration file.")
        self.parser.add_option("-j", "--job", dest="jobid", default="0",
                               help="Unique job identifier", metavar="STRING")
        self.parser.add_option("-r", "--run", dest="runid", default="0",
                               help="Unique run identifier", metavar="STRING")
        self.parser.add_option("-l", "--log", dest="logfile",
                               help="Alignment execution log file, STDOUT if not defined.",
                               metavar="STRING")
        self.parser.add_option("-d", "--debug", dest="debug", default=False, action="store_true",
                               metavar="BOOLEAN", help="Set log level to debug.")
        self.parser.add_option("-v", "--version", dest="version", help="Print version and exit",
                               action="store_true", default=False, metavar="INT")

    def init_custom_options(self):
        return 0

    def check_std_options(self, options):
        # if version is required print and exit
        if options.version:
            print(os.path.basename(sys.argv[0]), "version", self.version)
            exit(0)

        # init log system
        log_level = logging.INFO
        if options.debug:
            log_level = logging.DEBUG
        format_str = '[' + str(self.name) + '][%(levelname)s]:%(asctime)s:%(message)s'
        format_date = '%m/%d/%Y %H:%M:%S'
        if options.logfile:
            logging.basicConfig(format=format_str, filename=options.logfile, level=log_level, datefmt=format_date)
        else:
            logging.basicConfig(format=format_str, level=log_level, datefmt=format_date)

        # ---------- After this step logging system is initialized ---------- #

        logging.debug("Check input arguments.")

        # set run and job
        self.run_id = str(options.runid)
        self.job_id = str(options.jobid)

        # check prefix options and set output base
        reg = re.compile(r'[^\w\s/\.@_\-+~$*=]')
        if options.prefix is None:
            self.parser.error("Mandatory option -o prefix is missing")
        elif re.search(reg, options.prefix):
            self.parser.error("Invalid mandatory option -o prefix '%s' contains illegal characters." %
                              options.prefix)

        output_prefix = os.path.split(options.prefix)
        self.output_dir = os.path.sep.join(output_prefix[:-1])
        if self.output_dir == "":
            self.output_dir = "."

        logging.debug("Output directory name: %s", self.output_dir)
        self.prefix = output_prefix[-1]
        logging.debug("Output file prefix: %s", self.prefix)
        self._json_log = os.path.join(self.output_dir, self.prefix + "_mod_log.json")
        logging.debug("Execution summary json file: %s", self._json_log)

        # set config file
        if self._install_config_file is not None:
            self._install_config_file = options.config

        # set parameter file
        if not self._no_parameters:
            self._param_file = options.param

    def check_custom_options(self, options):
        return 0

    def check_args(self, args):
        return 0

    def init_output(self):
        # Initialized output files names and create directory if needed
        if not os.path.isdir(self.output_dir):
            logging.info("Create non-existing output directories %s", self.output_dir)
            os.makedirs(self.output_dir)
        if os.path.isfile(self._json_log):
            logging.warning("Execution summary json file: "
                            "%s exist and will be replaced", self._json_log)

    def load_install_config(self):
        if self._install_config_file is not None:
            try:
                if not os.path.isfile(self._install_config_file):
                    raise FileNotFoundError("%s: No such file or directory" %
                                            self._install_config_file)
                logging.debug("Loading install configuration file: %s",
                              self._install_config_file)
                self.install_config = ConfigParser()
                self.install_config.read(self._install_config_file)
                # check config
                logging.debug("Check install configuration file: %s",
                              self._install_config_file)
                return self.check_install_config(self.install_config)
            except Exception as e:
                return self.end_process(
                    error="Unexpected error while loading install configuration file "
                          "%s: %s\n%s" %
                          (self._install_config_file,  str(e), traceback.format_exc()),
                    error_code=10)
        else:
            logging.debug("Module without specific installation configuration.")
        return 0

    def check_install_config(self, install_config):
        return 0

    def load_parameter_file(self):
        # load parameter file (only if needed)
        if not self._no_parameters:
            try:
                logging.debug("Loading parameter file: %s", self._param_file)
                self.parameters = ConfigParser()
                self.parameters.read(self._param_file)
                # check config
                logging.debug("Check parameter file: %s", self._param_file)
                self.check_parameters(self.parameters)
            except Exception as e:
                return self.end_process(
                    error="Unexpected error while loading parameters file %s: %s\n%s" %
                          (self._param_file,  str(e), traceback.format_exc()),
                    error_code=11)
        else:
            logging.debug("Module without parameters.")
        return 0

    def check_parameters(self, parameters):
        pass

    def run(self, **kwargs):
        ec = 0
        # Initialisation of standard bioit module options.
        self.init_std_options()
        # Initialisation of custom bioit module options.
        ec = self.init_custom_options()
        # Read options and arguments.
        (options, args) = self.parser.parse_args()
        # Verifications of standard bioit module options.
        self.check_std_options(options)
        # Verifications of custom bioit module options.
        if ec == 0:
            ec = self.check_custom_options(options)
        # Check  input arguments.
        if ec == 0:
            ec = self.check_args(args)
        # Initialized output files names and create directory if needed
        self.init_output()
        # load install config
        if ec == 0:
            ec = self.load_install_config()
        # load parameter file
        if ec == 0:
            ec = self.load_parameter_file()
        # start module process
        if ec == 0:
            try:
                output_files_list = self.start_process(**kwargs)
                ec = self.end_process(error_code=0, files=output_files_list)
            except Exception as e:
                ec = self.end_process(error="Unexpected error: %s:\n%s" %
                                            (str(e), traceback.format_exc()), error_code=911)
        return ec

    def end_process(self, error_code=0, error="", files=[]):
        # if process end with error, print info in log system
        if error_code != 0 and error is not None:
            logging.error(error)
        # Print analysis execution summary in JSON format.
        with open(self._json_log, "w") as fp:
            json.dump({
                "meta": {
                    "status": error_code,
                    "jobid": self.job_id,
                    "runid": self.run_id,
                    "error": error,
                    "tool": self.name,
                    "version": self.version
                },
                "files": files
            }, fp)
        return error_code

    @abc.abstractmethod
    def start_process(self, **kwargs):
        raise NotImplementedError

