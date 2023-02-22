from argschema import ArgSchemaParser
import os
import logging
import time

import numpy as np
import pandas as pd

from ...common.utils import load_kilosort_data

from .extract_waveforms import extract_waveforms, writeDataAsNpy
from .waveform_metrics import calculate_waveform_metrics

def calculate_mean_waveforms(args):

    print('ecephys spike sorting: mean waveforms module')

    start = time.time()

    print("Loading data...")

    rawData = np.memmap(args['ephys_params']['ap_band_file'], dtype='int16', mode='r')

    # reference channels may have been removed, in which case args['ephys_params']['num_channels'] needs to be corrected
    if (rawData.size % args['ephys_params']['num_channels']) == 0:
        data = np.reshape(rawData, (int(rawData.size/args['ephys_params']['num_channels']), args['ephys_params']['num_channels']))
    else:
        nc = args['ephys_params']['num_channels'] - len(args['ephys_params']['reference_channels'])
        if (rawData.size % mc) == 0:
            data = np.reshape(rawData, (int(rawData.size/nc), nc))
            args['ephys_params']['num_channels'] = nc
        else:
            raise RuntimeError(f"Data contained in \"{args['ephys_params']['ap_band_file']}\" cannot be reshaped to a time x channels matrix")

    spike_times, spike_clusters, spike_templates, amplitudes, templates, channel_map, clusterIDs, cluster_quality = \
            load_kilosort_data(args['directories']['kilosort_output_directory'], \
                args['ephys_params']['sample_rate'], \
                convert_to_seconds = False)

    print("Calculating mean waveforms...")

    waveforms, spike_counts, coords, labels, metrics = extract_waveforms(data, spike_times, \
                spike_clusters,
                templates,
                channel_map,
                args['ephys_params']['bit_volts'], \
                args['ephys_params']['sample_rate'], \
                args['ephys_params']['vertical_site_spacing'], \
                args['mean_waveform_params'])

    writeDataAsNpy(waveforms, args['mean_waveform_params']['mean_waveforms_file'])
    metrics.to_csv(args['waveform_metrics']['waveform_metrics_file'])

    execution_time = time.time() - start

    print('total time: ' + str(np.around(execution_time,2)) + ' seconds')
    print()

    return {"execution_time" : execution_time} # output manifest


def main():

    from ._schemas import InputParameters, OutputParameters

    mod = ArgSchemaParser(schema_type=InputParameters,
                          output_schema_type=OutputParameters)

    output = calculate_mean_waveforms(mod.args)

    output.update({"input_parameters": mod.args})
    if "output_json" in mod.args:
        mod.output(output, indent=2)
    else:
        print(mod.get_output_json(output))


if __name__ == "__main__":
    main()
