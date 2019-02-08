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
        self.__NAME__ = name
        self.__VERSION__ = version
        self.__install_config_file__ = install_config
        self.__suffix__ = suffix
        self.__no_parameters__ = no_parameters
        self.__set_usage_str__(usage)
        self.__parser__ = None
        self.__outdir__ = None
        self.__prefix__ = None
        self.__job__ = None
        self.__run__ = None
        self.__install_config__ = None
        self.__parameters__ = None
        self.__param_file__ = None
        self.__json_log__ = None

    def __set_usage_str__(self, usage=None):
        if usage is not None:
            self.__usage_str__ = usage
        else:
            self.__usage_str__ = "Usage: %prog [options] -o prefix"
            if not self.__no_parameters__:
                self.__usage_str__ += " -p parameters.ini"
            self.__usage_str__ += " input"
        return

    @property
    def parser(self):
        return self.__parser__

    @property
    def config(self):
        return self.__install_config__

    @property
    def parameters(self):
        return self.__parameters__

    @property
    def output_dir(self):
        return self.__outdir__

    @property
    def suffix(self):
        return self.__suffix__

    @property
    def prefix(self):
        return self.__prefix__

    @property
    def name(self):
        return self.__NAME__

    @property
    def version(self):
        return self.__VERSION__

    def run(self, **kwargs):
        # Initialisation of standard bioit module options.
        self.init_std_options(inst_config=self.__install_config_file__, usage_str=self.__usage_str__)
        # Initialisation of custom bioit module options.
        self.init_custom_options()
        # Read options and arguments.
        (options, args) = self.__parser__.parse_args()
        # Verifications of standard bioit module options.
        self.check_std_options(options)
        # Verifications of custom bioit module options.
        self.check_custom_options(options)
        # Check  input arguments.
        self.check_args(args)

        # ---------- After this step logging system is initialized ---------- #

        # Initialized output files names and create directory if needed
        logging.debug("Check input arguments.")
        self.__outdir__ = "/".join(options.prefix.split("/")[:-1])
        if self.__outdir__ == "":
            self.__outdir__ = "."
        logging.debug("Output directory name: %s", self.__outdir__)
        self.__prefix__ = options.prefix.split("/")[-1]
        logging.debug("Output file prefix: %s", self.__prefix__)
        self.__json_log__ = os.path.join(self.__outdir__, self.__prefix__ + "_mod_log.json")
        logging.debug("Execution summary json file: %s", self.__json_log__)
        if not os.path.isdir(self.__outdir__):
            logging.info("Create non-existing output directories %s", self.__outdir__)
            os.makedirs(self.__outdir__)
        if os.path.isfile(self.__json_log__):
            logging.warning("Execution summary json file: %s exist and will be replaced", self.__json_log__)

        # load install config
        if self.__install_config_file__ is not None:
            try:
                logging.debug("Loading install configuration file: %s", self.__install_config_file__)
                self.__install_config__ = ConfigParser()
                self.__install_config__.read(self.__install_config_file__)
                # check config
                logging.debug("Check install configuration file: %s", self.__install_config_file__)
                self.check_install_config(self.__install_config__)
            except Exception as e:
                self.end_process(error="Unexpected error while loading install configuration file %s: %s" %
                                       (self.__install_config__, str(e)), error_code=10)

        # load parameter file (only if needed)
        if not self.__no_parameters__:
            try:
                logging.debug("Loading parameter file: %s", self.__param_file__)
                self.__parameters__ = ConfigParser()
                self.__parameters__.read(self.__param_file__)
                # check config
                logging.debug("Check parameter file: %s", self.__param_file__)
                self.check_parameters(self.__parameters__)
            except Exception as e:
                self.end_process(error="Unexpected error while loading parameters file %s: %s" %
                                       (self.__param_file__, str(e)), error_code=11)
        else:
            logging.debug("Module without parameters.")

        # start module process
        try:
            output_files_list = self.start_process(**kwargs)
            self.end_process(error_code=0, files=output_files_list)
        except NotImplementedError as nie:
            raise nie
        except Exception as e:
            self.end_process(error_code=911, error="Unexpected error: %s:\n%s" % (str(e), traceback.format_exception()))

    def end_process(self, error_code=0, error=None, files=None):
        # if process end with error, print info in log system
        if error_code != 0 and error is not None:
            logging.error(error)
        # Print analysis execution summary in JSON format.
        if self.__json_log__ is None:
            file_handler = sys.stderr
        else:
            file_handler = open(self.__json_log__, "w")
        if files is None:
            files = []
        if error is None:
            error = ""
        file_handler.write(json.dumps(
            dict({
                "meta": dict({
                    "status": error_code,
                    "jobid": self.__job__,
                    "runid": self.__run__,
                    "error": error,
                    "tool": self.__NAME__,
                    "version": self.__VERSION__
                }),
                "files": files
            })
        ))
        if file_handler == sys.stderr:
            file_handler.write("\n")
        file_handler.close()

        # Exit script.
        exit(error_code)

    def init_std_options(self, usage_str=None, inst_config=None):
        if usage_str is None:
            usage_str = "Usage: %prog [options] -o prefix input"
        self.__parser__ = OptionParser(usage=usage_str)
        self.__parser__.version = self.__VERSION__
        self.__parser__.add_option("-o", "--out-prefix", dest="prefix", metavar="Prefix",
                                   help="Prefix use to name output files (ex: output_dir/sample_1). "
                                        "If it doesn't exist, output directory will be created.")
        if not self.__no_parameters__:
            self.__parser__.add_option("-p", "--params", dest="param", help="Module parameters file.", metavar="FILE")
        if inst_config is not None:
            self.__parser__.add_option("-c", "--config", dest="config", default=inst_config, metavar="FILE",
                                       help="Use a specific install configuration file.")
        self.__parser__.add_option("-j", "--job", dest="jobid", default="0",
                                   help="Unique job identifier", metavar="STRING")
        self.__parser__.add_option("-r", "--run", dest="runid", default="0",
                                   help="Unique run identifier", metavar="STRING")
        self.__parser__.add_option("-l", "--log", dest="logfile",
                                   help="Alignment execution log file, STDOUT if not defined.", metavar="STRING")
        self.__parser__.add_option("-d", "--debug", dest="debug", default=False, action="store_true",
                                   metavar="BOOLEAN", help="Set log level to debug.")
        self.__parser__.add_option("-v", "--version", dest="version", help="Print version and exit",
                                   action="store_true", default=False, metavar="INT")
        return

    def check_std_options(self, options):
        # if version is required print and exit
        if options.version:
            print(os.path.basename(sys.argv[0]) + " version " + self.__VERSION__)
            exit(0)

        # init log system
        log_level = logging.INFO
        if options.debug:
            log_level = logging.DEBUG
        format_str = '['+str(self.__NAME__)+'][%(levelname)s]:%(asctime)s:%(message)s'
        format_date = '%m/%d/%Y %H:%M:%S'
        if options.logfile:
            logging.basicConfig(format=format_str, filename=options.logfile, level=log_level, datefmt=format_date)
        else:
            logging.basicConfig(format=format_str, level=log_level, datefmt=format_date)

        # set run and job
        self.__run__ = str(options.runid)
        self.__job__ = str(options.jobid)

        # check prefix options and set output base
        reg = re.compile('[^\w\s\/\.@_\-+~$*=]')
        if options.prefix is None:
            self.__parser__.error("Mandatory option -o prefix is missing")
        elif re.search(reg, options.prefix):
            self.__parser__.error("Invalid mandatory option -o prefix '" + str(options.prefix) +
                                  "' contains illegal characters.")
        # set config file
        if self.__install_config_file__ is not None:
            self.__install_config_file__ = options.config
        if not self.__no_parameters__:
            # set parameter file
            self.__param_file__ = options.param

    def init_custom_options(self):
        pass

    def check_custom_options(self, options):
        pass

    def check_args(self, args):
        pass

    def check_install_config(self, install_config):
        pass

    def check_parameters(self, parameters):
        pass

    @abc.abstractmethod
    def start_process(self, **kwargs):
        raise NotImplementedError

