#!/usr/bin/env python3

# Read airnow text data file and convert to IODA netcdf for RRFS-SD
# Last modified by Huiying Luo, Mar 2025

import os
from datetime import datetime
from pathlib import Path
import netCDF4 as nc
import numpy as np
import pandas as pd

import pyiodaconv.ioda_conv_engines as iconv
import pyiodaconv.ioda_conv_ncio as iconio
from collections import defaultdict, OrderedDict
from pyiodaconv.orddicts import DefaultOrderedDict

os.environ["TZ"] = "UTC"

# Dictionary of output variables (ObsVal, ObsError, and PreQC).
# First is the incoming variable name followed by list of IODA outgoing name and units.

varDict = {'PM2.5': ['particulatematter2p5Surface', 'ug m-3'],
           'OZONE': ['ozoneSurface', 'ppmV'],
           'BC': ['BlackcarbonSurface', 'ug m-3'],
           'CO': ['CarbonmonoxideSurface', 'ppmV'],
           'SO2': ['SulfurdioxideSurface', 'ppb'],
           'PM2.5raw': ['particulatematter2p5Surfaceraw', 'ug m-3'],
           'PM10': ['particulatematter10Surface', 'ug m-3']}

locationKeyList = [("latitude", "float", "degrees_north"),
                   ("longitude", "float", "degrees_east"),
                   ("dateTime", "long", "seconds since 1970-01-01T00:00:00Z"),
                   ("stationElevation", "float", "m"),
                   ("height", "float", "m"),
                   ("stationIdentification", "string", "")]
meta_keys = [m_item[0] for m_item in locationKeyList]

GlobalAttrs = {'converter': os.path.basename(__file__),
               'ioda_version': 2,
               'description': 'AIRNow data (converted from text/csv to IODA',
               'source': 'Unknown (ftp)'}

iso8601_string = locationKeyList[meta_keys.index('dateTime')][2]
epoch = datetime.fromisoformat(iso8601_string[14:-1])

metaDataName = iconv.MetaDataName()
obsValName = iconv.OvalName()
obsErrName = iconv.OerrName()
qcName = iconv.OqcName()

float_missing_value = nc.default_fillvals['f4']
int_missing_value = nc.default_fillvals['i4']
double_missing_value = nc.default_fillvals['f8']
long_missing_value = nc.default_fillvals['i8']
string_missing_value = '_'

missing_vals = {'string': string_missing_value,
                'integer': int_missing_value,
                'long': long_missing_value,
                'float': float_missing_value,
                'double': double_missing_value}
dtypes = {'string': object,
          'integer': np.int32,
          'long': np.int64,
          'float': np.float32,
          'double': np.float64}


def read_monitor_file(sitefile=None):

    colsinuse = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21]
    airnow = pd.read_csv(sitefile, delimiter='|', header=None,
                         usecols=colsinuse, dtype={0: str}, encoding="ISO-8859-1")
    airnow.columns = [
        'siteid', 'Site_Code', 'Site_Name', 'Status', 'Agency',
        'Agency_Name', 'EPA_region', 'latitude', 'longitude', 'Elevation',
        'GMT_Offset', 'Country_Code', 'CMSA_Code', 'CMSA_Name', 'MSA_Code',
        'MSA_Name', 'state_Code', 'state_Name', 'County_Code',
        'County_Name', 'City_Code']
    airnow['airnow_flag'] = 'AIRNOW'
    airnow.columns = [i.lower() for i in airnow.columns]
    return airnow


def filter_bad_values(df):
    """Short summary.

    Returns
    -------
    type
        Description of returned object.

    """
    #print(df.columns) 
    if sitefile == 'True':
      df.loc[(df.obs > 3000) | (df.obs < 0), 'obs'] = np.NaN
    else:
      df.loc[(df.pm25 > 3000) | (df.pm25 < 0), 'pm25'] = np.NaN
      df.loc[(df.ozone > 3000) | (df.ozone < 0), 'ozone'] = np.NaN

    return df


def long_to_wide(df):
    from pandas import Series, merge
    w = df.pivot_table(
        values='obs', index=['time', 'siteid'],
        columns='variable').reset_index()
    cols = Series(df.columns)
    g = df.groupby('variable')
    for name, group in g:
        w[name + '_unit'] = group.units.unique()[0]

    return merge(w, df, on=['siteid', 'time'])


def add_data(infile, sitefile):
    df = pd.read_csv(infile, delimiter='|',
                     header=None,
                     on_bad_lines='warn',
                     encoding='ISO-8859-1')
    cols = ['date', 'time', 'siteid', 'site', 'utcoffset', 'variable', 'units',
            'obs', 'source']
    df.columns = cols
    df['obs'] = df.obs.astype(float)
    df['siteid'] = df.siteid.str.zfill(9)
    df['utcoffset'] = df.utcoffset.astype(int)
    df['time'] = pd.to_datetime(df.date + ' ' + df.time,
                                format='%m/%d/%y %H:%M',
                                exact=True)
    df.drop(['date'], axis=1, inplace=True)
    df['time_local'] = df.time + pd.to_timedelta(df.utcoffset, unit='H')
    #print(df)
    monitor_df = read_monitor_file(sitefile)
    #print(monitor_df)
    df = pd.merge(df, monitor_df, on='siteid')
    df.drop_duplicates(inplace=True)
    df = filter_bad_values(df)
    return long_to_wide(df)

def read_bl(baselinefile,h):
    ds = nc.Dataset(baselinefile)
    site_id_aqs = ds.variables['site_id_aqs'][:]
    PM25baseline = ds.variables['PM25baseline'][:,h]
    df = pd.DataFrame(np.column_stack((site_id_aqs,PM25baseline)), columns=[ 'siteid','baseline'])
    return df

def add_data_1(infile):
    df = pd.read_csv(infile, delimiter=',',
                     header=0,
                     on_bad_lines='warn',
                     encoding='ISO-8859-1')
    cols = ["AQSID","SiteName","Status","EPARegion","Latitude","Longitude","Elevation","GMTOffset","CountryCode","StateName", \
            "ValidDate","ValidTime","DataSource","ReportingArea_PipeDelimited", \
            "OZONE_AQI","PM10_AQI","PM25_AQI","NO2_AQI", \
            "OZONE_Measured","PM10_Measured","PM25_Measured","NO2_Measured", \
            "NO2","NO2_Unit","CO","CO_Unit","PM25","PM25_Unit","SO2","SO2_Unit","OZONE","OZONE_Unit","PM10","PM10_Unit"]
    df.columns = cols
    df.columns = [i.lower() for i in df.columns]
    df['PM2.5'] = df.pm25.astype(float)
    #pd.set_option('display.max_rows', None)
    df['OZONE'] = df.ozone.astype(float)
    df['siteid'] = df.aqsid.str.zfill(9)
    df['utcoffset'] = df.gmtoffset.astype(int)
    df['time'] = pd.to_datetime(df.validdate + ' ' + df.validtime,
                                format='%m/%d/%Y %H:%M',
                                exact=True)
    df['time_local'] = df.time + pd.to_timedelta(df.utcoffset, unit='H')
    df.drop_duplicates(inplace=True)
    df = filter_bad_values(df)
    #print(df[["aqsid","latitude","longitude","elevation",'time',"pm25","pm25_unit","ozone","ozone_unit"]])
    return df

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(
        description=(
            'Reads single AIRNow text file '
            ' and converts into IODA formatted output files.')
    )
    import sys
    sitefile = os.environ['sitefile'] 
    required = parser.add_argument_group(title='required arguments')
    if sitefile == 'True':
        
        required.add_argument(
            '-s', '--sitefile',
            help="path of AIRNow site list file",
            type=str, required=True)

    required.add_argument(
        '-i', '--input',
        help="path of AIRNow text input file",
        type=str, required=True)
    required.add_argument(
        '-o', '--output',
        help="path of IODA output file",
        type=str, required=True)
    required.add_argument(
        '-b', '--baselinefile',
        help="path of baseline file",
        type=str, required=True)

    args = parser.parse_args()

    
    if sitefile == 'True':
      print('infile=', args.input, args.sitefile, args.baselinefile)
      
      f = add_data(args.input, args.sitefile).drop_duplicates(subset=['PM2.5', 'OZONE', 'BC', 'CO', 'SO2','PM10', 'siteid', 'latitude', 'longitude'])  

      # Baseline removal
      dt=f.time[1].to_pydatetime()
      #print(dt)
      f_bl=read_bl(args.baselinefile,int(dt.strftime("%-H")))
      ff = pd.merge(f, f_bl, on='siteid')
      #print(ff)
      ff=ff.rename(columns={'PM2.5':'PM2.5raw'})
      ff['PM2.5']=ff['PM2.5raw']-ff['baseline']
      ff.loc[ff['PM2.5'] < 0, 'PM2.5'] = 0
      #print(ff['PM2.5'].values.tolist())

    else:
      print('infile=', args.input)
      #f = add_data_1(args.input)

    f3 = ff.dropna(subset=['PM2.5'], how='any').reset_index()
    nlocs, columns = f3.shape
    
    #print(f3)
    #print(f3['PM2.5'].values.tolist())
    dt = f3.time[1].to_pydatetime()
    time_offset = round((dt - epoch).total_seconds())

    ioda_data = {}         # The final outputs.
    data = {}              # Before assigning the output types into the above.
    for key in varDict.keys():
        data[key] = []
    for key in meta_keys:
        data[key] = []

    # Fill the temporary data arrays from input file column data
    data['stationIdentification'] = np.full(nlocs, f3.siteid, dtype='S20')
    data['dateTime'] = np.full(nlocs, np.int64(time_offset))
    data['latitude'] = np.array(f3['latitude'])
    data['longitude'] = np.array(f3['longitude'])
    data['stationElevation'] = np.array(f3['elevation'])
    data['height'] = np.array(f3['elevation'])
    for n in range(nlocs):
        data['height'][n] = data['height'][n] + 10.0   # 10 meters above stationElevation

    for n, key in enumerate(varDict.keys()):
        if n == 0:
            key1 = key
            var1 = varDict[key][0]
        elif n == 1:
            key2 = key
            var2 = varDict[key][0]
        elif n == 2:
            key3 = key
            var3 = varDict[key][0]
        elif n == 3:
            key4 = key
            var4 = varDict[key][0]
        elif n == 4:
            key5 = key
            var5 = varDict[key][0]
        elif n == 5:
            key6 = key
            var6 = varDict[key][0]
        elif n == 6:
            key7 = key
            var7 = varDict[key][0]
    data[var1] = np.array(f3[key1].fillna(float_missing_value)) #PM2.5 bkg removed
    data[var2] = np.array((f3[key2]/1000).fillna(float_missing_value))
    data[var3] = np.array(f3[key3].fillna(float_missing_value))
    data[var4] = np.array(f3[key4].fillna(float_missing_value))
    data[var5] = np.array(f3[key5].fillna(float_missing_value))
    data[var6] = np.array(f3[key6].fillna(float_missing_value)) #PM2.5raw
    data[var7] = np.array(f3[key7].fillna(float_missing_value))
    DimDict = {'Location': nlocs}

    varDims = {}
    for key in varDict.keys():
        variable = varDict[key][0]
        varDims[variable] = ['Location']

    # Set units of the MetaData variables and all _FillValues.
    varAttrs = DefaultOrderedDict(lambda: DefaultOrderedDict(dict))
    for key in meta_keys:
        dtypestr = locationKeyList[meta_keys.index(key)][1]
        if locationKeyList[meta_keys.index(key)][2]:
            varAttrs[(key, metaDataName)]['units'] = locationKeyList[meta_keys.index(key)][2]
        varAttrs[(key, metaDataName)]['_FillValue'] = missing_vals[dtypestr]

    # Set units and FillValue attributes for groups associated with observed variable.
    for key in varDict.keys():
        variable = varDict[key][0]
        units = varDict[key][1]
        varAttrs[(variable, obsValName)]['units'] = units
        varAttrs[(variable, obsErrName)]['units'] = units
        varAttrs[(variable, obsValName)]['coordinates'] = 'longitude latitude'
        varAttrs[(variable, obsErrName)]['coordinates'] = 'longitude latitude'
        varAttrs[(variable, qcName)]['coordinates'] = 'longitude latitude'
        varAttrs[(variable, obsValName)]['_FillValue'] = float_missing_value
        varAttrs[(variable, obsErrName)]['_FillValue'] = float_missing_value
        varAttrs[(variable, qcName)]['_FillValue'] = int_missing_value

    # Fill the final IODA data:  MetaData then ObsValues, ObsErrors, and QC
    for key in meta_keys:
        dtypestr = locationKeyList[meta_keys.index(key)][1]
        ioda_data[(key, metaDataName)] = np.array(data[key], dtype=dtypes[dtypestr])

    for key in varDict.keys():
        variable = varDict[key][0]
        #print(variable)
        if variable in data:
          ioda_data[(variable, obsValName)] = np.array(data[variable], dtype=np.float32)
          ioda_data[(variable, obsErrName)] = np.full(nlocs, 0.1*data[variable], dtype=np.float32)
          #print('Datatype:', data[variable].dtype)
          ioda_data[(variable, obsErrName)] = np.where(0.1*data[variable]>0.1,0.1*np.float32(data[variable]),0.1)
          #v4
          #ioda_data[(variable, obsErrName)] = np.where(0.05*data[variable]>0.05,0.05*np.float32(data[variable]),0.05)
          #v3 
          #ioda_data[(variable, obsErrName)] = np.where(data[variable]<1.0,0.01,0.01*np.float32(data[variable]))
          #ioda_data[(variable, obsErrName)] = np.where(data[variable]>=10.0,0.001*np.float32(data[variable]*data[variable]),ioda_data[(variable, obsErrName)])
          #ioda_data[(variable, obsErrName)] = np.where(data[variable]>=50.0,0.05*np.float32(data[variable]),ioda_data[(variable, obsErrName)])
          #ioda_data[(variable, qcName)] = np.full(nlocs, 2, dtype=np.int32)
        else:
          print(f"Warning: {variable} not found in data.")
          ioda_data[(variable, obsValName)] = np.full(nlocs, float_missing_value, dtype=np.float32)
          ioda_data[(variable, obsErrName)] = np.full(nlocs, float_missing_value, dtype=np.float32)
          ioda_data[(variable, qcName)] = np.full(nlocs, float_missing_value, dtype=np.int32)

    # setup the IODA writer and write everything out.
    writer = iconv.IodaWriter(args.output, locationKeyList, DimDict)
    writer.BuildIoda(ioda_data, varDims, varAttrs, GlobalAttrs)
#$FV3bundle/ioda-upgrade-v2-to-v3.x ${airnow_out}/airnow-v2-$1.nc   ${airnow_out}/airnow-v3-$1.nc /scratch2/BMC/wrfruc/rli/JEDI/build/ioda/share/test/testinput/validation/ObsSpace.yaml
    print('Airnow ioda file saved for baseline-removed PM2.5!')
