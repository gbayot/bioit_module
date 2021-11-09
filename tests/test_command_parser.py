import argparse
import os
import pytest
from bioit_module.command_parser import CommandParser
from pathlib import Path
import fastq_utils


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

    def test_is_valid_dir_success(self, monkeypatch):
        def mockreturn(dirpath):
            return True
        monkeypatch.setattr(Path, 'is_dir', mockreturn)
        assert CommandParser._is_valid_dir('/Path/to/test')

    def test_is_valid_dir_exception_does_not_exist(self, monkeypatch):
        def mockreturn(dirpath):
            return False
        monkeypatch.setattr(Path, 'is_dir', mockreturn)
        with pytest.raises(argparse.ArgumentTypeError):
            CommandParser._is_valid_dir('/Path/to/test')

    def test_is_valid_integer(self):
        assert CommandParser._is_valid_integer('15')

    def test_is_valid_integer_exception_contains_invalid_characters(self):
        with pytest.raises(argparse.ArgumentTypeError):
           CommandParser._is_valid_integer('115d5')

    def test_is_valid_fastq(self, monkeypatch):
        def mockreturn(fastq):
            return True
        monkeypatch.setattr(fastq_utils, 'is_valid_fastq', mockreturn)
        assert CommandParser._is_valid_fastq('test.fastq')

    def test_is_valid_fastq_exception_invalid_fastq(self, monkeypatch):
        def mockreturn(fastq):
            return False
        monkeypatch.setattr(fastq_utils, 'is_valid_fastq', mockreturn)
        with pytest.raises(argparse.ArgumentTypeError):
            CommandParser._is_valid_fastq('test.fastq')