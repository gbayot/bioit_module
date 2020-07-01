import argparse
import os
import pytest
from bioit_module.command_parser import CommandParser


class TestCommandParser:
    def test_is_valid_filename_success(self):
        assert CommandParser._is_valid_filename("/data/input/file.bam") == "/data/input/file.bam"

    def test_is_valid_filename_exception_degree(self):
        with pytest.raises(argparse.ArgumentTypeError):
            CommandParser._is_valid_filename("/data/input/file.b°am")

    def test_is_valid_filename_exception_space(self):
        with pytest.raises(argparse.ArgumentTypeError):
            CommandParser._is_valid_filename("/data/input/file\ 1.bam")

    def test_is_valid_file_success(self, monkeypatch):
        def mockreturn(filename):
            return True
        monkeypatch.setattr(os.path, "isfile", mockreturn)
        assert CommandParser._is_valid_file("test.bam") == "test.bam"

    def test_is_valid_file_exception_does_not_exist(self, monkeypatch):
        def mockreturn(filename):
            return False
        monkeypatch.setattr(os.path, "isfile", mockreturn)
        with pytest.raises(argparse.ArgumentTypeError):
            CommandParser._is_valid_file("test.bam")
