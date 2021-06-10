import pandas as pd
import warnings
import numpy as np
import matplotlib.pyplot as plt
import constants as cons
import seaborn as sns

pd.set_option("display.max_rows", 999)

timestep = cons.TIMESTEP_NAME

'''

Functions

'''


def errors_by_week(df, which_error='mae'):

    week_df = pd.DataFrame()
    errors = []
    dates_start_of_week = []
    weeks = df.timestep.dt.weekofyear.unique()

    for week in np.sort(weeks):
        week_subset = df[df.timestep.dt.weekofyear == week]
        week_error = week_subset[which_error].mean()
        errors.append(week_error)
        
        date_start = str(week_subset.timestep.dt.date.iloc[0])
        dates_start_of_week.append(date_start)
            
    week_df['Dates_start_of_week'] = dates_start_of_week
    week_df[which_error + '_by_week'] = errors

    plt.figure(figsize=(6, 16))
    ax = sns.barplot(errors, dates_start_of_week)

    for i, v in enumerate(errors):
        ax.text(v + 0.1, i + .25, str("%2.1f" % v))

    if which_error == 'mae':
        ax.set_xlabel('Absolute error, MWh')
        ax.set_title('Absolute error by weeks', fontweight='bold')
    elif which_error == 'mape':
        ax.set_xlabel('MAPE, %')
        ax.set_title('Absolute percentage error by weeks', fontweight='bold')
    else:
        ax.set_xlabel('Error, MWh')
        ax.set_title('Error by weeks', fontweight='bold')

    return week_df


def errors_by_week_line(df, which_error='mae'):
    
    plt.figure(figsize=(25, 10)) 
    
    weeks = df.timestep.dt.weekofyear.unique()
    
    year_df = pd.DataFrame() 
    year_df['week'] = range(1,len(weeks)+1)
    years = df.timestep.dt.year.unique()
    
    dates_start_of_week = []
    
    for y in years:
        
        year_subset = df[df.timestep.dt.year == y]
        errors = []
                
        for week in np.sort(weeks):
            week_subset = year_subset[year_subset.timestep.dt.weekofyear == week]
            week_error = week_subset[which_error].mean()
            errors.append(week_error)
            
            if year_subset.shape[0] == 8760 or year_subset.shape[0] < 3000 :
                try:
                    date_start = str(week_subset.timestep.dt.date.iloc[0])
                    dates_start_of_week.append(date_start)
                except IndexError:
                    pass
                       
        year_df[str(y)] = errors
        
        plt.plot(range(1,len(weeks)+1), errors)
    
    if which_error == 'mae':
        plt.ylabel('Absolute error, MWh')
        plt.title('Absolute error by weeks', fontweight='bold')
    elif which_error == 'mape':
        plt.ylabel('MAPE, %')
        plt.title('Absolute percentage error by weeks', fontweight='bold')
    else:
        plt.ylabel('Error, MWh')
        plt.title('Error by weeks', fontweight='bold')
    plt.legend(years)
    plt.xticks(range(1,len(weeks)+1), dates_start_of_week, rotation = 90)
    # plt.savefig('errors_by_weeks_line.png')
    plt.show() 


def errors_by_day(df, which_error='mae'):

    day_df = pd.DataFrame()
    errors = []
    day_of_week = df.timestep.dt.dayofweek.unique()
    day_of_week_sorted = np.sort(day_of_week)
    
    for day in day_of_week_sorted:
        day_subset = df[df.timestep.dt.dayofweek == day]
        day_error = day_subset[which_error].mean()
        errors.append(day_error)
    
    dow = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    day_df['DoW'] = dow
    day_df[which_error + '_by_day'] = errors

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(dow, errors)

    if which_error == 'mae':
        ax.set_ylabel('Absolute error, MWh')
        ax.set_title('Absolute error by DoW', fontweight='bold')
    elif which_error == 'mape':
        ax.set_ylabel('MAPE, %')
        ax.set_title('Absolute percentage error by DoW', fontweight='bold')
    else:
        ax.set_ylabel('Error, MWh')
        ax.set_title('Error by DoW', fontweight='bold')

    return day_df


def errors_by_month(df, which_error='mae'):

    month_df = pd.DataFrame()
    errors = []
    months = df.timestep.dt.month.unique()
    months_sorted = np.sort(months)

    for m in months_sorted:
        month_subset = df[df.timestep.dt.month == m]
        month_error = month_subset[which_error].mean()
        errors.append(month_error)

    month_list = ['January', 'Febrary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']

    month_df['Month'] = month_list
    month_df[which_error + '_by_month'] = errors

    plt.figure(figsize=(6, 10))
    ax = sns.barplot(errors, month_list)

    for i, v in enumerate(errors):
        ax.text(v + 0.1, i + .25, str("%2.1f" % v))

    if which_error == 'mae':
        ax.set_xlabel('Absolute error, MWh')
        ax.set_title('Absolute error by month', fontweight='bold')
    elif which_error == 'mape':
        ax.set_xlabel('MAPE, %')
        ax.set_title('Absolute percentage error by month', fontweight='bold')
    else:
        ax.set_xlabel('Error, MWh')
        ax.set_title('Error by month', fontweight='bold')

    return month_df


def errors_by_month_line(df, which_error='mae'):
    
    month_list = ['January', 'Febrary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    plt.figure(figsize=(20, 10)) 
       
    year_df = pd.DataFrame() 
    year_df['month'] = range(1,13)
    years = df.timestep.dt.year.unique()
    
    for y in years:
        year_subset = df[df.timestep.dt.year == y]
        
        month_df = pd.DataFrame()
        errors = []
        months = df.timestep.dt.month.unique()
        months_sorted = np.sort(months)
    
        for m in months_sorted:
            month_subset = year_subset[year_subset.timestep.dt.month == m]
            month_error = month_subset[which_error].mean()
            errors.append(month_error)
    
        year_df[str(y)] = errors
        
        plt.plot(range(1,13), errors)
        
    if which_error == 'mae':
        plt.ylabel('Absolute error, MWh')
        plt.title('Absolute error by month', fontweight='bold')
    elif which_error == 'mape':
        plt.ylabel('MAPE, %')
        plt.title('Absolute percentage error by month', fontweight='bold')
    else:
        plt.ylabel('Error, MWh')
        plt.title('Error by month', fontweight='bold')
    plt.legend(years)
    plt.xticks(range(1,13), month_list)
    # plt.savefig('errors_by_months_line.png')
    plt.show() 


def errors_by_hour(df, which_error='mae'):

    hour_df = pd.DataFrame()
    errors = []
    hours = df.timestep.dt.hour.unique()

    for h in hours:
        hour_subset = df[df.timestep.dt.hour == h]
        hour_error = hour_subset[which_error].mean()
        errors.append(hour_error)

    hour_df['Hour'] = hours
    hour_df[which_error + '_by_hour'] = errors

    plt.figure(figsize=(10, 5))
    ax = sns.barplot(hours, errors)

    if which_error == 'mae':
        ax.set(xlabel='Hours', ylabel="Absolute Error, MWh")
        ax.set_title('Absolute error by hours', fontweight='bold')
    elif which_error == 'mape':
        ax.set(xlabel='Hours', ylabel="MAPE, %")
        ax.set_title('Absolute percentage error by hour', fontweight='bold')
    else:
        ax.set(xlabel='Hours', ylabel="Error, %")
        ax.set_title('Error by hour', fontweight='bold')
    plt.show()

    return hour_df


def plot_error(df, which_error='mae', start_dt=pd.datetime(2010, 1, 1), end_dt=pd.Timestamp.now()):

    plt.figure(figsize=(20, 5))
    subset = df[(df.timestep >= start_dt) & (df.timestep <= end_dt)]
    ax = sns.lineplot(subset.timestep, subset[which_error])

    if which_error == 'mae':
        ax.set_ylabel('Absolute error, MWh')
        ax.set_title('Absolute error of prediction', fontweight='bold')
    elif which_error == 'mape':
        ax.set_ylabel('MAPE, %')
        ax.set_title('Absolute percentage error', fontweight='bold')
    else:
        ax.set_ylabel('Error, MWh')
        ax.set_title('Error by DoW', fontweight='bold')


def plot_hist_error(df, which_error='mae'):

    plt.figure(figsize=(10, 5))
    ax = sns.distplot(df[which_error], hist = True, bins = 20)


def plot_fact_preds(df, start_dt=pd.datetime(2010, 1, 1), end_dt=pd.Timestamp.now()):

    subset = df[(df.timestep >= start_dt) & (df.timestep <= end_dt)]
    plt.figure(figsize=(20, 5))
    ax1 = sns.lineplot(subset.timestep, subset.Fact, label = 'Fact')
    ax2 = sns.lineplot(subset.timestep, subset.Prediction, label = 'Prediction')
    plt.legend()
    plt.ylabel('Consumption value, MWh')
    plt.xlabel('')
    plt.xticks(rotation = 90)
    plt.title('Actual and predicted consumption values', fontweight='bold')
    # plt.savefig('fact_preds_Jul_Avg_2017.png')


def mean_consumption_by_month(df):

    month_list = ['January', 'Febrary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    plt.figure(figsize=(20, 10)) 
       
    year_df = pd.DataFrame() 
    year_df['month'] = range(1, 13)
    years = df.timestep.dt.year.unique()
    
    for y in years:
        year_subset = df[df.timestep.dt.year == y]
        
        month_df = pd.DataFrame()
        mean_cons = []
        months = df.timestep.dt.month.unique()
        months_sorted = np.sort(months)
    
        for m in months_sorted:
            month_subset = year_subset[year_subset.timestep.dt.month == m]
            cons = month_subset['Fact'].mean()
            mean_cons.append(cons)
    
        year_df[str(y)] = mean_cons
        
        plt.plot(range(1, 13), mean_cons)
        
    plt.legend(years)
    plt.ylabel('Consumption value, MWh')
    plt.xticks(range(1, 13), month_list)
    plt.title('Mean consumption by months')
    # plt.savefig('mean_consumption_by_month.png')
    plt.show()


def mean_consumption_by_week(df):
    
    plt.figure(figsize=(20, 10)) 
       
    weeks = df.timestep.dt.weekofyear.unique()
    
    year_df = pd.DataFrame() 
    year_df['week'] = range(1,len(weeks)+1)
    years = df.timestep.dt.year.unique()
    
    dates_start_of_week = []
    
    for y in years:
        year_subset = df[df.timestep.dt.year == y]
        mean_cons = []
        
        for week in np.sort(weeks):
            week_subset = year_subset[year_subset.timestep.dt.weekofyear == week]
            cons = week_subset['Fact'].mean()
            mean_cons.append(cons)
            
            if year_subset.shape[0] == 8760 or year_subset.shape[0] < 3000:
                try:
                    date_start = str(week_subset.timestep.dt.date.iloc[0])
                    dates_start_of_week.append(date_start)
                except IndexError:
                    pass
    
        year_df[str(y)] = mean_cons
        
        plt.plot(range(1,len(weeks)+1), mean_cons)
        
    plt.legend(years)
    plt.ylabel('Consumption value, MWh')
    plt.xticks(range(1,len(weeks)+1), dates_start_of_week, rotation = 90)
    plt.title('Mean consumption by weeks')
    # plt.savefig('mean_consumption_by_month.png')
    plt.show()
    
    
def plot_temperature(df, start_dt=pd.datetime(2010, 1, 1), end_dt=pd.Timestamp.now()):

    subset = df[(df.index >= start_dt) & (df.index <= end_dt)]
    plt.figure(figsize=(20, 5))
    ax = sns.lineplot(subset.index.values, subset.temperature, label = 'Temperature')
    plt.legend()
    plt.ylabel('Temperature, C')
    plt.xlabel('')
    plt.xticks(rotation = 90)
    plt.title('Actual temperature', fontweight='bold')
    # plt.savefig('fact_preds_Jul_Avg_2017.png')


def mean_temperature_by_week(df):
    
    plt.figure(figsize=(20, 10)) 
       
    df['timestep'] = df.index
    weeks = df.timestep.dt.weekofyear.unique()
    
    year_df = pd.DataFrame() 
    year_df['week'] = range(1,len(weeks)+1)
    years = df.timestep.dt.year.unique()
    
    dates_start_of_week = []
    
    for y in years:
        year_subset = df[df.timestep.dt.year == y]
        mean_temp = []
        
        for week in np.sort(weeks):
            week_subset = year_subset[year_subset.timestep.dt.weekofyear == week]
            temp = week_subset['temperature'].mean()
            mean_temp.append(temp)
            
            if year_subset.shape[0] == 8760 or year_subset.shape[0]<3000:
                try:
                    date_start = str(week_subset.timestep.dt.date.iloc[0])
                    dates_start_of_week.append(date_start)
                except IndexError:
                    pass
    
        year_df[str(y)] = mean_temp
        
        plt.plot(range(1,len(weeks)+1), mean_temp)
    plt.legend(years)
    plt.ylabel('Temperature, C')
    plt.xticks(range(1,len(weeks)+1), dates_start_of_week, rotation = 90)
    plt.title('Mean temperature by weeks')
    # plt.savefig('mean_consumption_by_month.png')
    plt.show()
