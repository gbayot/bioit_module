# Bioit Module

OncoDNA bioit analysis module base library. This library define base requirement and comportement of an bio-informatics analysis module.

## Git repository

https://gitlab.oncoworkers.oncodna.com/bioinfo/libraries/bioit_module.git

## Installation

```sh
pip install 
--index-url http://devpi.oncoworkers.oncodna.com/root/pypi/+simple
--extra-index-url http://devpi.oncoworkers.oncodna.com/root/public/+simple
--trusted-host devpi.oncoworkers.oncodna.com

bioit_module==2.0.0
```

## What is defined

### Standard options

| Option                         | Mandatory | Description                                                  |
| ------------------------------ | --------- | ------------------------------------------------------------ |
| -h, --help                     |           | show module help message and exit.                           |
| -v, --version                  |           | Print version and exit.                                      |
| -o Prefix, --out-prefix=Prefix | Always    | Prefix use to name output files (ex:output_dir/sample_1). If it doesn't exist, output directory will be created. |
| -p FILE, --params=FILE         | If ask    | Module parameters file.                                      |
| -c FILE, --config=FILE         | If ask    | Use a specific install configuration file.                                  |
| -l STRING, --log=STRING        | Always    | log file.                             |
| -d, --debug                    | No        | Set log level to debug.                                      |


## Usage

### CommandParser

```python
from bioit_module import CommandParser


class AlphalistCommandParser(CommandParser):
    def set_custom_option(self):
        self.parser.add_argument(
            "-O",
            "--oncoit",
            dest="oncoit",
            required=True,
            help="OncoIT3 library configuration file.",
            type=self._is_valid_file
        )
        self.parser.add_argument(
            "-t",
            "--targetfile",
            dest="targetfile",
            required=True,
            help="CSV file description for alpha list targets",
            type=self._is_valid_file
        )
        self.parser.add_argument(
            "-b",
            "--bed",
            dest="bed",
            required=True,
            help="BED file describing targeted regions.",
            type=self._is_valid_file
        )
        self.parser.add_argument("bam", help="BAM file", type=self._is_valid_file)

alphalist_command_parser = AlphalistCommandParser(
    version="2.0.0", default_install_config="/data/config.ini"
)
```


### BioitLauncher

```python
import os
from bioit_module import BioitLauncher, exit_code, exception

from schematics.models import Model
from schematics.types import IntType, FloatType, StringType


class AlphalistConfig(Model):
    samtools = StringType(required=True)


class AlphalistParameters(Model):
    mincov = IntType(required=True, min_value=0)
    minfreq = FloatType(required=True, min_value=0, max_value=100)
    minindelfreq = FloatType(required=True, min_value=0, max_value=100)
    minStrandFreq = FloatType(required=True, min_value=0, max_value=100)
    minvarcov = IntType(required=True, min_value=0)
    minindelcov = IntType(required=True, min_value=0)
    ThresholdQcFail = IntType(required=True)


class AlphalistLauncher(BioitLauncher):
    def _validate_args(self):
        extension = os.path.splitext(self.args.bam)[1]
        if extension != ".bam":
            raise exception.InvalidArgsError("Bam file extension isn't .bam")

    def _validate_install_config(self):
        if os.path.basename(self.install_config.samtools) != "samtools":
            raise exception.InvalidInstallConfigError("samtools binary isn't named 'samtools'")

    def _validate_params(self):
        if self.params.minindelfreq < self.params.minfreq:
            raise exception.InvalidParametersError("minindelfreq is smaller than minfreq")

    def read_install_config(self):
        config = self._read_config_file(self.args.config)
        install_config = AlphalistConfig()
        install_config.samtools = config.get("EXTERNALS", "samtools")
        install_config.validate()
        return install_config

    def read_parameters(self):
        config = self._read_config_file(self.args.params)
        parameters = AlphalistParameters()
        parameters.mincov = config.get("ANALYSIS", "mincov")
        parameters.minfreq = config.get("ANALYSIS", "minfreq")
        parameters.minindelfreq = config.get("ANALYSIS", "minindelfreq")
        parameters.minStrandFreq = config.get("ANALYSIS", "minStrandFreq")
        parameters.minvarcov = config.get("ANALYSIS", "minvarcov")
        parameters.minindelcov = config.get("ANALYSIS", "minindelcov")
        parameters.ThresholdQcFail = config.get("ANALYSIS", "ThresholdQcFail")
        parameters.validate()
        return parameters

    def launch(self):
        suffix = "_alphalist"
        output_file = os.path.join(self.output_dir, suffix + ".csv")
        json_file = os.path.join(self.output_dir, suffix + ".json")
        try:
            print(
                {
                    "target_file": self.args.targetfile,
                    "bed_file": self.args.bed,
                    "bam": self.args.bam,
                    "parameters": self.params,
                    "install_config": self.install_config,
                    "output_dir": self.output_dir,
                    "prefix": self.args.prefix,
                    "output_file": output_file,
                    "json_file": json_file,
                }
            )
        except Exception as e:
            self.logger.exception('')
            exit(exit_code.UnknownError)


AlphalistLauncher(command_parser=alphalist_command_parser).launch()
```

