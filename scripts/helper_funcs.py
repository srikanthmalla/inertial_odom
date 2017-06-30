import tensorflow as tf
from utils import *
#ref: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
def quat_to_euler(q):#tf array [qw,qx,qy,qz] as the data is in this format
	shape = q.get_shape()
	bs = int(shape[0])
	w=q[:,0]
	x=q[:,1]
	y=q[:,2]
	z=q[:,3]
	ysqr = y * y
	# roll (x-axis rotation)
	t0 = +2.0 * (w * x + y * z)
	t1 = +1.0 - 2.0 * (x * x + ysqr)
	roll =tf.reshape(atan2(t0, t1),[bs,1])

	# pitch (y-axis rotation)
	t2 = +2.0 * (w*y  - z * x)
	t2=tf.where(tf.greater(t2,1),tf.zeros_like(t2)+1,t2)
	t2=tf.where(tf.less(t2,-1),tf.zeros_like(t2)-1,t2)
	pitch = tf.reshape(tf.asin(t2),[bs,1])
	# yaw (z-axis rotation)
	t3 = +2.0 * (w * z + x * y)
	t4 = +1.0 - 2.0 * (ysqr + z * z)
	yaw = tf.reshape(atan2(t3, t4),[bs,1])
	return (roll,pitch,yaw)
#ref: https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles
def quat2rotmat(q):#tf array [qw,qx,qy,qz] as the data is in this format
	shape = q.get_shape()
	bs = int(shape[0])
	q0=q[:,0]
	q1=q[:,1]
	q2=q[:,2]
	q3=q[:,3]
	t1=tf.reshape((q0*q0)+(q1*q1)-(q2*q2)-(q3*q3),[bs,1])
	t2=tf.reshape(2.0*(q1*q2-q0*q3),[bs,1])
	t3=tf.reshape(2.0*(q0*q2+q1*q3),[bs,1])
	R1=tf.reshape(tf.concat([t1,t2,t3],1),[bs,1,3])
	t1=tf.reshape(2.0*(q1*q2+q0*q3),[bs,1])
	t2=tf.reshape((q0*q0)-(q1*q1)+(q2*q2)-(q3*q3),[bs,1])
	t3=tf.reshape(2.0*(q2*q3-q0*q1),[bs,1])
	R2=tf.reshape(tf.concat([t1,t2,t3],1),[bs,1,3])
	t1=tf.reshape(2.0*(q1*q3-q0*q2),[bs,1])
	t2=tf.reshape(2.0*(q0*q1+q2*q3),[bs,1])
	t3=tf.reshape((q0*q0)-(q1*q1)-(q2*q2)+(q3*q3),[bs,1])
	R3=tf.reshape(tf.concat([t1,t2,t3],1),[bs,1,3])
	R=tf.reshape(tf.concat([R1,R2,R3],1),[bs,3,3])	
	return R
	# R=tf.array([])
def pose2mat(p):
	shape = p.get_shape()
	bs = int(shape[0])
	q=p[:,3:7]
	t=tf.reshape(p[:,0:3],[bs,3])
	R=quat2rotmat(q)
	T=merge_rt(R,t)
	return T