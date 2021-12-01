from schematics.models import Model
from schematics.types import BooleanType, StringType
from pathlib import Path

class PipelineParameters(Model):
    reference_dir = StringType(required=True)
    gencode_version = StringType(required=True)

    def get_gtf_file(self):
        return Path(self.reference_dir, 'gtf', "gencode.v{}.annotation.gtf".format(self.gencode_version))

    def get_gtf_collapse_file(self):
        return Path(self.reference_dir, 'gtf', "gencode.v{}.collapsed.gtf".format(self.gencode_version))

    def get_fasta_ref(self):
        fasta_files = [path for path in Path(self.reference_dir).iterdir() if path.suffix in ['.fa', '.fasta']]
        if len(fasta_files) != 1:
            raise Exception("0 or too many fasta found in reference directory ({})".format(self.reference_dir))
        return fasta_files[0]
            