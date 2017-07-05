import tensorflow as tf
from io_libs.reader import read_tfrecords
import os
from scripts.lstm import *
import numpy as np
from io_libs.writer import *
from scripts.hyperparams import *

if __name__=="__main__":
	if(create_tfrecords):
		write_tfrecords()
	nRecords= len([name for name in os.listdir(input_Dir) if os.path.isfile(os.path.join(input_Dir, name))])
	print 'found %d records' % nRecords
	train_dataset = [input_Dir+'/sample_'+ str(i)+'.tfrecord' for i in range(1,int(nRecords*0.75))]
	validation_dataset = [input_Dir+'/sample_'+ str(i)+'.tfrecord' for i in range(int(nRecords*0.75),nRecords)]
	train_data = tf.train.string_input_producer(train_dataset, shuffle=True)
	validation_data = tf.train.string_input_producer(validation_dataset, shuffle=True)

	imu_t,rel_pose_t,imu_len_t=read_tfrecords(train_data)
	imu_t,rel_pose_t,imu_len_t = tf.train.batch([imu_t,rel_pose_t,imu_len_t],batch_size=batch_size)
	rel_pose_t = tf.reshape(rel_pose_t,[batch_size, 7])
        
	imu_v,rel_pose_v,imu_len_v=read_tfrecords(validation_data)
	imu_v,rel_pose_v,imu_len_v = tf.train.batch([imu_v,rel_pose_v,imu_len_v],batch_size=batch_size)
	rel_pose_v = tf.reshape(rel_pose_v,[batch_size, 7])    

	init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
	writer_t = tf.summary.FileWriter('./graphs/train', None)
	writer_v = tf.summary.FileWriter('./graphs/validation', None)
	writer_t_z = tf.summary.FileWriter('./graphs/train_zero', None)
	writer_v_z = tf.summary.FileWriter('./graphs/validation_zero', None)
    
	# Add ops to save and restore all the variables.
	saver = tf.train.Saver()
	with tf.Session()  as sess:	
		sess.run(init_op)
		coord = tf.train.Coordinator()
		threads = tf.train.start_queue_runners(coord=coord)
		if(is_train):
			step = 1
			# Keep training until reach max iterations
			while step * batch_size < training_iters:
				global do_zero_motion
				batch_x, batch_y, imu_len_ = sess.run([imu_t,rel_pose_t,imu_len_t])
				# Run optimization op (backprop)
				if not do_zero_motion:
					[opt, train_loss, summ] = sess.run([optimizer, cost, summary], feed_dict={x: batch_x, y: batch_y})
					writer_t.add_summary(summ,step)
				#zero loss summary for train dataset
				else:
					[t_z_loss,summ] = sess.run([cost,summary],feed_dict={x: batch_x, y: batch_y})
					writer_t_z.add_summary(summ,step)
				# writer.flush()
				#validation on different batch
				batch_x, batch_y, imu_len_ = sess.run([imu_v,rel_pose_v,imu_len_v])
				if not do_zero_motion:
					[pred_,val_loss, summ] = sess.run([pred,cost, summary], feed_dict={x: batch_x, y: batch_y})
					writer_v.add_summary(summ,step)
					if step % display_step == 0:
						print("Iter " + str(step*batch_size) + ", Minibatch Loss= " + \
						      "{:.6f}".format(train_loss)+" Validation loss= ""{:.6f}".format(val_loss))
				#zero loss summary for validation dataset
				else:
					[v_z_loss,summ] = sess.run([cost,summary],feed_dict={x: batch_x, y: batch_y})
					writer_v_z.add_summary(summ,step)
					print(step)
				step += 1
			print("Optimization Finished!")
			# Save the variables to disk.	
			save_path = saver.save(sess, "./tmp/model.ckpt")
			print("Model saved in file: %s" % save_path)
		else:
		  # Restore variables from disk.
			saver.restore(sess, "./tmp/model.ckpt")
			print("Model restored.")
			# for i in range(1,1000):
			# 	print(i)
			# 	batch_x_v, batch_y_v,imu_len_=sess.run([imu_v,rel_pose_v,imu_len_v])
			# 	batch_y_v = batch_y_v.reshape((batch_size, 7))
			# 	summary3=sess.run(write_op3, feed_dict={x: batch_x_v, y: batch_y_v})
			# 	print(sess.run(Ti12, feed_dict={x: batch_x_v, y: batch_y_v}))
			# 	writer_3.add_summary(summary3,i)
			# 	writer_3.flush()
			# print("Done")
	coord.request_stop()
	coord.join(threads)
	# if (using_cluster):
	# 	import os
	# 	os.system('tensorboard --port=1234 --logdir="./graphs/" && exit && cd && ssh -N -4 -L :1234:localhost:1234 compute-0-9;')
