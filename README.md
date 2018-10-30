## Description

OncoDNA bioit analysis module base library. This library define base requierement and comportement of an bio-informatics analysis module.

### Technical informations

| Language | Type    | version |
| -------- | ------- | ------- |
| python3  | library | 0.1     |

### git repository

<to be define>

### installation

```bash
pip install git+ssh://git@gitlab.oncoworkers.oncodna.com/bioinfo/libs/bioit_module.git
```

## What is defined

### Standard options

| Option                         | Mandatory | Description                                                  |
| ------------------------------ | --------- | ------------------------------------------------------------ |
| -h, --help                     |           | show module help message and exit.                           |
| -v, --version                  |           | Print version and exit.                                      |
| -o Prefix, --out-prefix=Prefix | Always    | Prefix use to name output files (ex:output_dir/sample_1). If it doesn't exist, output directory will be created. |
| -p FILE, --params=FILE         | If ask    | Module parameters file.                                      |
| -c FILE, --config=FILE         | No        | Use a specific install configuration file.                   |
| -j STRING, --job=STRING        | No        | Unique job identifier.                                       |
| -r STRING, --run=STRING        | No        | Unique run identifier.                                       |
| -l STRING, --log=STRING        | No        | log file, STDOUT if not defined.                             |
| -d, --debug                    | No        | Set log level to debug.                                      |

### Logging system and mods

Library instanciate [logging](https://docs.python.org/3.6/howto/logging.html) object, with predefined printing format. Actuamlly only 2 mods are available:

- Default: print info, warning, error and critical messages.
- Debug: also print debug messages.

**Usage**: 

logging.level("message"), where level is one of debug, info, warning, error and critical.

**Log format:**

`[MODULE_NAME][MESSAGE_LEVEL]:MM/DD/YYY HH:mm:ss:Mesage`

**Examples**:

```python
logging.debug("Check  input arguments.")
logging.info("Create non-existing output directories %s", self.__outdir__)
logging.warning("File %s exist and will be override", final_bam)
logging.error("Missing %s definition value in parameters", param_name)
logging.critical("Cannot open input file %s", input_bam)
```

### Execution summary file

By convention, each bioit analysis module will print an execution summary file in json with meta informations. This file will always have "_mod_log.json" suffix and will be filled by calling of "end_process" method.

**Content:**

```json
{
    'meta':{
        "status": error_code,
        "jobid": execution_job_id,
        "runid": execution_run_id,
        "error": error_message,
        "tool": module_name,
        "version": module_version
    },
    'files':[list_of_output_files_path]
}
```

### Some additionnal utility methods

<None available yet>

## Usage

### Example: A module to say hello

```python
from BaseModule import BaseModule

class Hello(BaseModule):
	uname = None
    
    def check_args(self, args):
        if len(args) == 0:
            self.parser.error("Missing input argument name")
    	self.uname = args[0]
    
    def start_process(self):
		print("This module say hello to %s" % self.uname)
        return []

if __name__ == "__main__":
    hello = Hello(name="HELLO", version="0.0.0", install_config=None, suffix="hello", no_parameters=True, usage="%prog [options] -o prefix name")
    hello.run()
```

### Exception and error management: Good pratice

#### Arguments and options error

As module implementation allow usage of custom options and argument verification of those command lines parameters have to be also implemented. If verifications lead to error they have to be return as module command line parser error.

**Example:** 

```python 
self.parser.error("Missing input argument name")
```

#### Other error or exception

All exception that can occurs have to be catch, if exception leads to process end use end_process method to produce execution log file and exit. If an exception not manage by module occur in start_process method it will be manage by library and process will exit with error code 911.

**Example:** 

```python
try:
    do_something()
except Exception as e:
    self.end_process(error_code=1, error="Something goes wrong in do something: %s" % str(e))
```

#### Reserved Error Codes

4 exit status codes are reserved and cannot be use in module implementation:

| Exit code | Description                                                  |
| --------- | ------------------------------------------------------------ |
| 0         | All ends without error                                       |
| 10        | Unknown error while loading install configuration file       |
| 11        | Unknown error while loading parameters file                  |
| 911       | Unknown exception will running process. Call emergency service to investigate. |

## Methods that require implementation

### Module options and arguments

#### def init_custom_options(self)

If additional commad line arguments are necessary for plugin execution, there must be define in ths method like in example below:

```python
def init_custom_options(self):
    self.parser.add_option("-f", "--genome", dest="genome", help="Reference genome FASTA file to align reads on.", metavar="FILE")
```

#### def check_custom_options(self, options)

If some checks have to be performed on additionnal command line options they have to be set in this method.

```python
def check_custom_options(self, options):
    if options.genome is None:
        self.parser.error("Mandatory option -f genome is missing")
    elif not os.path.exists(options.genome):
        self.parser.error("Reference genome not found '%s': Not such file or directory" % options.genome)
```

#### def check_args(self, args)

If some verification have to be done on input file(s), all check must be implementes in this method.

```python
def check_args(self, args):
    if len(args) < 1:
        self.parser.error('Missing reads input file argument.')
    elif len(args) > 1:
        self.parser.error('Too many arguments as reads input file.')
    elif not os.path.exists(args[0]):
        self.parser.error("Input file not found '%s': Not such file or directory" % args[0])
```

### Configuration and Parameters

#### Definitions

**Configuration**: Local bin and file dependency, e.g.: path to samtools executable bin

**Parameters**: Module metrics option (e.g.: minimum coverage) or share dependency (e.g.: path to hg19.fasta refernce genome).

#### File Format

Both install configuration and parameters file share same format: _ini_ like

```ini
[SECTION_NAME]
key=value
```

Format of configuration and parameters files are always checked by library.

#### Install configuration and verification

If no installation configuration is requiere by analysis module, set `install_config=None` in parent init method, else sepcify default file to use.

If other verification than file format of configuration file are needed, module must implement `check_install_config` method. Raised exception will lead to exit code 10, to end with a more specific exit code, use `end_process` method.

**Example**:

```python
def check_install_config(self, install_config):
    if not install_config.has_section("EXTERNALS"):
        raise Exception("Invalid configuration, no section 'EXTERNALS' was found.")
    elif not install_config.has_option("EXTERNALS", "tmap"):
        raise Exception("Invalid configuration, tmap binary location was not defined.")
    elif not install_config.has_option("EXTERNALS", "samtools"):
        raise Exception("Invalid configuration, tmap binary location was not defined.")
    elif not os.path.exists(install_config.get("EXTERNALS", "tmap")):
        self.end_process(error_code=1, error="TMAP binary not found at given location '" + str(install_config.get("EXTERNALS", "tmap")) + "'.")
```

#### Parameters definition and verification

If no parameters file is requiere by analysis module, set `no_parameters=True` in parent init method, else sepcify `False` or don't use method argument.&ge;

If other verification than format of parameter file are needed, module must implement `check_parameters` method. Raised exception will lead to exit code 11, to end with a more specific exit code, use `end_process` method.

```python
def check_parameters(self, parameters):
    if not parameters.has_section("ANALYSIS"):
        raise Exception("Invalid configuration, no section 'ANALYSIS' was found.")
    elif parameters.getint("ANALYSIS", "min_cov") < 0:
        self.end_process(error_code=2, error="Invalid minimum coverage value in parameter file, 'min_cov' must be >=0")
```

### Module analysis: "`start_process`"

Madatory implementation is require for the core method of the module, all execution code goes in.

This method have to return list of output files path.

If an non-catch exception occur during execution, module exection will stop with 911 exit code.