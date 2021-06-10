import numpy as np
import pandas as pd
import utils_data as ud
import constants as cons
import datetime
import urllib3
import certifi
import re
import io
import gzip
import time
import json
from dateutil.parser import parse
# import pyowm
import logging
'''

Functions

'''
module_logger = logging.getLogger('consumption_forecast.weather')

def join_temperature_actuals_and_forecast(mi, date_start, date_end, split_date=cons.DATE_END_DEFAULT):
    
    if split_date < cons.DATE_END_DEFAULT:
        date_end_a = split_date + pd.Timedelta(23, unit='H')
        fcst_date = split_date
    else:
        date_end_a = date_end
        fcst_date = pd.Timestamp.now()
    
    temperature_act = ud.get_data(mi['temperature_actuals_filename'],
                                  date_start, date_end_a, mi['temperature_actuals_dateformat'])
                       
    module_logger.info('Last actual temperature and its date \n%s', temperature_act.tail(5).to_string())
                       
    if (split_date < cons.DATE_END_DEFAULT) or (date_end > pd.Timestamp.now()):
        
        filename = mi['temperature_forecast_filename']

        if filename.find('PROVCODE') > 0:

            filename = filename.replace('YYYY-MM-DD', fcst_date.strftime(cons.DATE_FORMAT))
            try:
                filename_1 = filename.replace('PROVCODE', cons.YANDEX_PROVIDER_CODE)
                temperature_fcst = ud.get_data(filename_1, d_end=date_end)
            except FileNotFoundError:
                filename_2 = filename.replace('PROVCODE', cons.OWM_PROVIDER_CODE)
                temperature_fcst = ud.get_data(filename_2, d_end=date_end + pd.Timedelta(1, unit='H'))
                date_end = date_end + pd.Timedelta(1, unit='H')

        else:

            temperature_fcst = ud.get_data(mi['temperature_forecast_filename'],
                                           date_start, date_end, mi['temperature_forecast_dateformat'])
        
        module_logger.info('forecast temperature on date, when forecast is being made\n%s', temperature_fcst[fcst_date.strftime(cons.DATE_FORMAT)].to_string())
        
        date_range = pd.date_range(date_start, date_end, freq='H')
        x = np.empty(len(date_range)).fill(np.nan)
        t = pd.DataFrame(x, index=date_range, columns=[cons.TEMPERATURE_NAME])

        t.loc[temperature_act.index, cons.TEMPERATURE_NAME] = temperature_act[cons.TEMPERATURE_NAME]
        forecast_start_date = t.last_valid_index() + pd.Timedelta(1, unit = 'H')
        t.loc[forecast_start_date:, cons.TEMPERATURE_NAME] = temperature_fcst[cons.TEMPERATURE_NAME]
        t.to_csv('temp_check.csv')
        module_logger.info('Actual and forecast temperature merged. \n%s', t[fcst_date.strftime(cons.DATE_FORMAT)].to_string())
    else:

        t = temperature_act
        module_logger.info('Only actual temperature will be used')
    return t



def read_from_url(station_id, date_start, date_end, code):

    url_custom = 'http://' + code + '/download/files.synop/' + station_id[:2] + '/' + station_id + '.' + \
                 date_start + '.' + date_end + '.1.0.0.ru.utf8.00000000.csv.gz'

#     print(url_custom)

    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
    response = http.request(method='GET',
                            headers={'Referer': 'https://rp5.ru/'},
                            url=url_custom
                            )

    compressed_file = io.BytesIO(response.data)
    source_file = gzip.open(compressed_file, mode='rt')

    df = pd.read_csv(filepath_or_buffer=source_file,
                     delimiter=';',
                     skiprows=6,
                     index_col=0,
                     parse_dates=True,
                     dayfirst=True,
                     decimal='.',
                     encoding='UTF-8')

    return df


def load_temperature_actuals(station_id, date_from, date_to, file=None):

    date_from_str = date_from.strftime('%d.%m.%Y')
    date_to_str = date_to.strftime('%d.%m.%Y')

    if file is not None:
        df = pd.read_csv(filepath_or_buffer=file,
                         delimiter=';',
                         skiprows=6,
                         index_col=0,
                         parse_dates=True,
                         dayfirst=True,
                         decimal='.',
                         encoding='UTF-8')

    else:
        try:
            code = '93.90.217.250'
            df = read_from_url(station_id, date_from_str, date_to_str, code)

        except OSError:

            try:
                code = '95.213.205.170'
                df = read_from_url(station_id, date_from_str, date_to_str, code)

            except OSError:
                code = '37.200.66.117'
                df = read_from_url(station_id, date_from_str, date_to_str, code)

    df = df.iloc[:, 0]
    dt = pd.DataFrame(df.values, index=df.index, columns=[cons.TEMPERATURE_NAME])
    dt.index.name = cons.TIMESTEP_NAME
    dt.sort_index(inplace=True)
    dt = dt.loc[date_from:date_to]

    return dt


def load_yandex_temperature_forecast(mi, period=cons.YANDEX_FORECAST_DAYS_NUMBER):

    parts_to_hours = {
        'night': range(0, 6),
        'morning': range(6, 12),
        'day': range(12, 18),
        'evening': range(18, 24)
    }
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    params = {
        'lat': str(mi['temperature_yan_station_lat']),
        'lon': str(mi['temperature_yan_station_lon']),
        'lang': 'en_US',
        'limit': str(period),
        'hours': True,
        'extra': True
    }

    r = http.request(method='GET',
                     fields=params,
                     headers={'X-Yandex-API-Key': cons.YANDEX_KEY},
                     url='https://api.weather.yandex.ru/v1/forecast/')

    response = json.loads(r.data.decode('utf-8'))

    res = []

    for f in response['forecasts']:

        dt = parse(f['date']).date()
        hrs = []

        for h in f['hours']:
            timestep = datetime.datetime.combine(dt, datetime.time(hour=int(h['hour'])))
            hrs.append({
                cons.TIMESTEP_NAME: timestep,
                cons.TEMPERATURE_NAME: float(h['temp']),
            })

        for p, rng in parts_to_hours.items():

            for h in rng:
                timestep = datetime.datetime.combine(dt, datetime.time(hour=h))

                res.append({
                    cons.TIMESTEP_NAME: timestep,
                    cons.TEMPERATURE_NAME: hrs[h][cons.TEMPERATURE_NAME]
                    if len(hrs) >= h + 1 else float(f['parts'][p]['temp_avg']),
                })

    forecast_df = pd.DataFrame(res).set_index(cons.TIMESTEP_NAME).sort_index()

    return forecast_df


# def load_owm_temperature_forecast(mi):
    
#     lati = float(mi['temperature_owm_station_lat'])
#     long = float(mi['temperature_owm_station_lon'])
        
#     owm = pyowm.OWM(cons.OWM_KEY)
#     fc = owm.three_hours_forecast_at_coords(lati, long)
#     fcst = fc.get_forecast()
    
#     dates = []
#     temp_fcsts = []

#     for weather in fcst:
    
#         date = pd.to_datetime(weather.get_reference_time('date'))
#         date_form = datetime.datetime.combine(date.date(), date.time())
#         dates.append(date_form)
    
#         temp_fcst = weather.get_temperature('celsius')['temp']
#         temp_fcsts.append(temp_fcst)
    
#     forecast_df = pd.DataFrame()
#     forecast_df[cons.TEMPERATURE_NAME] = temp_fcsts
#     forecast_df.index = dates
#     forecast_df.index.name = cons.TIMESTEP_NAME
    
#     return forecast_df
    
    
    
    
    
