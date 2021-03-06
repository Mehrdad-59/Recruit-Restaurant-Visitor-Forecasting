# -*- coding: utf-8 -*-
"""Recruit Restaurant Visitor Forecasting_PyTorch0.56299.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pol1qvQuWld0rBdK6Nzxxt7SBWS1ThS1
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split
import random
from sklearn.metrics import mean_squared_error as mse
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder

import warnings
warnings.filterwarnings('ignore')
import gc

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

def RMSLE(y_pred, y_test):
    return np.sqrt(mse(y_test,y_pred))

train=pd.read_csv('Recruit_Restaurant_train.csv')
test=pd.read_csv('Recruit_Restaurant_test.csv')

train.drop(['air_store_id','visit_date','latitude','longitude'], axis=1, inplace=True)
test.drop(['air_store_id','visit_date','latitude','longitude'], axis=1, inplace=True)

X=train.drop('visitors', axis=1)
y=train['visitors']
X_test=test

cat_cols=[col for col in X.columns if X[col].dtype in ['object', 'category'] ]
cat_cols

for f in cat_cols:
  lbl = LabelEncoder()
  lbl.fit(list(X[f].values) + list(X_test[f].values))
  X[f] = lbl.transform(list(X[f].values))
  X_test[f] = lbl.transform(list(X_test[f].values))

Scaler=MinMaxScaler().fit(X)
X=Scaler.transform(X)
X_test=Scaler.transform(X_test)

def seed_everything(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

SEED=2022
seed_everything(SEED)

torch.cuda.is_available()

X=torch.tensor(X, dtype=torch.float)#.cuda()
X_test=torch.tensor(X_test, dtype=torch.float)#.cuda()
y=torch.tensor(y,dtype=torch.float).reshape(-1,1)#.cuda()

class ResVisModel(nn.Module):
  def __init__(self, in_sz, out_sz, layers, p):
    super().__init__()
    layerlist=[]
    for i in layers:
      layerlist.append(nn.Linear(in_sz,i))
      layerlist.append(nn.ReLU(inplace=True))
      layerlist.append(nn.BatchNorm1d(i))
      layerlist.append(nn.Dropout(p))
      in_sz=i
    layerlist.append(nn.Linear(layers[-1], out_sz))

    self.layers=nn.Sequential(*layerlist)
  
  def forward(self, x):
    x=self.layers(x)
    return x

in_sz=X.shape[1]
out_sz=1
layers=[200,150,100,100]
p=0.5
model=ResVisModel(in_sz, out_sz, layers, p)
#gpumodel=model.cuda()

criterion=nn.MSELoss()
optimizer=torch.optim.Adam(model.parameters(), lr=0.1)

import time
start_time=time.time()

epochs=100
NFOLDS=5
kf =KFold(n_splits=NFOLDS)
y_pred_final=torch.tensor(np.zeros((X_test.shape[0],1)))#.cuda()
y_pred_rmsle=torch.tensor(np.zeros((X.shape[0],1)))#.cuda()

for fold, (tr_idx, te_idx) in enumerate(kf.split(X)):
  kf_X_train=X[tr_idx]#.cuda()
  kf_y_train=y[tr_idx]#.cuda()
  kf_X_val=X[te_idx]#.cuda()
  kf_y_val=y[te_idx]#.cuda()
  
  print('Training fold:', fold+1)
  #y=y.cuda()
  for i in range (epochs):
        i+=1
        oof_y_pred=model(kf_X_train)
        oof_y_val=model(kf_X_val)

        oof_Pred_loss=torch.sqrt(criterion(oof_y_pred,kf_y_train))
        oof_Val_loss=torch.sqrt(criterion(oof_y_val,kf_y_val))

        if i%10==0:
          print(f'epoch: {i:3}  loss: {oof_Pred_loss.item(): 8.6f}  val_loss: {oof_Val_loss.item(): 8.6f}')
        
        optimizer.zero_grad()
        oof_Pred_loss.backward()
        optimizer.step()
  with torch.no_grad() :
    #X=X.cuda()
    #X_test=X_test.cuda()
    y_pred=model(X)
    y_pred_rmsle+=model(X)/NFOLDS
    #y_pred_final=y_pred_final.cpu()
    y_pred_final+=(np.expm1(model(X_test)))/NFOLDS
    #y=y.cpu()
    #y_pred=y_pred.cpu()
  print(f'fold {fold+1} RMSLE Score: {np.sqrt(mse(y,y_pred)): 8.6f}')
print(f'\nDuration:{time.time() - start_time:.0f} seconds')

y_pred_final=y_pred_final.detach().numpy()#.cpu()

y_pred_final.min()

y_pred_final=np.clip(y_pred_final,0,None)

np.save('pred_PyTorch.npy', y_pred_final)

y_pred_rmsle=y_pred_rmsle.detach().numpy()#.cpu()

y_pred_rmsle=np.clip(y_pred_rmsle,0,None)

RMSLE(y_pred_rmsle, y)

submission=pd.read_csv('sample_submission.csv')

submission['visitors']=y_pred_final

submission.to_csv('submission_PyTorch.csv', index=False, float_format='%.3f')

from google.colab import files

files.download('submission_PyTorch.csv')