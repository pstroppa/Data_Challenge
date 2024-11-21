## module:: Data challenge config file
#     :platform:   Windows
#     :synopsis:   all functions for plotting
# .. moduleauthor: Peter Stroppa BSc
#
#
##########################################################################
import config_file as cf

from pathlib import Path

from dateutil.relativedelta import *


from bokeh.plotting import figure, show
from bokeh.io import output_file, output_notebook, show
from bokeh.models import Span, ColumnDataSource
from bokeh.transform import dodge
from bokeh.palettes import Category10, Category20

######################################################################

def plot_train_test(train, test, **kwargs):
    """
    creates a bokeh plot from the train and test set.
    :param train: pandas.DataFrame
    :param test: pandas.DataFrame
    :kwarg output_name: str
    :kwarg title: str
    """
    output_name = kwargs.get("output_name", cf.save_train_test_name)
    title_name = kwargs.get("title", "Train-Test- Split European SF6 emmission")

    output_notebook()

    p = figure(
        title= title_name,
        x_axis_label="Time",
        y_axis_label="Value",
        x_axis_type="datetime",
        width=1000,
        height=800
    )

    # Plot the train data
    p.line(
        train.index, train["y"],
        line_width=2, color="blue",
        legend_label="Train Data"
    )

    # Plot the test data
    p.line(
        test.index, test["y"],
        line_width=2, color="green",
        legend_label="Test Data"
    )

    # Add a vertical line to indicate the split
    split_line = Span(
        location=train.index[-1].timestamp() * 1000,  # Convert to timestamp for Bokeh
        dimension="height",
        line_color="black",
        line_dash="dashed",
        line_width=2
    )
    p.add_layout(split_line)

    # Customize the legend
    p.legend.title = "Legend"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    p.xaxis.axis_label_text_font_size = "10pt"
    p.yaxis.axis_label_text_font_size = "10pt"
    p.xaxis.major_label_text_font_size = "10pt"
    p.yaxis.major_label_text_font_size = "10pt"
    p.title.text_font_size = '24pt'

    if output_name.find(".html") != -1:
            saving_path = output_name
    else:
        saving_path = output_name + ".html"
    correct_path = str(Path(__file__).parents[0].joinpath(
            "Results/" + saving_path))

    output_file(correct_path)

    # Show the plot
    show(p)


    
def plot_all_gases(em_data, names, categories, **kwargs):
    """
    creates a bokeh plot from the train and test set.
    :param train: pandas.DataFrame
    :param test: pandas.DataFrame
    :kwarg output_name: str
    :kwarg title: str
    """
    output_name = kwargs.get("output_name", cf.save_all_gases_name)
    title_name = kwargs.get("title", "All gases for one country")

    em_data=em_data.rename(columns={"value":"y"})
    short_names =["CO2", "GHGs_CO2", "GHGs", "HFC", "CH4", "NF3", "N2O", "PFC", "SF6", "mix"]
    legend_dict = {key:val for key,val in zip(names,short_names)}
    
    output_notebook()

    p = figure(
        title=title_name,
        x_axis_label="Time",
        y_axis_label="Value",
        x_axis_type="datetime",
        width=800,
        height=400
    )
    
    # Generate colors for each category
    num_categories = len(categories)
    palette = Category10[10] if num_categories <= 10 else Category20[20]
    
    # Loop through categories and plot each series
    for i, category in enumerate(categories):
        category_data = em_data[em_data["category"] == category]
        
        p.line(
            category_data.index, category_data["y"],
            line_width=2, color=palette[i % len(palette)],  # Cycle through colors if needed
            legend_label=legend_dict[category]
        )
    
    # Customize the legend
    p.legend.title = "Categories"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    # Show the plot
    if output_name.find(".html") != -1:
            saving_path = output_name
    else:
        saving_path = output_name + ".html"
    correct_path = str(Path(__file__).parents[0].joinpath(
            "Results/" + saving_path))

    output_file(correct_path)

    # Show the plot
    show(p)


def plot_prediction(train,test,backtest_df,forecast_df, **kwargs):
    """
    using bokeh for plotting the prediction of the SF6 emissions in Europe
    """
    output_name = kwargs.get("output_name", cf.save_prediction_name)
    title_name = kwargs.get("title", "Greenhouse Gas Emissions Forecast")
    output_notebook()
    p = figure(title=title_name,
            x_axis_label='Year', 
            y_axis_label='SF6 Emissions in KT',
            x_axis_type='datetime', 
            width=1200, 
            height=800)

    # Add training data
    p.line(train.index, train['y'], color="blue", legend_label="Train Data", line_width=2)

    # Add testing data
    p.line(test.index, test['y'], color="green", legend_label="Test Data", line_width=2)

    # Add backtesting predictions
    p.line(backtest_df.index, backtest_df['y'], color="orange", legend_label="Backtest Predictions", line_width=2)

    # Add future predictions
    p.line(forecast_df.index, forecast_df['y'], color="red", legend_label="Forecast", line_dash="dashed", line_width=2)

    # Add a vertical line to indicate where training ends
    split_line = Span(location=train.index[-1].timestamp() * 1000,  # Convert timestamp for Bokeh
                    dimension='height', 
                    line_color='black', 
                    line_dash='dashed', 
                    line_width=2)
    p.add_layout(split_line)

    # Customize legend
    p.legend.title = "Legend"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"

    p.yaxis.axis_label_text_font_size = "14pt"
    p.xaxis.major_label_text_font_size = "14pt"
    p.yaxis.major_label_text_font_size = "14pt"
    p.title.text_font_size = '24pt'

    # Show the plot
    if output_name.find(".html") != -1:
                saving_path = output_name
    else:
            saving_path = output_name + ".html"
    correct_path = str(Path(__file__).parents[0].joinpath(
                "Results/" + saving_path))

    output_file(correct_path)

    # Show the plot
    show(p)
