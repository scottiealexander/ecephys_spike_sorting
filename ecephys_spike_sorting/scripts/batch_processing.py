import os, sys, re
import subprocess, argparse, tempfile

from create_input_json import createInputJson

# NOTE: this is a modified version of the batch_processing script that came with
# ecephys_spike_sorting

# ============================================================================ #
class DirectoryManager:
    def __init__(self, path):
        if len(path) == 0:
            self.cleanup = True
            self.tmpdir = tempfile.TemporaryDirectory()
            self.path = self.tmpdir.name
        elif os.path.isdir(path):
            self.cleanup = False
            self.tmpdir = ""
            self.path = path
        else:
            raise RuntimeError(f"Given directory \"{path}\" is not valid")

    def __enter__(self):
        return self.path

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.cleanup:
            self.tmpdir.cleanup()

# ============================================================================ #
# yes, the probe_tpye input is not currently used, it's just a placeholder
def run_quality_control(sorted_directories, modules, json_directory, probe_type="3a"):

    ALL_MODULES = [
        'extract_from_npx',
        'depth_estimation',
        'median_subtraction',
        'kilosort_helper',
        'kilosort_postprocessing',
        'noise_templates',
        'mean_waveforms',
        'quality_metrics'
        ]

    with DirectoryManager(json_directory) as json_dir:

        for directory in sorted_directories:

            session_id = os.path.basename(directory)

            input_json = os.path.join(json_dir, session_id + '-input.json')
            output_json = os.path.join(json_dir, session_id + '-output.json')

            info = createInputJson(input_json, kilosort_output_directory=directory)

            for module in modules:

                if module in ALL_MODULES:
                    command = (
                        f"python -W ignore -m ecephys_spike_sorting.modules.{module}"
                        f" --input_json \"{input_json}\""
                        f" --output_json \"{output_json}\""
                     )

                    subprocess.check_call(command, shell=True)

                else:
                    module_list = "\n\t" + "\n\t".join(ALL_MODULES)
                    raise RuntimeError(f"Invalid module \"{module}\", must be one of:{module_list}")

# ============================================================================ #
def add_args(p):
    json_directory = ""
    modules = ['kilosort_postprocessing','noise_templates','mean_waveforms','quality_metrics']
    p.add_argument("-p", "--probe", help="The type of Neuropixel probe used", default="3a")
    p.add_argument("-j", "--jsondir", help="Local directory to store json input and output files (if unspecified a temporary directory will be created and later deleted)", default=json_directory)
    p.add_argument("-m", "--modules", help=f"A comma seperated list of ecephys_spike_sorting modules to run (e.g. \"{','.join(modules)}\")", default=",".join(modules))
    p.add_argument("dirs", help="A list of Kilosort output directories to process", nargs=argparse.REMAINDER)

# ============================================================================ #
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    add_args(parser)
    args = parser.parse_args()

    # allow for space and ; seperators (even though we asked for commas)
    modules = re.split(r"[,; ]+\s*", args.modules)

    sorted_directories = list()
    for dir in args.dirs:
        if os.path.isdir(dir):
            sorted_directories.append(dir)
        else:
            print("**INVALID DIR***: " + dir)

    run_quality_control(sorted_directories, modules, args.jsondir, args.probe)
