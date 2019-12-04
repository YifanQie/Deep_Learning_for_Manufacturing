
#tensorbaord is added as call back to model training
#start tensorboard from terminal/cmd window using tensorboard --logdir ./logs

class TrainViz:

	def training_plot(self, history,plots_path,run_id=0):

		import matplotlib.pyplot as plt
		
		#summarize history for Mean Absolute Error
		# plt.plot(history.history['mae'])
		# plt.plot(history.history['val_mae'])
		# plt.title('model MAE`')
		# plt.ylabel('MAE')
		# plt.xlabel('epoch')
		# plt.legend(['train', 'test'], loc='upper left')
		# plt.savefig(plots_path+'/'+'accuracy_'+str(run_id)+'.png')
		# plt.clf()

		# summarize history for loss
		plt.plot(history.history['loss'])
		plt.plot(history.history['val_loss'])
		plt.title('model loss')
		plt.ylabel('loss')
		plt.xlabel('epoch')
		plt.legend(['train', 'test'], loc='upper left')
		plt.savefig(plots_path+'/'+'loss_'+str(run_id)+'.png')
		plt.clf()