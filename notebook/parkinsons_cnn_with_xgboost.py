# -*- coding: utf-8 -*-
"""Parkinsons CNN with XGboost.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18-mSKRW5mfB2CfCdwoO4IJgbW1RfA4Ux

# Installing and Importing required libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from sklearn.preprocessing import MinMaxScaler, LabelBinarizer
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.naive_bayes import CategoricalNB
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, make_scorer, roc_auc_score, auc, roc_curve
from sklearn.calibration import calibration_curve
import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

from keras.models import Sequential, Model
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Flatten
from keras.optimizers import Adam
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
#from keras.utils import np_utils
from keras.callbacks import LearningRateScheduler
from keras.callbacks import EarlyStopping

"""# Data Collection and Preprocessing"""

df = pd.read_csv('/content/Gait_Data___Arm_swing_02Apr2024.csv')
df = df.iloc[:,3:]
print(df.shape)
df = df.dropna(subset=['COHORT'])
df.head()

"""## Dataset Information"""

df.info()

"""## Statistical Details of the data"""

df.describe()

"""## Checking for missing values in the data"""

df.isnull().sum()

"""## Data Visualization

### Histograms
"""

_ = df.hist(figsize=(25,20))

"""### Plotting Correlation matrix"""

fig1 = plt.figure(figsize=(50,50))
sns.heatmap(df.corr(), annot=True, fmt='.2f')

"""### Label Encoding"""

df['COHORT'].value_counts()

df.COHORT = df.COHORT.replace({1.0:0, 3.0:1})

df.head()

"""# Splitting into Data and Target"""

x = df.drop('COHORT', axis=1)
x.fillna(x.mean(), inplace=True)
y = df['COHORT']

x.head()

y.head()

"""## Scaling the Data"""

scaler = MinMaxScaler(feature_range=(0,1))
x_scaled = pd.DataFrame(scaler.fit_transform(x), columns=x.columns)
x_scaled.head()

"""# Splitting into Training and Testing Sets"""

X_train, X_test, y_train, y_test = train_test_split(x_scaled, y, test_size=0.2, stratify=y, random_state=42)

X_train = X_train.reset_index(drop=True)
X_test = X_test.reset_index(drop=True)
y_train = y_train.reset_index(drop=True)
y_test = y_test.reset_index(drop=True)

X_train.shape, X_test.shape, y_train.shape, y_test.shape

X_train.head()

"""# Building and Training ML Classification models

### Naive Bayes
"""

gnb = GaussianNB()

gnb.fit(X_train, y_train)

acc_nb = accuracy_score(gnb.predict(X_test), y_test)
rec_nb = recall_score(gnb.predict(X_test), y_test)
prec_nb = precision_score(gnb.predict(X_test), y_test)
print('Accuracy on Testing Set: {:.2f}'.format(acc_nb))
print('Recall on Testing Set: {:.2f}'.format(rec_nb))
print('Precision on Testing Set: {:.2f}'.format(prec_nb))

print(classification_report(y_test, gnb.predict(X_test)))

"""### XGBoost Classifier"""

xgb = XGBClassifier()

xgb.fit(X_train.values, y_train.values)

acc_train = accuracy_score(xgb.predict(X_train.values), y_train.values)
print('Accuracy on Training Set: ', acc_train)

acc_x = accuracy_score(xgb.predict(X_test.values), y_test.values)
rec_x = recall_score(xgb.predict(X_test.values), y_test.values)
prec_x = precision_score(xgb.predict(X_test.values), y_test.values)
print('Accuracy on Testing Set: {:.2f}'.format(acc_x))
print('Recall on Testing Set: {:.2f}'.format(rec_x))
print('Precision on Testing Set: {:.2f}'.format(prec_x))

print(classification_report(y_test.values, xgb.predict(X_test.values)))

"""### Random Forest Classifier"""

rfc = RandomForestClassifier()

rfc.fit(X_train, y_train)

acc_train = accuracy_score(rfc.predict(X_train), y_train)
print('Accuracy on Training Set: ', acc_train)

acc_r = accuracy_score(rfc.predict(X_test), y_test)
rec_r = recall_score(rfc.predict(X_test), y_test)
prec_r = precision_score(rfc.predict(X_test), y_test)
print('Accuracy on Testing Set: {:.2f}'.format(acc_r))
print('Recall on Testing Set: {:.2f}'.format(rec_r))
print('Precision on Testing Set: {:.2f}'.format(prec_r))

report = classification_report(y_test, rfc.predict(X_test))
print(report)

"""### CatBoost Classifier"""

clf = CatBoostClassifier(
    iterations=10,
    learning_rate=0.001,
    verbose=0)

clf.fit(X_train, y_train)

acc_c = accuracy_score(clf.predict(X_test), y_test)
rec_c = recall_score(clf.predict(X_test), y_test)
prec_c = precision_score(clf.predict(X_test), y_test)
print('Accuracy on Testing Set: {:.2f}'.format(acc_c))
print('Recall on Testing Set: {:.2f}'.format(rec_c))
print('Precision on Testing Set: {:.2f}'.format(prec_c))

accuracies = [acc_nb, acc_x, acc_r,acc_c]

accuracies

"""# ConvXGB - CNN with XGBoost

### Checking if the datset is balanced

"""

df = df.sort_values(by='COHORT')
print(df.shape)
df

freqs = df['COHORT'].value_counts()
freqs

"""###  Reshaping Training and Testing Sets for CNN"""

X_train_cnn = np.array(X_train).reshape(-1, 2, 28, 1)
X_test_cnn = np.array(X_test).reshape(-1, 2, 28, 1)
y_train = np.array(y_train)
y_test = np.array(y_test)

"""### CNN model"""

model_cnn = Sequential()
K.set_image_data_format('channels_last')
model_cnn.add(Conv2D(64,3,3, padding='same', input_shape=(2,28,1),activation='relu',name = 'convo_2d_1'))
# model_cnn.add(MaxPooling2D(pool_size=(1,1),padding='same',name = 'maxpool_1'))
model_cnn.add(Dropout(0.5))
model_cnn.add(Conv2D(64, 3, 3, activation= 'relu',padding='same' ,name = 'convo_2d_2'))
# model_cnn.add(MaxPooling2D(pool_size=(1,1),padding='same',name = 'maxpool_2'))
model_cnn.add(Dropout(0.5))
model_cnn.add(Conv2D(32, 5, 5, activation= 'relu',padding='same' ,name = 'convo_2d_3'))
model_cnn.add(Dropout(0.5))
# model_cnn.add(Conv2D(32, 5, 5, activation= 'relu',padding='same' ,name = 'convo_2d_4'))
# model_cnn.add(Dropout(0.5))
model_cnn.add(Flatten(name = 'flatten'))
model_cnn.add(Dense(128, activation= 'relu',name = 'dense_layer1' ))
model_cnn.add(Dense(64, activation= 'relu',name = 'dense_layer_2' ))
model_cnn.add(Dense(1, activation= 'sigmoid' ))
model_cnn.compile(loss= 'binary_crossentropy' , optimizer= 'adam' , metrics=[ 'accuracy' ])

"""## Model Summary"""

model_cnn.summary()

"""## Training the CNN Model"""

import tensorflow as tf
checkpoint_filepath = '/tmp/ckpt/checkpoint.model.keras'
model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=True,
    monitor='val_accuracy',
    mode='max',
    save_best_only=True)

from tensorflow.keras.callbacks import Callback

class StopAtAccuracy(Callback):
    def __init__(self, accuracy=0.8):
        super(StopAtAccuracy, self).__init__()
        self.accuracy = accuracy

    def on_epoch_end(self, epoch, logs=None):
        if logs.get('val_accuracy') >= self.accuracy:
            print(f"\nReached {self.accuracy*100}% validation accuracy, stopping training!")
            self.model.stop_training = True
stop_at_accuracy_callback = StopAtAccuracy(accuracy=0.91)

history = model_cnn.fit(
    X_train_cnn, y_train,
    epochs=200,
    batch_size=120,
    validation_data=(X_test_cnn, y_test),
    shuffle=True,
    callbacks=[model_checkpoint_callback, stop_at_accuracy_callback]
)

plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.xlabel('Number of Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

loss_df = pd.DataFrame({'Epoch': np.arange(0,200,1),
                        'TrainingLoss': history.history['loss'],
                        'ValidationLoss': history.history['val_loss']})

loss_df.to_csv('LossDataFrame.csv')

plt.plot(history.history['accuracy'], label='Training Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.xlabel('Number of Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

accuracy_df =  pd.DataFrame({'Epoch': np.arange(0,200,1),
                             'TrainingAccuracy': history.history['accuracy'],
                             'ValidationAccuracy': history.history['val_accuracy']})

accuracy_df.to_csv('AccuracyDataFrame.csv')

model_feat = Model(inputs = model_cnn.input, outputs=model_cnn.get_layer('convo_2d_3').output)

X_train.shape

feat_train = model_feat.predict(X_train_cnn)
print(feat_train.shape)

feat_test = model_feat.predict(X_test_cnn)
print(feat_test.shape)

"""## Combining with XGBoost"""

xgb_cnn = XGBClassifier(learning_rate=0.01, n_estimators=100,max_depth=6)
xgb_cnn.fit(feat_train.reshape(feat_train.shape[0], -1), y_train)
xgb_cnn.score(feat_test.reshape(feat_test.shape[0], -1), y_test)

rfc = RandomForestClassifier(n_estimators = 100)
rfc.fit(feat_train.reshape(feat_train.shape[0], -1), y_train)
rfc.score(feat_test.reshape(feat_test.shape[0], -1),y_test)

clf = CatBoostClassifier(
    iterations=100,
    learning_rate=0.01,
    verbose=0)

clf.fit(feat_train.reshape(feat_train.shape[0], -1), y_train)
clf.score(feat_test.reshape(feat_test.shape[0], -1), y_test)

from lightgbm import LGBMClassifier
lgm = LGBMClassifier(min_data_in_leaf=200,verbose = 0)
lgbm = lgm.fit(feat_train.reshape(feat_train.shape[0], -1), y_train)
lgbm.score(feat_test.reshape(feat_test.shape[0], -1), y_test)

import numpy as np
from sklearn.metrics import accuracy_score

# Assuming xgb_cnn, clf, and rfc are already trained models and feat_test is the test dataset

# Obtain predictions from each model
xgb_cnn_pred = xgb_cnn.predict(feat_test.reshape(feat_test.shape[0], -1))
clf_pred = clf.predict(feat_test.reshape(feat_test.shape[0], -1))
rfc_pred = rfc.predict(feat_test.reshape(feat_test.shape[0], -1))

# Ensure predictions are integer class labels
xgb_cnn_pred = xgb_cnn_pred.astype(int)
clf_pred = clf_pred.astype(int)
rfc_pred = rfc_pred.astype(int)

# Stack the predictions
preds = np.vstack((xgb_cnn_pred, clf_pred, rfc_pred)).T

# Ensemble Voting
ensemble_pred = np.apply_along_axis(lambda x: np.argmax(np.bincount(x)), axis=1, arr=preds)

# Evaluation
accuracy = accuracy_score(y_test, ensemble_pred)
print(f'Ensemble Model Accuracy: {accuracy:.2f}')

"""# **END**"""
