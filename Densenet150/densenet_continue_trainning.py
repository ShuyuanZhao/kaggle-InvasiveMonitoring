# coding: utf-8
import os
import numpy as np
import pandas as pd
from keras.preprocessing import image
from PIL import ImageFile

from keras.models import Model
from keras.optimizers import SGD
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import ModelCheckpoint

from densenet121 import densenet121_model

def get_data(img_size, split_rate):
    # get train data
    train_label = pd.read_csv("../../data/train_labels.csv")
    img_path = "../../data/train/"
    
    file_paths = []
    y = []
    for i in range(len(train_label)):
        file_paths.append( img_path + str(train_label.iloc[i][0]) +'.jpg' )
        y.append(train_label.iloc[i][1])
    y = np.array(y)

    x = []
    for i, img_path in enumerate(file_paths):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        img = image.load_img(img_path, target_size=(img_size, img_size))
        img = image.img_to_array(img)   
        x.append(img)
    x = np.array(x)
    
    # get test data
    test_no = pd.read_csv("../../data/sample_submission.csv")
    test_img_path = "../../data/test/"

    test_file_paths = []
    test_img_nos = []
    for i in range(len(test_no)):
        test_file_paths.append( test_img_path + str(int(test_no.iloc[i][0])) +'.jpg' )
        test_img_nos.append(int(test_no.iloc[i][0]))
    test_img_nos = np.array(test_img_nos)

    test = []
    for i, img_path in enumerate(test_file_paths):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        img = image.load_img(img_path, target_size=(img_size, img_size))
        img = image.img_to_array(img)   
        test.append(img)
    test = np.array(test)

    test = test.astype('float32')
    test /= 255
    
    # data shuffle
    random_index = np.random.permutation(len(y))
    x_shuffle = []
    y_shuffle = []
    for i in range(len(y)):
        x_shuffle.append(x[random_index[i]])
        y_shuffle.append(y[random_index[i]])

    x = np.array(x_shuffle) 
    y = np.array(y_shuffle)
    
    # data split
    val_split_num = int(round(split_rate*len(y)))
    x_train = x[val_split_num:]
    y_train = y[val_split_num:]
    x_test = x[:val_split_num]
    y_test = y[:val_split_num]

    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    
    return x_train, y_train, x_test, y_test, test_img_nos, test  


# get model
model = densenet121_model(img_rows=128, img_cols=128, color_type=3, num_classes=1000)
model.load_weights('./cp_weights.hdf5')
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='binary_crossentropy', metrics=['accuracy'])


# get data
img_size = 128
split_rate = 0.1
(x_train, y_train, x_test, y_test, test_img_nos, test) = get_data(img_size, split_rate)

datagen = ImageDataGenerator(rotation_range=30,width_shift_range=0.2,height_shift_range=0.2,horizontal_flip=True)
datagen.fit(x_train)


# training process
nb_epoch = 1
batch_size = 32
checkpointer = ModelCheckpoint(filepath= './cp_weights_with_2_epoch.hdf5', verbose=1, monitor='val_acc',save_best_only=True, save_weights_only=True)
model.fit_generator(datagen.flow(x_train, y_train, batch_size=batch_size),
                    steps_per_epoch = x_train.shape[0],
                    epochs=nb_epoch,
                    validation_data = (x_test, y_test),
                    callbacks=[checkpointer])



