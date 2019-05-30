import os, io, json, glob, sys

if sys.platform == 'linux':
    import pwd

def create_samba_directory(samba_server, samba_share):

    if sys.platform == 'linux':
        proc_owner_uid = str(pwd.getpwnam(os.environ['USER']).pw_uid)
        share_string = 'smb-share:server={},share={}'.format(samba_server, samba_share)
        data_dir = os.path.join('/', 'var', 'run', 'user', proc_owner_uid, 'gvfs', share_string)
    else:
        data_dir = r'\\' + os.path.join(samba_server, samba_share)

    return data_dir

def createInputJson(npx_directory, output_file, nwb_file = None):

    settings_xml = os.path.join(npx_directory, 'settings.xml')

    drive, tail = os.path.split(npx_directory)

    extracted_data_directory = npx_directory + '_sorted'
    probe_json = os.path.join(extracted_data_directory, 'probe_info.json')
    kilosort_output_directory = glob.glob(os.path.join(extracted_data_directory, 'continuous', 'Neuropix-*-100.0'))[0]

    dictionary = \
    {
        "npx_file": npx_directory,
        "settings_xml": settings_xml,
        "probe_json" : probe_json,

        "npx_extractor_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\npxextractor\\Release\\NpxExtractor.exe",
        "npx_extractor_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\npxextractor",

        "median_subtraction_executable": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\Builds\\VisualStudio2013\\Release\\SpikeBandMedianSubtraction.exe",
        "median_subtraction_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\spikebandmediansubtraction\\",

        "kilosort_location": "C:\\Users\\svc_neuropix\\Documents\\MATLAB",
        "kilosort_repo": "C:\\Users\\svc_neuropix\\Documents\\GitHub\\kilosort2",
        "kilosort_version" : 2,
        "surface_channel_buffer" : 15,

        "mean_waveforms_file" : os.path.join(kilosort_output_directory, 'mean_waveforms.npy'),
        "waveform_metrics_file" : os.path.join(kilosort_output_directory, 'waveform_metrics.csv'),

        "directories": {
            "extracted_data_directory": extracted_data_directory,
            "kilosort_output_directory": kilosort_output_directory
        },

        "ephys_params": {
            "sample_rate" : 30000,
            "lfp_sample_rate" : 2500,
            "bit_volts" : 0.195,
            "num_channels" : 384,
            "reference_channels" : [36, 75, 112, 151, 188, 227, 264, 303, 340, 379],
            "vertical_site_spacing" : 20e-6
        }, 

        "depth_estimation_params" : {
            "hi_noise_thresh" : 50.0,
            "lo_noise_thresh" : 3.0,
            "save_figure" : 1,
            "figure_location" : extracted_data_directory,
            "smoothing_amount" : 5,
            "power_thresh" : 2.5,
            "diff_thresh" : -0.06,
            "freq_range" : [0, 10],
            "max_freq" : 150,
            "channel_range" : [370, 380],
            "n_passes" : 1,
            "air_gap" : 100,
            "skip_s_per_pass" : 1000
        }, 

        "kilosort2_params" : {
        
            "chanMap" : "'chanMap.mat'",
            "fshigh" : 150,
            "minfr_goodchannels" : 0.1,
            "Th" : '[10 4]',
            "lam" : 10,
            "AUCsplit" : 0.9,
            "minFR" : 1/50.,
            "momentum" : '[20 400]',
            "sigmaMask" : 30,
            "ThPre" : 8
        },

        "ks_postprocessing_params" : {
            "within_unit_overlap_window" : 0.000166,
            "between_unit_overlap_window" : 0.000166,
            "between_unit_overlap_distance" : 5
        },

        "mean_waveform_params" : {
            "samples_per_spike" : 82,
            "pre_samples" : 20,
            "num_epochs" : 1,
            "spikes_per_epoch" : 500,
            "spread_threshold" : 0.12,
            "site_range" : 16
        },

        "noise_waveform_params" : {
            "classifier_path" : os.path.join(os.getcwd(), 'ecephys_spike_sorting', 'modules', 'noise_templates', 'rf_classifier.pkl')

        },

        "quality_metrics_params" : {
            "isi_threshold" : 0.0015,
            "min_isi" : 0.000166,
            "num_channels_to_compare" : 13,
            "max_spikes_for_unit" : 500,
            "max_spikes_for_nn" : 10000,
            "n_neighbors" : 4,
            "quality_metrics_output_file" : os.path.join(kilosort_output_directory, "new_metrics.csv")
        }

    }

    with io.open(output_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(dictionary, ensure_ascii=False, sort_keys=True, indent=4))

    return dictionary