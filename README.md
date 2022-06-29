# Recruit-Restaurant-Visitor-Forecasting
Predict how many future visitors a restaurant will receive.

Challenge is to use reservation and visitation data to predict the total number of visitors to a restaurant for future dates. This information will help restaurants be much more efficient and allow them to focus on creating an enjoyable dining experience for their customers.

After data preparation and feature engineering, feature extraction was done based on mutual correlation between features and one of the features in each pair of features with correlation higher than 0.9 was removed.

prediction eas done using 4 models: Catboost, lgbm, XGBoost and PyTorch. The best single model performer was lgbm with rmsle: 0.53397. The best ensemble of the models' rmsle was 0.53298 
