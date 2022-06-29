# Recruit-Restaurant-Visitor-Forecasting
Predict how many future visitors a restaurant will receive.

After data preparation and feature engineering, feature extraction was done based on mutual correlation between features and one of the features in each pair of features with correlation higher than 0.9 was removed.

prediction eas done using 4 models: Catboost, lgbm, XGBoost and PyTorch. The best single model performer was lgbm with rmsle: 0.53397. The best ensemble of the models' rmsle was 0.53298 
