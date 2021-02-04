import argparse
import json
# import scipy.signal as ssig
# from math import factorial
from datetime import date, datetime
from pprint import pprint

import ee
import numpy as np
import pandas as pd
import scipy.ndimage as sndi

class Dataset:
    dataset_id = ''
    band_id = ''

    image_collection = None
    band = None
    scale = None

    header = None
    data = None
    data_time = None
    data_values = None

    def __init__(self, dataset_id, band_id):
        self.dataset_id = dataset_id
        self.band_id = band_id

    def initialize_dataset(self, startdate, enddate):
        self.image_collection = ee.ImageCollection(self.dataset_id).filterDate(startdate, enddate)
        self.band = self.image_collection.select(self.band_id)

        try:
            self.scale = ee.Image(self.band.first()).projection().nominalScale().getInfo()
            if self.dataset_id.endswith("LE7_L1T_32DAY_NDVI"):
                self.scale = 30
                if self.dataset_id.endswith("LC8_L1T_32DAY_NDVI"):
                    self.scale = 30
        except ee.ee_exception.EEException as e:
            raise Exception(e.message)

            # check scale LE7_L1T_32DAY_NDVI -> 30

    def load_values(self, point):
        info = self.image_collection.getRegion(point, self.scale).getInfo()
        self.header = info[0]
        self.data = np.array(info[1:])
        index_time = self.header.index('time')
        index_values = self.header.index(self.band_id)
        self.data_time = [i for i in (self.data[0:, index_time])]
        self.data_values = [i for i in (self.data[0:, index_values])]

    def calculate_minimum(self, radius):
        self.data_values = sndi.minimum_filter1d(self.data_values, radius * 2 + 1)

    def calculate_maximum(self, radius):
        self.data_values = sndi.maximum_filter1d(self.data_values, radius * 2 + 1)

    # def smooth_savitzky_golay(self, window_size, order, deriv=0, rate=1):
    #     self.data_values = ssig.savgol_filter(self.data_values, window_size, order, deriv, rate)

    def calculate_median(self, radius):
        self.data_values = sndi.median_filter(self.data_values, radius * 2 + 1)

    def get_time_array(self):
        return self.data_time

    def get_value_array(self):
        return self.data_values

    def calculate_average(self, radius):
        self.data_values = sndi.generic_filter1d(self.data_values, np.mean, radius * 2 + 1)

    def set_scale(self):
        if isinstance(self.data_time[0], (str, unicode)):
            self.data_time = [int(timestamp) for timestamp in self.data_time]

        if self.dataset_id.startswith("MODIS"):
            if self.dataset_id.endswith("MCD15A3H"):
                newTime = []
                newVals = []
                c = len(self.data_values)
                for x in xrange(0, c):
                    if self.data_values[x] is not None:
                        newVals.append(float(self.data_values[x]) / 10)
                        newTime.append(self.data_time[x])
                self.data_time = newTime
                self.data_values = newVals
            else:
                newTime = []
                newVals = []
                c = len(self.data_values)
                for x in xrange(0, c):
                    if self.data_values[x] is not None:
                        newVals.append(float(self.data_values[x]) * 1e-4)
                        newTime.append(self.data_time[x])
                self.data_time = newTime
                self.data_values = newVals

        if self.dataset_id.endswith("LC8_L1T_32DAY_NDVI"):
            newTime = []
            newVals = []
            c = len(self.data_values)
            for x in xrange(0, c):
                if self.data_values[x] is not None:
                    newVals.append(float(self.data_values[x]))
                    newTime.append(self.data_time[x])
            self.data_time = newTime
            self.data_values = newVals

        if self.dataset_id.startswith("VITO"):
            # if isinstance(ndvi[0], (str, unicode)):
            newTime = []
            newVals = []
            c = len(self.data_values)
            for x in xrange(0, c):
                if self.data_values[x] is not None:
                    newVals.append(float(self.data_values[x] - 20) / 250)
                    newTime.append(self.data_time[x])
            self.data_time = newTime
            self.data_values = newVals

	else:
	    newTime = []
	    newVals = []
            c = len(self.data_values)
            for x in xrange(0, c):
                if self.data_values[x] is not None:
                    newVals.append(float(self.data_values[x]))
                    newTime.append(self.data_time[x])
            self.data_time = newTime
            self.data_values = newVals


class Timeline:
    dataset = None
    lat = None
    lon = None
    startdate = None
    enddate = None

    def __init__(self, dataset_id, band_id, lat, lon, startdate, enddate):
        self.dataset = Dataset(dataset_id, band_id)
        self.lat = lat
        self.lon = lon
        self.startdate = startdate
        self.enddate = enddate

    def initialize_dataset(self):
        ee.Initialize()
        self.dataset.initialize_dataset(self.startdate, self.enddate)

    def load_values(self):
        point = {'type': 'Point', 'coordinates': [self.lon, self.lat]}
        self.dataset.load_values(point)

    def calculate_minimum(self, radius):
        self.dataset.calculate_minimum(radius)

    def calculate_maximum(self, radius):
        self.dataset.calculate_maximum(radius)

    def calculate_average(self, radius):
        self.dataset.calculate_average(radius)

    def calculate_median(self, radius):
        self.dataset.calculate_median(radius)

    def get_data_as_list(self):
        return np.column_stack((self.dataset.get_time_array(), self.dataset.get_value_array())).tolist()

    def get_doy_average_data_as_list(self, min, max, avg, med):
        time = self.dataset.get_time_array()
        values = self.dataset.get_value_array()
        time_doy = [datetime.fromtimestamp(i / 1e3).timetuple().tm_yday for i in time]
        df = pd.DataFrame({'time': time_doy, 'values': values})
        values_doy = df.groupby('time').mean()
        values = values_doy.values

        if not min == 0:
            values = sndi.minimum_filter1d(values, min * 2 + 1)
        if not max == 0:
            values = sndi.maximum_filter1d(values, max * 2 + 1)
        if not avg == 0:
            values = sndi.generic_filter1d(values, np.mean, avg * 2 + 1)
        if not med == 0:
            values = sndi.median_filter(values, med * 2 + 1)

        idx = values_doy.index
        return np.column_stack((idx, values)).tolist()

    def set_scale(self):
        self.dataset.set_scale()


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


# def windowsize_type(x):
#     x = int(x)
#     if (x < 0) or (x % 2 == 0):
#         raise argparse.ArgumentTypeError("Window size has to be positive odd integer.")
#     return x


parser = argparse.ArgumentParser(
    "Get a timeline for a specific location from a dataset available on Google Earth Engine.")

parser.add_argument("lat", type=float, help="Latitude for the query location.")
parser.add_argument("lon", type=float, help="Longitude for the query location.")
parser.add_argument("dataset_id", help="Dataset ID (ImageCollection ID) as provided by Google Earth Engine.")
parser.add_argument('-b', "--band-id", help="Band ID as provided by Google Earth Engine.")
parser.add_argument('-s', "--startdate", help="Start Date (YYYY-MM-DD)", required=True, type=valid_date)
parser.add_argument('-e', "--enddate", help="End Date (YYYY-MM-DD) - Current date is used as default.", type=valid_date,
                    default=date.today().strftime('%Y-%m-%d'))
parser.add_argument("-dm", "--daily-mean", action="store_true",
                        help="Return mean values for each day of the year. (e.g. Mean for Jan 1st for all available years)")

group_stat = parser.add_mutually_exclusive_group()
group_stat.add_argument("-min", "--minimum", type=int, default=0,
                        help="Use minimum value of all values within the given radius.")
group_stat.add_argument("-max", "--maximum", type=int, default=0,
                        help="Use maximum value of all values within the given radius.")
group_stat.add_argument("-avg", "--average", type=int, default=0,
                        help="Use average value of all values within the given radius.")
group_stat.add_argument("-med", "--median", type=int, default=0,
                        help="Use median value of all values within the given radius.")
# group_smooth = group_stat.add_argument_group("group_smooth")
# group_smooth.add_argument("-sg", "--savitzky-golay", action="store_true", default=0,
#                         help="Apply Savitzky-Golay smoothing to return dataset.")
# group_smooth.add_argument("windowsize", type=windowsize_type, help="Window size for the filter. Has to be a positive odd integer.")
# group_smooth.add_argument("order", type=int, help="The order of the polynomial used to fit the samples.")

parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode for detailed output.")

args = parser.parse_args()

if args.verbose:
    print("Google Earth Engine timeline loader called with the following arguments:")
    pprint(args)

# if args.sg and (args.windowsize <= args.order):
#     raise argparse.ArgumentTypeError("Polynomial has to be less than windowsize.")

timeline = Timeline(args.dataset_id, args.band_id, args.lat, args.lon, args.startdate, args.enddate)
timeline.initialize_dataset()
timeline.load_values()
timeline.set_scale()

if not args.minimum == 0:
    timeline.calculate_minimum(args.minimum)
if not args.maximum == 0:
    timeline.calculate_maximum(args.maximum)
if not args.average == 0:
    timeline.calculate_average(args.average)
if not args.median == 0:
    timeline.calculate_median(args.median)

if args.daily_mean:
    print(json.dumps(timeline.get_doy_average_data_as_list(args.minimum, args.maximum, args.average, args.median)))
else:
    print(json.dumps(timeline.get_data_as_list()))