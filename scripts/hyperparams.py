# Parameters
learning_rate = 0.00001
training_iters = 25000
batch_size = 1
display_step = 10 #while training every 10 epochs print
dropout=0.7
# Network Parameters
n_steps=20 # no of time steps of imu data and for rnn 
n_input = 6 # imu (linear acc and ang vel) (20 readings of imu *6 channels) +7 (vicon prev pose)
n_hidden = 256 # hidden layer num of features for lstm cell
n_output = 7 # position and quaternion

# if train or use trained model
is_train=False
if(is_train):
	load_model=False
else:
	load_model=True
# create tf records or read already created ones
create_tfrecords= False
input_Dir='./records/'

using_cluster=False #to create port on cluster and to visualize
compute='0-9'

eps = 1e-6
do_zero_motion=False
