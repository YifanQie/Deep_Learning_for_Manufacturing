"""The Sampling configuration file consists of the parameters which conducting adaptive sampling/active learning from the VRM system 
                
        :param sampling_config['sample_dim']: Initial set (number) of KCC values to be generated to be sent to VRM for deviation pattern simulation
        :type sampling_config['sample_dim']: int (required)

        :param sampling_config['adaptive_sample_dim']: Consecutive adaptive set (number) of KCC values to be generated to be sent to VRM for deviation pattern simulation
        :type sampling_config['adaptive_sample_dim']: int (required)

        :param sampling_config['adaptive_runs']: Number of adaptive runs to conducted used as a terminating criteria for active learning
        :type sampling_config['adaptive_runs']: int (required)

        :param sampling_config['sample_type']: Initial sampling strategy uniform or LHS (Latin Hypercube Sampling), defaults to LHS
        :type sampling_config['sample_type']: str (required)

        :param sampling_config['sample_type']: The output filename of the generated samples to be used as input for the VRM software
        :type sampling_config['sample_type']: str (required)

"""

sampling_config={'sample_dim':2000,
                'test_sample_dim':10,
                'sample_validation_dim':100,
		'adaptive_sample_dim':50,
		'adaptive_runs':5,
                'num_mix':3,
                'weight':0.5,
                'decay_factor':0.1,
                'pp_masking':0,	
                'output_folder_name':'cross_member_assembly',
                'sample_type':'uniform',
                'output_file_name':'cross_member_samples_datagen_hybrid_5',
                'output_file_name_test':'cross_member_samples_dynamic_test_0',
                'output_file_name_validate':'cross_member_samples_dynamic_validate_0',
                'output_file_name_train': 'cross_member_samples_dynamic_train',
                'datagen_filename_x':'DX_crossmember_datagen_dynamic_11_',
                'datagen_filename_y':'DY_crossmember_datagen_dynamic_11_',
                'datagen_filename_z':'DZ_crossmember_datagen_dynamic_11_',
        }