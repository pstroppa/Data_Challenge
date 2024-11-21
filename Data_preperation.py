## module:: Data challenge config file
#     :platform:   Windows
#     :synopsis:   all functions for data handling
# .. moduleauthor: Peter Stroppa BSc
#
#
##########################################################################

import pandas as pd
import numpy as np
from dateutil.relativedelta import *

def load_csv_data(raw_data_path, **kwargs):
    """
    read in data. Data has to be in csv file format using the porvided input paths as Windows.Path
    objects. Set the correct index and returns two pandas.Dataframes containing all transmitter data

    :param raw_data_path: Windows.Path
    :returns raw_data: pandas.Dataframe
    """

    index = kwargs.get("index", "default")
    raw_data = pd.read_csv(raw_data_path, sep=",", lineterminator="\n", encoding="utf-8",dtype={"year":str,"value":float})
    if index != "default":
        raw_data = raw_data.set_index(index) 
    return raw_data


def replace_categories(one_country, labels):
    """
    function replace all category labels with shorter names:
    :param one_country: pandas.DataFrame
    :param labels: list
    """
    keys = one_country["category"].unique()
    replace_dict = {key: value for key,value in zip(keys,labels)}

    one_country = one_country.replace(replace_dict)
    return one_country


def seperate_categories(emission_df,**kwargs):
    """
    emission_df contains emission data with different categories in one label they shall be 
    seperated into different column
    
    :param emission_df: pandas.DataFrame
    :kwarg: choose_labels: list of str or str
    :returns working_dict: dict
    """
    working_labels = kwargs.get("choose_labels", ["carbon_dioxide_co2", "methane_ch4_emissions", \
                                                 'sulphur_hexafluoride_sf6'])
    labels = ["_".join(label.split("_", 3)[:3]) for label in emission_df["category"].unique()]
    
    emission_dict = {}
    for label,long_label in zip(labels,emission_df["category"].unique()):
        emission_dict[label] = emission_df.loc[emission_df["category"]==long_label]

    working_dict = dict((key, emission_dict[key]) for key in working_labels)

    return working_dict


def dataframe_interpolation(emission_df, intervall):
    """
    interpolate in between dataframe values. Add an interpolated value on each intervall row.
    supported intervall are 2 and 3!
    
    :param emission_df: pandas.DataFrame
    :param intervall: int
    :returns interpolated_df: pandas.Dataframe
    """
    emission_df = emission_df.sort_values(by=["year"])
    emission_df_loc = emission_df.reset_index()
    index = range(0,len(emission_df)*intervall)
    interpolated_df = pd.DataFrame(columns=emission_df.columns,index=index)
    month = 12/intervall

    for ind, row in emission_df_loc.iterrows():
        interpolated_df.iloc[ind*intervall] = [row["country_or_area"], row["year"], row["value"],\
                                               row["category"] ]
        
    for ind, row in emission_df_loc.iterrows():
        interpolated_df.iloc[ind*intervall+1] = [row["country_or_area"], row["year"]+ relativedelta(months=+month),\
                                                 np.nan, row["category"] ]
    if intervall == 3:
        for ind, row in emission_df_loc.iterrows():
            interpolated_df.iloc[ind*intervall+2] = [row["country_or_area"], row["year"]+\
                                                      relativedelta(months=+month*2), np.nan, row["category"] ]
    
    interpolated_df["value"] = interpolated_df["value"].astype("float")
    interpolated_df.loc[:,"value"]= interpolated_df.loc[:,"value"].interpolate(method="polynomial", order=2)
    interpolated_df = interpolated_df.iloc[:-(intervall-1),:]
    return interpolated_df


def calc_Results(em_data,categories, countries,  **kwargs):
    """
    calculate the desired measure for example max pultor for one gas for example CO2
    :param em_data: pandas.DataFrame
    :param countries: list
    """
    #get kwargs
    rating_type = kwargs.get("rating_type", "all")
    results_dict = {}
    result_temp = {}

    years = pd.to_datetime(em_data["year"], format='%Y')
    em_data.loc[:,"year"] = years
    
    if rating_type == "max-year" or rating_type == "all":
        results_dict["max-year"] = {}   
        for gas in categories:
            one_gas = em_data[em_data["category"]==gas]
            maximum = one_gas.sort_values("value",ascending=False)[:3]
            results_dict["max-year"][gas] = round(maximum,1)

    if rating_type == "min-year" or rating_type == "all":
        results_dict["min-year"] = {}   
        for gas in categories:
            one_gas = em_data[em_data["category"]==gas]
            minimum = one_gas.sort_values("value",ascending=True)[:3]
            results_dict["min-year"][gas] = round(minimum,1)


    if rating_type == "max-total" or rating_type == "all":
        results_dict["max-total"] = {}
        result_temp["max-total"] = {}   
        for gas in categories:
            one_gas = em_data[em_data["category"]==gas]
            for country in countries:
                working_data = one_gas[one_gas["country_or_area"]==country]
                working_data = working_data.set_index("year")
                result_temp["max-total"]["max_total_" +gas + "_" + country] = working_data["value"].sum()
            max_tot = round(pd.Series(result_temp["max-total"]).sort_values(ascending=False),1)
            results_dict["max-total"][gas] = max_tot[:3]

    if rating_type == "min-total" or rating_type == "all":
        results_dict["min-total"] = {}
        result_temp["min-total"] ={}  
        for gas in categories:
            one_gas = em_data[em_data["category"]==gas]
            for country in countries:
                working_data = one_gas[one_gas["country_or_area"]==country]
                working_data = working_data.set_index("year")
                result_temp["min-total"]["min_total_" + gas + "_" + country] = working_data["value"].sum()
            min_tot =round(pd.Series(result_temp["min-total"]).sort_values(ascending=True),1)
            results_dict["min-total"][gas] = min_tot[:3]

    if rating_type == "most-improved" or rating_type == "all":
        results_dict["most-improved"] = {} 
        result_temp["most-improved"] = {} 
        for gas in categories:
            one_gas = em_data[em_data["category"]==gas]
            for country in countries:
                working_data = one_gas[one_gas["country_or_area"]==country]
                working_data = working_data.set_index("year")
                if len(working_data) != 0:
                    result_temp["most-improved"]["most-improved_" +gas + "_" + country] = \
                          working_data["value"].max() / working_data["value"].iloc[0] 
            improved = round(pd.Series(result_temp["most-improved"]).sort_values(ascending=False),2)
            results_dict["most-improved"][gas] = improved[:3]

    return results_dict            
            
            
            
           

def flatten_result_and_csv(results_dict):
    """
    export results to Excel for faster plotting and analysis due to time constraint
    :param results_dict: dict
    """
        
    mi_tot =  pd.DataFrame(results_dict["min-total"])
    improved =  pd.DataFrame(results_dict["most-improved"])
    ma_tot = pd.DataFrame(results_dict["max-total"])
    
    rest = pd.DataFrame({key: results_dict[key] for key in ["max-year", "min-year"]})
    rest.to_csv("max_min.csv")
    ma_tot.to_csv("maxium_total" +".csv")
    mi_tot.to_csv("mi_tot" +".csv")
    improved.to_csv("improved" +".csv")


















# %%
