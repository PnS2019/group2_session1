"""Logistic Regression for Fashion MNIST Binary Classification.

Group 2
"""
from __future__ import print_function, absolute_import

import numpy as np
import matplotlib.pyplot as plt

from tensorflow.keras import backend as K

from random import shuffle

from pnslib import utils
from pnslib import ml

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


# Load T-shirt/top and Trouser classes from Fashion MNIST
# complete label description is at
# https://github.com/zalandoresearch/fashion-mnist#labels

classes = {
    "Tshirt/top": 0,
    "Trouser": 1,
    "Pullover": 2,
    "Dress": 3,
    "Coat": 4,
    "Sandal": 5,
    "Shirt": 6,
    "Sneaker": 7,
    "Bag": 8,
    "Ankle boot": 9
}

labels = ["Tshirt/top", "Trouser"]

class_list = [classes[labels[0]], classes[labels[1]]]

(train_x, train_y, test_x, test_y) = utils.binary_fashion_mnist_load(
    class_list=class_list,
    flatten=True)

print("[MESSAGE] Dataset is loaded.")


# preprocessing for training and testing images
train_x = train_x.astype("float32") / 255.  # rescale image
mean_train_x = np.mean(train_x, axis=0)  # compute the mean across pixels
train_x -= mean_train_x  # remove the mean pixel value from image
test_x = test_x.astype("float32") / 255.
test_x -= mean_train_x

print("[MESSAGE] Dataset is preporcessed.")

# Use PCA to reduce the dimension of the dataset,
# so that the training will be less expensive
# perform PCA on training dataset
train_X, R, n_retained = ml.pca(train_x)

# perform PCA on testing dataset
test_X = ml.pca_fit(test_x, R, n_retained)

print("[MESSAGE] PCA is complete")

# sample sizes and feature dimensions
num_train_samples = train_X.shape[0]
num_test_samples = test_X.shape[0]
input_dim = train_X.shape[1]

# defining the batch size and epochs
batch_size = 64
num_epochs = 10

# defining the learning rate
lr = 0.1

# building the model

# defining the placeholders to feed the input and target data
input_tensor = K.placeholder(shape=(None, input_dim), dtype='float32')
target_tensor = K.placeholder(shape=(None, 1), dtype='float32')

# defining the weight and the bias variables
weight_variable = K.random_uniform_variable(shape=(input_dim, 1),
                                            low=-1., high=1.,
                                            dtype='float32')
bias_variable = K.zeros(shape=(1, ), dtype='float32')

# defining the sigmoid output tensor
output_tensor = K.dot(input_tensor, weight_variable) + bias_variable
output_tensor = K.sigmoid(output_tensor)

# defining the mean loss tensor
loss_tensor = K.mean(K.binary_crossentropy(target_tensor,
                                           output_tensor))

# getting the gradients of the mean loss with respect to the weight and bias
gradient_tensors = K.gradients(loss=loss_tensor, variables=[weight_variable,
                                                            bias_variable])

# creating the updates based on stochastic gradient descent rule
updates = [(weight_variable, weight_variable - lr * gradient_tensors[0]),
           (bias_variable, bias_variable - lr * gradient_tensors[1])]

# creating a training function which also updates the variables when the
# function is called based on the lists of updates provided
train_function = K.function(inputs=(input_tensor, target_tensor),
                            outputs=(loss_tensor,),
                            updates=updates)

# for logistic regression, the prediction is 1 if greater than 0.5 and 0
# if less
prediction_tensor = K.cast(K.greater(output_tensor, 0.5), dtype='float32')

# computing the accuracy based on how many prediction tensors equal the target
# tensors
accuracy_tensor = K.equal(prediction_tensor, target_tensor)

# a test function to evaluate the performance of the model
test_function = K.function(inputs=(input_tensor, target_tensor),
                           outputs=(accuracy_tensor, prediction_tensor))

# now you have to write a training loop which can loop over the data
# 10 (num_epochs) times in batches of size 64 (batch_size) and update the
# two variables in each batch in order to minimize the loss or cost function

############ WRITE YOUR CODE HERE #################

for epoch in range(num_epochs):
  permutation = np.random.permutation(num_train_samples)
  train_X = train_X[permutation]
  train_y = train_y[permutation]
  losses = np.array([])

  # Progress bar
  disp = "\rEpoch {epoch}: [{bar_1}>{bar_2}] "
  progess_len = 20
  print("Epoch {:<3} ".format(epoch), end="", flush=True)

  for batch in range(0, num_train_samples, batch_size):

    # Progress bar
    progress = progess_len * batch / num_train_samples
    bar_1 = "=" * int(progress)
    bar_2 = "." * (progess_len - len(bar_1) - 1)
    print(disp.format(epoch=epoch, bar_1=bar_1, bar_2=bar_2), end="", flush=True)

    start = batch
    end = min(batch + batch_size, len(train_X))

    batch_X = train_X[start: end]
    batch_y = train_y[start: end][:, np.newaxis]

    loss = train_function((batch_X, batch_y))[0]
    losses = np.append(losses, loss)

  acc, pred = test_function((test_X, np.expand_dims(test_y, axis=-1)))

  accuracy = np.count_nonzero(acc) / len(acc)

  #print(acc, pred)

  print("Loss - {:0.4}  Accuracy - {:0.4}".format(losses.mean(), accuracy))


############ YOUR CODE ABOVE THIS #################

# visualize the ground truth and prediction
# take first 64 examples in the testing dataset
test_X_vis = test_X[: batch_size]  # fetch first 64 samples
# fetch first 64 ground truth prediction
ground_truths = test_y[: batch_size]
# predict with the model
preds = test_function((test_X_vis,
                       np.expand_dims(ground_truths, axis=-1)))[1]
preds = np.squeeze(preds, axis=-1).astype(np.int)

plt.figure()
for i in range(2):
  for j in range(5):
    plt.subplot(2, 5, i * 5 + j + 1)
    plt.imshow(test_x[i * 5 + j].reshape(28, 28), cmap="gray")
    plt.title("Ground Truth: %s, \n Prediction %s" %
              (labels[ground_truths[i * 5 + j]],
               labels[preds[i * 5 + j]]))
plt.show()
