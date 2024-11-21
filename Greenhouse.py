

"""
## module:: main file
#     :platform:   Windows
#     :synopsis:   contains all sections, that are loaded into the main file
# .. moduleauthor: Peter Stroppa BSc
#
#
##########################################################################

##########################################################################

.. Overview of the file:
    1) comments
    2) Input
    3) general preprocessing
    4) calculate Correlation
    5) calculate prediction
    6) preprocessing
    7) applying methods
    8) evaluation
"""
#%%
#import self written files:
import Data_preperation as dp
import config_file as cf
import plotting as pt

#import data proccessing packages
import pandas as pd
from dateutil.relativedelta import *


from statsmodels.tsa.statespace.sarimax import SARIMAX

# Plotting
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['font.size'] = 10

######################################################################
#comments old predictions
#
##from sklearn.ensemble import RandomForestRegressor
#from lightgbm import LGBMRegressor
#from sklearn.metrics import mean_squared_error
#import skforecast
#from skforecast.recursive import ForecasterRecursive
#from skforecast.model_selection import TimeSeriesFold
#from skforecast.model_selection import grid_search_forecaster
#from skforecast.model_selection import backtesting_forecaster
#from skforecast.preprocessing import RollingFeatures
#from skforecast.utils import save_forecaster
#from skforecast.utils import load_forecaster

######################################################################
#Input
  

Emission_df = dp.load_csv_data(cf.emission_data_path)

#%%
######################################################################
#general preprocessing (not associated with any methode or any of the four preprocessing methods later on)
original_categories = Emission_df["category"].unique()
categories = ["_".join(label.split("_", 3)[:3]) for label in Emission_df["category"].unique()]
countries = Emission_df["country_or_area"].unique()

Emission_df = dp.replace_categories(Emission_df, categories)

working_dict = dp.seperate_categories(Emission_df, choose_labels=cf.interesting_gases)

######################################################################
#section one_gas
one_gas = Emission_df[Emission_df["category"]=="carbon_dioxide_co2"]
years = pd.to_datetime(one_gas["year"], format='%Y')
one_gas.loc[:,"year"] = years
one_gas = one_gas.set_index("year")
# choose data from European union 

######################################################################

######################################################################
#section one_country
one_country = Emission_df[Emission_df["country_or_area"]=="European Union"]
years = pd.to_datetime(one_country["year"], format='%Y')
one_country.loc[:,"year"] = years
one_country = one_country.set_index("year")
# choose data from European union 

######################################################################
# data analysis find biggest polluters an best practise examples
# for better understanding of data plot all countries with all gases
if cf.plot_all_countries == True:
    i = 1
    for country in countries:
        one_c = Emission_df[Emission_df["country_or_area"]==country]
        years = pd.to_datetime(one_c["year"], format='%Y')
        one_c.loc[:,"year"] = years
        one_c = one_c.set_index("year")

        output_name = country + "_all_gases.html"
        title_name = "all emssions of: " + country
        print(f"Step: {i} of {len(countries)}")
        i+=1
        dp.plot_all_gases(one_c, categories, categories, output_name = output_name,title=title_name)

if cf.make_analysis == True:
    results = dp.calc_Results(Emission_df,cf.interesting_gases, countries)
    dp.flatten_result_and_csv(results)



######################################################################
#starting prediction section
######################################################################
sf6 = working_dict["sulphur_hexafluoride_sf6"]
sf6_EU = sf6[sf6["country_or_area"]=="European Union"] #  European Union
#convert years to datetime
years = pd.to_datetime(sf6_EU["year"], format='%Y')
sf6_EU.loc[:,"year"] = years

######################################################################
#polynomial interpolation of data to get more values
sf6_EU_interpolated = dp.dataframe_interpolation(sf6_EU, cf.interpolation_intervall)
######################################################################
sf6_EU_interpolated = sf6_EU_interpolated[["year","value"]]
sf6_EU_interpolated = sf6_EU_interpolated.set_index("year")
#creat correct frequency for time series analyis yearly
sf6_EU_interpolated = sf6_EU_interpolated.asfreq('4MS') #
# data is already sorted correctly but to be sure for other data sets
sf6_EU_interpolated = sf6_EU_interpolated.sort_index()
sf6_EU_interpolated = sf6_EU_interpolated.rename(columns={"value":"y"})

######################################################################
# define old train and test sets randforest regressor
#steps = 7
#prediction_steps = 7
#train = sf6_EU_interpolated[:-steps]#no random splitting because timeseries [20:-steps]
#test  = sf6_EU_interpolated[-steps:]

######################################################################
#plot train test split
#pt.plot_train_test(train,test)


######################################################################
#first prediction - no good quality
"""regressor = RandomForestRegressor(random_state=123, n_estimators=100)
forecaster = ForecasterRecursive(regressor, lags = 2)

#fit data
forecaster.fit(y=train["value"])
predictions = forecaster.predict(steps=prediction_steps)

#calculate error
error_mse = mean_squared_error(y_true = test["value"], y_pred = predictions)

fig, ax = plt.subplots(figsize=(6, 2.5))
train["value"].plot(ax=ax, label="train")
test["value"].plot(ax=ax, label="test")
predictions.plot(ax=ax, label="prediction-without backtracking")
ax.legend();
"""
######################################################################
#new approach using a SARIMAX model for predicting
percent_80 = int(round(len(sf6_EU_interpolated)*0.85,0))   #int(round(len(sf6_EU_interpolated)*cf.test_percent,0)) # 80/20 split
train = sf6_EU_interpolated[:percent_80]#no random splitting because timeseries [20:-steps]
test = sf6_EU_interpolated[percent_80:]
offset = 10000


#%%
#############################################################################
#SARIMAX
model = SARIMAX(
    train['y'],  # Training data
    order=(1, 1, 0),  # (p, d, q) order: adjust based on data behavior
    seasonal_order=(0, 0, 0, 0),  # No seasonality
    enforce_stationarity=False,
    enforce_invertibility=False
)

sarimax_results = model.fit(disp=False)

# Predict future values 30 steps = 120 months
n_forecast_steps = 30
future_years = pd.date_range(start=train.index[-1] + pd.DateOffset(months=4), periods=n_forecast_steps, freq='4MS')
forecast_values = sarimax_results.get_forecast(steps=n_forecast_steps).predicted_mean

# Backtesting on test data (i.e. kross falidating time series data)
backtest_values = sarimax_results.get_prediction(start=test.index[0], end=test.index[-1]).predicted_mean

# Combine data for visualization
forecast_df = pd.DataFrame({'y': forecast_values}, index=future_years)
backtest_df = pd.DataFrame({'y': backtest_values}, index=test.index)

# Combine everything for plotting
train['type'] = 'train'
test['type'] = 'test'
backtest_df['type'] = 'backtest'
forecast_df['type'] = 'forecast'

combined_df = pd.concat([train, test, backtest_df, forecast_df])

pred_title_name = "prediction of SF6 emission within the EU for the next 10 years "

pt.plot_prediction(train,test,backtest_df,forecast_df,title = pred_title_name)

print("DONE JUHU!")