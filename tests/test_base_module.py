import shutil
from unittest import mock
import pytest, os
from bioit_module.base_module import BaseModule

@pytest.fixture
def opts():
    options = mock.Mock()
    options.version = False
    options.runid = "01"
    options.jobid = "02"
    options.prefix = "this/is/a/test"
    return options


@pytest.fixture
def module():
    return FakeModule("name", "version", "suffix")


class FakeModule(BaseModule):
    def start_process(self, **kwargs):
        pass


def test_cannot_instantiate():
    with pytest.raises(TypeError):
        BaseModule()


def test_init_module_require_args():
    with pytest.raises(TypeError):
        mod = FakeModule()


def test_init_module():
    mod = FakeModule("name", "version", "suffix")
    assert mod.name == "name"
    assert mod.version == "version"
    assert mod.suffix == "suffix"


def test_init_module_with_usage():
    mod = FakeModule("name", "version", "suffix", usage="RTFM")
    mod.init_std_options()
    assert mod.parser.usage == "RTFM"


def test_init_module_with_config():
    mod = FakeModule("name", "version", "suffix", install_config="test.ini")
    mod.init_std_options()
    assert mod.name == "name"
    assert mod.version == "version"
    assert mod.suffix == "suffix"
    assert mod._install_config_file == "test.ini"


def test_init_module_with_parameters():
    mod = FakeModule("name", "version", "suffix", no_parameters=True)
    mod.init_std_options()
    assert mod._no_parameters == True


def test_check_std_options_no_prefix(opts, module):
    opts.prefix = None
    module.init_std_options()
    with pytest.raises(SystemExit):
        module.check_std_options(options=opts)


def test_check_std_options_invalid_prefix(opts, module):
    opts.prefix = "some^invalids?chars%inùpath"
    module.init_std_options()
    with pytest.raises(SystemExit):
        module.check_std_options(options=opts)


def test_check_std_options_pass(opts, module):
    module.check_std_options(options=opts)
    assert module.run_id == "01"
    assert module.job_id == "02"
    assert module.output_dir == "this/is/a"
    assert module.prefix == "test"
    assert module.version == "version"


@mock.patch('optparse.OptionParser.parse_args')
def test_run_noparam_noconfig(mock_parse_args, opts):
    mod = FakeModule("name", "version", "suffix", no_parameters=True)
    args = ["not an input file"]
    mock_parse_args.return_value = (opts, args)
    assert mod.run() == 0
    assert os.path.isfile(os.path.join(mod.output_dir, mod.prefix + "_mod_log.json"))
    # remove created output directory
    shutil.rmtree("this")


def test_load_config_no_file_error():
    mod = FakeModule("name", "version", "suffix")
    mod._install_config_file = "NotAFile"
    mod._json_log = "summary.json"
    assert mod.load_install_config() == 10
    os.unlink("summary.json")


@mock.patch('bioit_module.BaseModule.check_install_config')
def test_load_config_file_check_error(mock_check_install_config):
    mod = FakeModule("name", "version", "suffix")
    mod._install_config_file = "pytest.ini"
    mod._json_log = "summary.json"
    mock_check_install_config.side_effect = Exception("Random error")
    assert mod.load_install_config() == 10
    os.unlink("summary.json")


@mock.patch('bioit_module.BaseModule.check_install_config')
def test_load_config_file_check_ok(mock_check_install_config):
    mod = FakeModule("name", "version", "suffix")
    mod._install_config_file = "pytest.ini"
    mock_check_install_config.return_value = None
    assert mod.load_install_config() == 0


@mock.patch('bioit_module.BaseModule.check_parameters')
def test_load_parameter_file_check_error(mock_check_parameters):
    mod = FakeModule("name", "version", "suffix")
    mod._param_file = "NotAFile"
    mod._json_log = "summary.json"
    mock_check_parameters.side_effect = Exception("Random error")
    assert mod.load_parameter_file() == 11
    os.unlink("summary.json")


@mock.patch('bioit_module.BaseModule.check_parameters')
def test_load_config_file_check_ok(mock_check_parameters):
    mod = FakeModule("name", "version", "suffix")
    mod._param_file = "pytest.ini"
    mock_check_parameters.return_value = None
    assert mod.load_parameter_file() == 0
