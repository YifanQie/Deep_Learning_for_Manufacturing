""" Contains core classes and methods for initializing the deep learning 3D CNN model with different variants of the loss function, inputs are provided from the modelconfig_train.py file"""

class DLModel:	
	""" Deep Learning Model Class

		:param model_type: Type of model to be used for training 3D CNN with MSE loss, 3D CNN with hetreoskedastic aleatoric loss, 3D CNN with a mixture density network (GMM) output
		:type model_type: str (required)

		:param output_dimension: Number of output nodes for the network equal to number of KCCs for the assembly in case MSE is used as loss function
		:type output_dimension: int (required)

		:param optimizer: The optimizer to be used while model training, refer: https://keras.io/optimizers/ for more information
		:type optimizer: keras.optimizer (required) 

		:param loss_function: The loss function to be optimized by training the model, refer: https://keras.io/losses/ for more information
		:type loss_function: keras.losses (required)

		:param regularizer_coeff: The L2 norm regularization coefficient value used in the penultimate fully connected layer of the model, refer: https://keras.io/regularizers/ for more information
		:type regularizer_coeff: float (required)

		:param output_type: The output type of the model which can be regression or classification, this is used to define the output layer of the model, defaults to regression (classification: softmax, regression: linear)
		:type output_type: str		

	"""
	def __init__(self,model_type,output_dimension,optimizer,loss_function,regularizer_coeff,output_type='regression'):
		self.output_dimension=output_dimension
		self.model_type=model_type
		self.optimizer=optimizer
		self.loss_function=loss_function
		self.regularizer_coeff=regularizer_coeff
		self.output_type=output_type

	def cnn_model_3d(self,voxel_dim,deviation_channels):
		"""Build the 3D Model using the specified loss function, the inputs are parsed from the assemblyconfig_<case_study_name>.py file

			:param voxel_dim: The voxel dimension of the input, required to build input to the 3D CNN model
			:type voxel_dim: int (required)

			:param voxel_channels: The number of voxel channels in the input structure, required to build input to the 3D CNN model
			:type voxel_channels: int (required)
		"""
		from tensorflow.keras.layers import Conv3D, MaxPool3D, Flatten, Dense, Dropout
		from tensorflow.keras.models import Sequential
		from tensorflow.keras import regularizers

		if(self.output_type=="regression"):
			final_layer_avt='linear'

		if(self.output_type=="classification"):
			final_layer_avt='softmax'

		model = Sequential()
		model.add(Conv3D(32, kernel_size=(5,5,5),strides=(2,2,2),activation='relu',input_shape=(voxel_dim,voxel_dim,voxel_dim,deviation_channels)))
		model.add(Conv3D(32, kernel_size=(4,4,4),strides=(2,2,2),activation='relu'))
		model.add(Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),activation='relu'))
		model.add(MaxPool3D(pool_size=(2,2,2)))
		model.add(Flatten())
		model.add(Dense(64,kernel_regularizer=regularizers.l2(self.regularizer_coeff),activation='relu'))
		#model.add(Dropout(0.2))
		model.add(Dense(64,kernel_regularizer=regularizers.l2(self.regularizer_coeff),activation='relu'))
		model.add(Dense(self.output_dimension, activation=final_layer_avt))
		model.compile(loss=self.loss_function, optimizer=self.optimizer, metrics=['mae'])

		print("3D CNN model successfully compiled")
		return model

	def resnet_3d_cnn(self,voxel_dim,deviation_channels,w_val=0):

		import numpy as np
		import tensorflow.keras.backend as K 
		from tensorflow.keras.models import Model
		from tensorflow.keras import regularizers
		from tensorflow.keras.layers import Conv3D, MaxPooling3D, Add, BatchNormalization, Input, LeakyReLU,Activation, Lambda, Concatenate, Flatten, Dense,UpSampling3D,GlobalAveragePooling3D

		if(w_val==0):
			w_val=np.zeros(self.output_dimension)
			w_val[:]=1/self.output_dimension


		def weighted_mse(val):
			def loss(yTrue,yPred):

				#val = np.array([0.1,0.1,0.1,0.1,0.1]) 
				w_var = K.variable(value=val, dtype='float32', 
											 name='weight_vec')
				#weight_vec = K.ones_like(yTrue[0,:]) #a simple vector with ones shaped as (60,)
				#idx = K.cumsum(ones) #similar to a 'range(1,61)'

				return K.mean((w_var)*K.square(yTrue-yPred))
			return loss

		input_size=(voxel_dim,voxel_dim,voxel_dim,deviation_channels)
		inputs = Input(input_size)
		x = inputs
		y = Conv3D(32, kernel_size=(4,4,4),strides=(2,2,2), name="conv_block_1")(x)
		res1=y
		
		y = LeakyReLU()(y)
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1), padding='same',name="conv_block_2")(y)
		y = LeakyReLU()(y)
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1), padding='same',name="conv_block_3")(y)
		y = Add()([res1, y])
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(2,2,2), name="conv_block_4")(y)
		res2=y
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1), padding='same',name="conv_block_5")(y)
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1), padding='same',name="conv_block_6")(y)
		y = Add()([res2, y])
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(2,2,2), name="conv_block_7")(y)
		res3=y
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),padding='same', name="conv_block_8")(y)
		y = LeakyReLU()(y)
		
		y = Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),padding='same', name="conv_block_9")(y)
		
		y = Add()([res3, y])
		y = LeakyReLU()(y)
		
		y=Flatten()(y)
		
		y=Dense(128,kernel_regularizer=regularizers.l2(self.regularizer_coeff),activation='relu')(y)
		y=Dense(64,kernel_regularizer=regularizers.l2(self.regularizer_coeff),activation='relu')(y)
		output=Dense(self.output_dimension)(y)
		
		model=Model(inputs, outputs=output, name='Res_3D_CNN')
		
		model.compile(loss=self.loss_function, optimizer=self.optimizer, metrics=['mae'])
		
		#print(model.summary())
		
		return model

	
		
	def cnn_model_3d_tl(self,voxel_dim,deviation_channels):
		"""Build the 3D Model with GlobalMAxPooling3D instead of flatten, this enables input for different voxel dimensions, to be used when the model needs to be leveraged for transfer learning with different size input

			:param voxel_dim: The voxel dimension of the input, required to build input to the 3D CNN model
			:type voxel_dim: int (required)

			:param voxel_channels: The number of voxel channels in the input structure, required to build input to the 3D CNN model
			:type voxel_channels: int (required)
		"""
		from tensorflow.keras.layers import Conv3D, MaxPool3D, Flatten, Dense, Dropout, Input
		from tensorflow.keras.models import Model
		from tensorflow.keras import regularizers

		inputs = Input(shape=(None,None,None,3,))
		cnn3d_1=Conv3D(32, kernel_size=(5,5,5),strides=(2,2,2),activation='relu')(inputs)
		cnn3d_2=Conv3D(32, kernel_size=(4,4,4),strides=(2,2,2),activation='relu')(cnn3d_1)
		cnn3d_3=Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),activation='relu')(cnn3d_2)
		max_pool3d=MaxPool3D(pool_size=(2,2,2))(cnn3d_3)
		pooled_layer=GlobalMaxPooling3D()(max_pool3d)
		dense_1=Dense(128,kernel_regularizer=regularizers.l2(self.regularizer_coeff),activation='relu')(pooled_layer)
		predictions=Dense(self.output_dimension, activation=final_layer_avt)(dense_1)
		model = Model(inputs=inputs, outputs=predictions)

		model.compile(loss=self.loss_function, optimizer=self.optimizer, metrics=['mae'])
		
		return model

	def cnn_model_3d_aleatoric(self,voxel_dim,deviation_channels):
		"""Build the 3D Model with a heteroeskedastic aleatoric loss, this enables different standard deviation of each predicted value, to be used when the expected sensor noise is heteroskedastic

			:param voxel_dim: The voxel dimension of the input, required to build input to the 3D CNN model
			:type voxel_dim: int (required)

			:param voxel_channels: The number of voxel channels in the input structure, required to build input to the 3D CNN model
			:type voxel_channels: int (required)
		"""
		if(self.model_type=="regression"):
			final_layer_avt='linear'

		if(self.model_type=="classification"):
			final_layer_avt='softmax'

		def myloss(y_true, y_pred):
			prediction = y_pred[:,0:self.output_dimension]
			log_variance = y_pred[:,self.output_dimension:self.output_dimension+1]
			loss = tf.reduce_mean(0.5 * tf.exp(-1 * log_variance) * tf.square(tf.abs(y_true - prediction))+ 0.5 * log_variance)
			return loss
		
		from tensorflow.keras.layers import Conv3D, MaxPool3D, Flatten, Dense
		from tensorflow.keras.models import Sequential

		model = Sequential()
		model.add(Conv3D(32, kernel_size=(5,5,5),strides=(2,2,2),activation='relu',input_shape=(voxel_dim,voxel_dim,voxel_dim,deviation_channels)))
		model.add(Conv3D(32, kernel_size=(4,4,4),strides=(2,2,2),activation='relu'))
		model.add(Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),activation='relu'))
		model.add(MaxPool3D(pool_size=(2,2,2)))
		model.add(Flatten())
		model.add(Dense(128,kernel_regularizer=regularizers.l2(0.02),activation='relu'))
		#model.add(Dropout(0.3))
		model.add(Dense(self.output_dimension, activation=final_layer_avt))
		model.compile(loss=myloss, optimizer='adam', metrics=['mae'])

		print("3D CNN model Aleatoric successfully compiled")
		return model

	def cnn_model_3d_mdn(self,voxel_dim,deviation_channels,num_of_mixtures=5):
		"""Build the 3D Model with a Mixture Density Network output the gives parameters of a Gaussian Mixture Model as output, to be used if the system is expected to be collinear (Multi-Stage Assembly Systems) i.e. a single input can have multiple outputs
			Functions for predicting and sampling from a MDN.py need to used when deploying a MDN based model
			refer https://publications.aston.ac.uk/id/eprint/373/1/NCRG_94_004.pdf for more details on the working of a MDN model
			refer https://arxiv.org/pdf/1709.02249.pdf to understand how a MDN model can be leveraged to estimate the epistemic and aleatoric unceratninty present in manufacturing sytems based on the data collected

			:param voxel_dim: The voxel dimension of the input, reuired to build input to the 3D CNN model
			:type voxel_dim: int (required)

			:param voxel_channels: The number of voxel channels in the input structure, required to build input to the 3D CNN model
			:type voxel_channels: int (required)

			:param number_of_mixtures: The number of mixtures in the Gaussian Mixture Model output, defaults to 5, can be increased if higher collinearity is expected
			:type number_of_mixtures: int
		"""

		assert self.model_type=="regression","Mixture Density Network Should be a Regression Model"
		
		from tensorflow.keras.layers import Conv3D, MaxPool3D, Flatten, Dense
		from tensorflow.keras.models import Sequential
		import mdn

		model = Sequential()
		model.add(Conv3D(32, kernel_size=(5,5,5),strides=(2,2,2),activation='relu',input_shape=(voxel_dim,voxel_dim,voxel_dim,deviation_channels)))
		model.add(Conv3D(32, kernel_size=(4,4,4),strides=(2,2,2),activation='relu'))
		model.add(Conv3D(32, kernel_size=(3,3,3),strides=(1,1,1),activation='relu'))
		model.add(MaxPool3D(pool_size=(2,2,2)))
		model.add(Flatten())
		model.add(Dense(128,kernel_regularizer=regularizers.l2(0.02),activation='relu'))
		#model.add(Dropout(0.3))
		model.add(Dense(self.output_dimension, activation=final_layer_avt))
		model.add(mdn.MDN(self.output_dimension, num_of_mixtures))
		model.compile(loss=mdn.get_mixture_loss_func(self.output_dimension,num_of_mixtures), optimizer='adam')

		print("3D CNN Mixture Density Network model successfully compiled")
		return model

if (__name__=="__main__"):
	print('Model Deep Learning Class')