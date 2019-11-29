
model_parameters = {	
        'model_type':'3D Convolutional Neural Network',
        'output_type':'regression',
        'batch_size': 32,
        'epocs': 150,
        'split_ratio': 0.3,
        'optimizer':'adam',
        'loss_func':'mse',
        'regularizer_coeff': 0.01,
        'activate_tensorboard':0
        }

data_study_params = {
	'batch_size':32,
	'epocs':5,
	'no_of_splits':10,
	'min_train_samples':50,
	'split_ratio':0.2
}

kmc_params={
        'tree_based_model':'xgb',
        'importance_creteria':'gini',
        'split_ratio':0.2,
        'save_model':1,
        'plot_kmc':1,
        'kcc_tplot':['KCC_1','KCC_3']

}