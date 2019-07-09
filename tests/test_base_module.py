import shutil
from unittest import mock
import pytest, os
from bioit_module.base_module import BaseModule


@pytest.fixture
def opts():
    return mock.Mock(version=False, runid="01", jobid="02", prefix="this/is/a/test")


@pytest.fixture
def module():
    return FakeModule("name", "version", "suffix")


class FakeModule(BaseModule):
    def start_process(self, **kwargs):
        return 0, []


class FakeModuleError(BaseModule):
    def start_process(self, **kwargs):
        raise Exception("Random error")


def test_cannot_instantiate():
    with pytest.raises(TypeError):
        BaseModule()


def test_init_module_require_args():
    with pytest.raises(TypeError):
        mod = FakeModule()


def test_init_module(module):
    assert module.name == "name"
    assert module.version == "version"
    assert module.suffix == "suffix"


def test_init_module_with_usage():
    mod = FakeModule("name", "version", "suffix", usage="RTFM")
    mod.init_std_options()
    assert mod.parser.usage == "RTFM"


def test_init_module_with_config():
    mod = FakeModule("name", "version", "suffix", install_config="test.ini")
    mod.init_std_options()
    assert mod._install_config_file == "test.ini"


def test_init_module_with_parameters():
    mod = FakeModule("name", "version", "suffix", no_parameters=False)
    mod.init_std_options()
    assert mod._no_parameters is False


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


@mock.patch("optparse.OptionParser.parse_args")
class TestRun:
    def test_ok(self, mock_parse_args, opts):
        mod = FakeModule("name", "version", "suffix", no_parameters=True, install_config=None)
        args = ["not an input file"]
        mock_parse_args.return_value = (opts, args)
        assert mod.run() == 0
        assert os.path.isfile(os.path.join(mod.output_dir, mod.prefix + "_mod_log.json"))
        # remove created output directory
        shutil.rmtree("this")

    def test_error(self, mock_parse_args, opts):
        module = FakeModuleError("name", "version", "suffix", no_parameters=True, install_config=None)
        args = ["not an input file"]
        mock_parse_args.return_value = (opts, args)
        assert module.run() == 911
        assert os.path.isfile(os.path.join(module.output_dir, module.prefix + "_mod_log.json"))
        shutil.rmtree("this")


def test_load_config_no_file_error(module):
    module._install_config_file = "NotAFile"
    module._json_log = "summary.json"
    assert module.load_install_config() == 10
    os.unlink("summary.json")


@mock.patch("bioit_module.BaseModule.check_install_config")
class TestLoadConfigFileCheck:
    def test_error(self, mock_check_install_config, module):
        module._install_config_file = "pytest.ini"
        module._json_log = "summary.json"
        mock_check_install_config.side_effect = Exception("Random error")
        assert module.load_install_config() == 10
        os.unlink("summary.json")

    def test_ok(self, mock_check_install_config, module):
        module._install_config_file = "pytest.ini"
        mock_check_install_config.return_value = 0
        assert module.load_install_config() == 0


@mock.patch("bioit_module.BaseModule.check_parameters")
class TestLoadParameterFileCheck:
    def test_error(self, mock_check_parameters, module):
        module._param_file = "NotAFile"
        module._json_log = "summary.json"
        mock_check_parameters.side_effect = Exception("Random error")
        assert module.load_parameter_file() == 11
        os.unlink("summary.json")

    def test_ok(self, mock_check_parameters, module):
        module._param_file = "pytest.ini"
        mock_check_parameters.return_value = None
        assert module.load_parameter_file() == 0

