## module:: Data challenge config file
#     :platform:   Windows
#     :synopsis:   serveral configuration possibilites
# .. moduleauthor: Peter Stroppa BSc
#
#
##########################################################################
from pathlib import Path
from datetime import date


filename = "Greenhouse.csv"
emission_data_path = Path(__file__).parents[0].joinpath("Data/" + filename)

interesting_gases = ["carbon_dioxide_co2", "methane_ch4_emissions", "sulphur_hexafluoride_sf6"]
##########################################################################
# old prediction section
#train / test split
test_percent = 0.2
interpolation_intervall = 3
# how many steps to predict
prediction_steps = 5

##########################################################################
#plotting parameters
current_date = date.today().strftime("%d_%m_%Y")

save_train_test_name = "train_test_" + current_date + ".html"
save_all_gases_name = "all_gases_" + current_date + ".html"
save_prediction_name = "prediction_" + current_date +".html"

plot_all_countries = False
make_analysis = True
plot_analysis = True


