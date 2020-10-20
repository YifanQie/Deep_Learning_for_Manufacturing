""" The model train file trains the model on the download dataset and other parameters specified in the assemblyconfig file
The main function runs the training and populates the created file structure with the trained model, logs and plots
"""

import os
import sys
current_path=os.path.dirname(__file__)
parentdir = os.path.dirname(current_path)

os.environ["CUDA_VISIBLE_DEVICES"]="0" # Nvidia Quadro GV100
#os.environ["CUDA_VISIBLE_DEVICES"]="1" # Nvidia Quadro M2000

#Adding Path to various Modules
sys.path.append("../core")
sys.path.append("../visualization")
sys.path.append("../utilities")
sys.path.append("../datasets")
sys.path.append("../trained_models")
sys.path.append("../config")
#path_var=os.path.join(os.path.dirname(__file__),"../utilities")
#sys.path.append(path_var)
#sys.path.insert(0,parentdir) 

#Importing Required Modules
import pathlib
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import backend as K
K.clear_session()

#Importing Config files
import assembly_config as config
import model_config as cftrain
import hybrid_utils as hy_util
#Importing required modules from the package
from measurement_system import HexagonWlsScanner
from assembly_system import VRMSimulationModel
from wls400a_system import GetInferenceData
from data_import import GetTrainData
from core_model_bayes import Bayes_DLModel
from training_viz import TrainViz
from metrics_eval import MetricsEval
from keras_lr_multiplier import LRMultiplier

class Unet_TrainModel:
	def __init__(self,batch_size,epochs,split_ratio):
			self.batch_size=batch_size
			self.epochs=epochs
			self.split_ratio=split_ratio
			

	def bayes_unet_run_train_model(self,model,X_in,Y_out_list,X_in_test,Y_out_test_list,model_path,logs_path,plots_path,activate_tensorboard=0,run_id=0,tl_type='full_fine_tune'):
		"""run_train_model function trains the model on the dataset and saves the trained model,logs and plots within the file structure, the function prints the training evaluation metrics
			
			:param model: 3D CNN model compiled within the Deep Learning Class, refer https://keras.io/models/model/ for more information 
			:type model: keras.models (required)

			:param X_in: Train dataset input (predictor variables), 3D Voxel representation of the cloud of point and node deviation data obtained from the VRM software based on the sampling input
			:type X_in: numpy.array [samples*voxel_dim*voxel_dim*voxel_dim*deviation_channels] (required)
			
			:param Y_out: Train dataset output (variables to predict), Process Parameters/KCCs obtained from sampling
			:type Y_out: numpy.array [samples*assembly_kccs] (required)

			:param model_path: model path at which the trained model is saved
			:type model_path: str (required)
			
			:param logs_path: logs path where the training metrics file is saved
			:type logs_path: str (required)

			:param plots_path: plots path where model training loss convergence plot is saved
			:type plots_path: str (required)

			:param activate_tensorboard: flag to indicate if tensorboard should be added in model callbacks for better visualization, 0 by default, set to 1 to activate tensorboard
			:type activate_tensorboard: int

			:param run_id: Run id index used in data study to conduct multiple training runs with different dataset sizes, defaults to 0
			:type run_id: int			
		"""			
		import tensorflow as tf
		from tensorflow.keras.models import load_model
		import tensorflow.keras.backend as K 
		#model_file_path=model_path+'/unet_trained_model_'+str(run_id)+'.h5'
		model_file_path=model_path+'/unet_oser_'+str(run_id)

		from tensorflow.keras.callbacks import Callback, EarlyStopping, LearningRateScheduler, ModelCheckpoint
		
		# #Decrease Learning Rate
		# def schedule(epoch, initial_learning_rate, lr_decay_start_epoch):
		#     """Defines exponentially decaying learning rate."""

		#     if epoch < lr_decay_start_epoch:
		#         return initial_learning_rate
		#     else:
		#         return initial_learning_rate * math.exp((10 * initial_learning_rate) * (lr_decay_start_epoch - epoch))

		# scheduler = LearningRateScheduler(schedule)

		# #Annealing the Learning Rate
		# class AnnealingCallback(Callback):
		   
		#     def __init__(self, kl_alpha, kl_start_epoch, kl_alpha_increase_per_epoch):
		#         self.kl_alpha = kl_alpha
		#         self.kl_start_epoch = kl_start_epoch
		#         self.kl_alpha_increase_per_epoch = kl_alpha_increase_per_epoch
		    
		#     def on_epoch_end(self, epoch, logs={}):
		#         if epoch >= self.kl_start_epoch - 2:
		#             new_kl_alpha = min(K.get_value(self.kl_alpha) + self.kl_alpha_increase_per_epoch, 1.)
		#             K.set_value(self.kl_alpha, new_kl_alpha)
		#         print ("Current KL Weight is " + str(K.get_value(self.kl_alpha)))

		#tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir='C:\\Users\\sinha_s\\Desktop\\dlmfg_package\\dlmfg\\trained_models\\inner_rf_assembly\\logs',histogram_freq=1)
		checkpointer = tf.keras.callbacks.ModelCheckpoint(model_file_path, verbose=1, save_best_only='val_loss',save_weights_only=True)
		#Check pointer to save the best model
		
		val_steps=X_in_test[0].shape[0]//self.batch_size
		
		history=model.fit(x=X_in,y=Y_out_list, validation_data=(X_in_test,Y_out_test_list),validation_steps=val_steps, epochs=self.epochs, batch_size=self.batch_size,callbacks=[checkpointer])
		
		return model

		
if __name__ == '__main__':

	print('Parsing from Assembly Config File....')

	data_type=config.assembly_system['data_type']
	application=config.assembly_system['application']
	part_type=config.assembly_system['part_type']
	part_name=config.assembly_system['part_name']
	data_format=config.assembly_system['data_format']
	assembly_type=config.assembly_system['assembly_type']
	assembly_kccs=config.assembly_system['assembly_kccs']	
	assembly_kpis=config.assembly_system['assembly_kpis']
	voxel_dim=config.assembly_system['voxel_dim']
	point_dim=config.assembly_system['point_dim']
	voxel_channels=config.assembly_system['voxel_channels']
	noise_type=config.assembly_system['noise_type']
	mapping_index=config.assembly_system['mapping_index']

	system_noise=config.assembly_system['system_noise']
	aritifical_noise=config.assembly_system['aritifical_noise']
	data_folder=config.assembly_system['data_folder']
	kcc_folder=config.assembly_system['kcc_folder']
	kcc_files=config.assembly_system['kcc_files']
	test_kcc_files=config.assembly_system['test_kcc_files']

	#added for hybrid model
	categorical_kccs=config.assembly_system['categorical_kccs']
	
	print('Parsing from Training Config File')

	model_type=cftrain.model_parameters['model_type']
	output_type=cftrain.model_parameters['output_type']
	batch_size=cftrain.model_parameters['batch_size']
	epocs=cftrain.model_parameters['epocs']
	split_ratio=cftrain.model_parameters['split_ratio']
	optimizer=cftrain.model_parameters['optimizer']
	loss_func=cftrain.model_parameters['loss_func']
	regularizer_coeff=cftrain.model_parameters['regularizer_coeff']
	activate_tensorboard=cftrain.model_parameters['activate_tensorboard']
	
	print('Creating file Structure....')
	
	folder_name=part_type
	train_path='../trained_models/'+part_type
	pathlib.Path(train_path).mkdir(parents=True, exist_ok=True) 

	train_path=train_path+'/unet_model_bayes_hybrid'
	pathlib.Path(train_path).mkdir(parents=True, exist_ok=True) 

	model_path=train_path+'/model'
	pathlib.Path(model_path).mkdir(parents=True, exist_ok=True)
	
	logs_path=train_path+'/logs'
	pathlib.Path(logs_path).mkdir(parents=True, exist_ok=True)

	plots_path=train_path+'/plots'
	pathlib.Path(plots_path).mkdir(parents=True, exist_ok=True)

	deployment_path=train_path+'/deploy'
	pathlib.Path(deployment_path).mkdir(parents=True, exist_ok=True)

	#Objects of Measurement System, Assembly System, Get Inference Data
	print('Initializing the Assembly System and Measurement System....')

	measurement_system=HexagonWlsScanner(data_type,application,system_noise,part_type,data_format)
	vrm_system=VRMSimulationModel(assembly_type,assembly_kccs,assembly_kpis,part_name,part_type,voxel_dim,voxel_channels,point_dim,aritifical_noise)
	get_data=GetTrainData()

	#print(input_conv_data.shape,kcc_subset_dump.shape)
	print('Building Unet Model')

	kcc_sublist=cftrain.encode_decode_params['kcc_sublist']
	output_heads=cftrain.encode_decode_params['output_heads']
	encode_decode_multi_output_construct=config.encode_decode_multi_output_construct
	
	if(output_heads==len(encode_decode_multi_output_construct)):
		print("Valid Output Stages and heads")
	else:
		print("Inconsistent model setting")

	print("KCC sub-listing: ",kcc_sublist)
	
	#Check for KCC sub-listing
	if(kcc_sublist!=0):
		output_dimension=len(kcc_sublist)
	else:
		output_dimension=assembly_kccs
	
	print("Process Parameter Dimension: ",output_dimension)

	input_size=(voxel_dim,voxel_dim,voxel_dim,voxel_channels)

	model_depth=cftrain.encode_decode_params['model_depth']
	inital_filter_dim=cftrain.encode_decode_params['inital_filter_dim']

	dl_model=Bayes_DLModel(model_type,output_dimension,optimizer,loss_func,regularizer_coeff,output_type)
	
	#changed to attention model
	model=dl_model.bayes_unet_model_3d_hybrid(inital_filter_dim,model_depth,categorical_kccs,voxel_dim,voxel_channels,output_heads)

	print(model.summary())
	#sys.exit()
	
	#importing file names for model input
	input_file_names_x=config.encode_decode_construct['input_data_files_x']
	input_file_names_y=config.encode_decode_construct['input_data_files_y']
	input_file_names_z=config.encode_decode_construct['input_data_files_z']

	test_input_file_names_x=config.encode_decode_construct['input_test_data_files_x']
	test_input_file_names_y=config.encode_decode_construct['input_test_data_files_y']
	test_input_file_names_z=config.encode_decode_construct['input_test_data_files_z']


	if(activate_tensorboard==1):
		tensorboard_str='tensorboard' + '--logdir '+logs_path
		print('Visualize at Tensorboard using ', tensorboard_str)
	
	print('Importing and Preprocessing Cloud-of-Point Data')
	
	point_index=get_data.load_mapping_index(mapping_index)
	
	input_dataset=[]
	input_dataset.append(get_data.data_import(input_file_names_x,data_folder))
	input_dataset.append(get_data.data_import(input_file_names_y,data_folder))
	input_dataset.append(get_data.data_import(input_file_names_z,data_folder))
	
	test_input_dataset=[]
	test_input_dataset.append(get_data.data_import(test_input_file_names_x,data_folder))
	test_input_dataset.append(get_data.data_import(test_input_file_names_y,data_folder))
	test_input_dataset.append(get_data.data_import(test_input_file_names_z,data_folder))


	kcc_dataset=get_data.data_import(kcc_files,kcc_folder)
	test_kcc_dataset=get_data.data_import(test_kcc_files,kcc_folder)
	
	if(kcc_sublist!=0):
		print("Sub-setting Process Parameters: ",kcc_sublist)
		kcc_dataset=kcc_dataset.iloc[:,kcc_sublist]
		test_kcc_dataset=test_kcc_dataset[:,kcc_sublist]
	else:
		print("Using all Process Parameters")
	
	#Pre-processing to point cloud data
	convergent_train=[]
	convergent_test=[]

	#Pre-processing to point cloud data
	input_conv_data, kcc_subset_dump,kpi_subset_dump=get_data.data_convert_voxel_mc(vrm_system,input_dataset,point_index,kcc_dataset)
	test_input_conv_data, test_kcc_subset_dump,test_kpi_subset_dump=get_data.data_convert_voxel_mc(vrm_system,test_input_dataset,point_index,test_kcc_dataset)

	convergent_train.append(kpi_subset_dump)
	convergent_test.append(test_kpi_subset_dump)

	
	y_shape_error_list=[]
	y_shape_error_test_list=[]

	for encode_decode_construct in encode_decode_multi_output_construct:
		#importing file names for model output
		print("Importing output data for stage: ",encode_decode_construct)
		
		output_file_names_x=encode_decode_construct['output_data_files_x']
		output_file_names_y=encode_decode_construct['output_data_files_y']
		output_file_names_z=encode_decode_construct['output_data_files_z']

		test_output_file_names_x=encode_decode_construct['output_test_data_files_x']
		test_output_file_names_y=encode_decode_construct['output_test_data_files_y']
		test_output_file_names_z=encode_decode_construct['output_test_data_files_z']

		output_dataset=[]
		output_dataset.append(get_data.data_import(output_file_names_x,data_folder))
		output_dataset.append(get_data.data_import(output_file_names_y,data_folder))
		output_dataset.append(get_data.data_import(output_file_names_z,data_folder))
	
		test_output_dataset=[]
		test_output_dataset.append(get_data.data_import(test_output_file_names_x,data_folder))
		test_output_dataset.append(get_data.data_import(test_output_file_names_y,data_folder))
		test_output_dataset.append(get_data.data_import(test_output_file_names_z,data_folder))
		
		output_conv_data, kcc_subset_dump,kpi_subset_dump=get_data.data_convert_voxel_mc(vrm_system,output_dataset,point_index,kcc_dataset)
		test_output_conv_data, test_kcc_subset_dump,test_kpi_subset_dump=get_data.data_convert_voxel_mc(vrm_system,test_output_dataset,point_index,test_kcc_dataset)
		
		convergent_train.append(kpi_subset_dump)
		convergent_test.append(test_kpi_subset_dump)

		y_shape_error_list.append(output_conv_data)
		y_shape_error_test_list.append(test_output_conv_data)

	convergent_ids_train=list(set(convergent_train[0]).intersection(*convergent_train))
	convergent_ids_test=list(set(convergent_train[0]).intersection(*convergent_test))

	del output_dataset
	del input_dataset

	print("Convergent Train Samples: ", len(convergent_ids_train))
	print("Convergent Test Samples: ", len(convergent_ids_test))

	shape_error=np.concatenate(y_shape_error_list, axis=4)
	shape_error_test=np.concatenate(y_shape_error_test_list, axis=4)

	del y_shape_error_list

	#Collect Only Convergent Samples
	shape_error=shape_error[convergent_ids_train,:,:,:,:]
	shape_error_test=shape_error_test[convergent_ids_test,:,:,:,:]
	
	input_conv_data=input_conv_data[convergent_ids_train,:,:,:,:]
	test_input_conv_data=test_input_conv_data[convergent_ids_test,:,:,:,:]

	kcc_subset_dump=kcc_subset_dump[convergent_ids_train,:]
	test_kcc_subset_dump=test_kcc_subset_dump[convergent_ids_test,:]
	
	#Create IO list
	kcc_regression,kcc_classification=hy_util.split_kcc(kcc_subset_dump)
	kcc_regression_test,kcc_classification_test=hy_util.split_kcc(test_kcc_subset_dump)

	Y_out_list=[]
	Y_out_list.append(kcc_regression)
	Y_out_list.append(kcc_classification)
	Y_out_test_list=[]
	Y_out_test_list.append(kcc_regression_test)
	Y_out_test_list.append(kcc_classification_test)
	
	Y_out_list.append(shape_error)
	Y_out_test_list.append(shape_error_test)

	unet_train_model=Unet_TrainModel(batch_size,epocs,split_ratio)
	
	trained_model=unet_train_model.bayes_unet_run_train_model(model,input_conv_data,Y_out_list,test_input_conv_data,Y_out_test_list,model_path,logs_path,plots_path,activate_tensorboard)
	
	print("Model Training Complete..")
	