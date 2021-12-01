from bioit_module import PipelineParameters
from pathlib import Path
import pytest


def create_parameters(ref_dir= '/mnt/data', gencode_version = 38):
    parameters = PipelineParameters()
    parameters.reference_dir = ref_dir
    parameters.gencode_version = gencode_version
    parameters.validate()
    return parameters


class TestPipelineParameters:
    def test_get_gtf_file_valid(self):
        parameters = create_parameters()
        assert '/mnt/data/gtf/gencode.v38.annotation.gtf' == str(parameters.get_gtf_file())

    def test_get_fasta_ref_fa(self, monkeypatch):
        def mockreturn_fa(ref_dir):
            return [Path('dummy.fa')]
        monkeypatch.setattr(Path, "iterdir", mockreturn_fa)
        parameters = create_parameters(ref_dir='files')
        assert 'dummy.fa' == str(parameters.get_fasta_ref())

    def test_get_fasta_ref_fasta(self, monkeypatch):
        def mockreturn_fa(ref_dir):
            return [Path('dummy.fasta')]
        monkeypatch.setattr(Path, "iterdir", mockreturn_fa)
        parameters = create_parameters(ref_dir='files')
        assert 'dummy.fasta' == str(parameters.get_fasta_ref())

    def test_get_fasta_ref_not_found(self, monkeypatch):
        def mockreturn_fa(ref_dir):
            return []
        monkeypatch.setattr(Path, "iterdir", mockreturn_fa)
        parameters = create_parameters(ref_dir='files')
        with pytest.raises(Exception):
            parameters.get_fasta_ref()

    def test_get_fasta_ref_too_many_fasta(self, monkeypatch):
        def mockreturn_fa(ref_dir):
            return [Path('dummy.fasta'), Path('dummy.fa')]
        monkeypatch.setattr(Path, "iterdir", mockreturn_fa)
        parameters = create_parameters(ref_dir='files')
        with pytest.raises(Exception):
            parameters.get_fasta_ref()
