#!/usr/bin/env python3

# Read airnow text data file and convert to IODA netcdf for RRFS-SD
# Baseline v2r1
# Last modified by Huiying Luo, Sept 2025, v2

import os
from datetime import datetime
from pathlib import Path
import netCDF4 as nc
import numpy as np
import pandas as pd
import calendar
from math import radians, cos, sin, asin, sqrt
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
    monitor_df = read_monitor_file(sitefile)
    df = pd.merge(df, monitor_df, on='siteid')
    df.drop_duplicates(inplace=True)
    df = filter_bad_values(df)
    return long_to_wide(df)

def read_lu(aqslandusefile):
    lu_read = pd.read_csv(aqslandusefile)
    lu_id = lu_read['stat_id']
    lu_loc = lu_read['loc_setting']
    lu_isurban = [1 if loc == 'URBAN AND CENTER CITY' else 0 for loc in lu_loc]
    df = pd.DataFrame(np.column_stack((lu_id,lu_isurban)), columns=[ 'lu_id','lu_isurban'])
    return df

def read_bl(baselinefile,aqslandusefile):
    dss = nc.Dataset(baselinefile)
    site_id_aqs = dss.variables['site_id_aqs'][:]
    site_lat_aqs = dss.variables['site_lat'][:]
    site_lon_aqs = dss.variables['site_lon'][:]
    DS_aqs = dss.variables['PM25baseline'][:]
    
    dss.close()
    aqs_isurban = np.zeros(len(site_id_aqs))
    lu=read_lu(aqslandusefile)

    counter=0
    for i in range(len(site_id_aqs)):
        try:
            aqs_isurban[i]=lu.lu_isurban[np.where(site_id_aqs[i]==lu.lu_id)[0][0]]
        except:# no info as not urban
            counter=counter+1
    #print('Total urban baseline site: ' +str(int(sum(aqs_isurban))))
    #print(str(counter)+' out of '+str(len(site_id_aqs)) +' baseline location settings not found, used non-urban as default.')
    df = pd.DataFrame(np.column_stack((site_id_aqs,site_lat_aqs,site_lon_aqs,aqs_isurban)), columns=[ 'siteid','lat','lon','isurban'])
    return (df,DS_aqs)

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

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Radius of earth in kilometers.
    return km
# Settings
SearchDist_km=[100,30,30] # Max searching distances for both (baseline and obs) non-urban, one urban one non urban, and both urban; ORDER MATTERS
KeepNoncalib=0 # Keep(1) or discart(0, default) sites w no matching baseline nearby

def find_nearest_within_threshold(reference_lat, reference_lon, reference_isurban,lat,lon,isurban):
    """
    Finds the index of the nearest location from a baseline dataset to a reference point.
    In: lat lon is_urban for obs site, lat lon is_urban array for baseline data
    Out: index of matched site from baseline
    """
    min_distance=[100000,100000,100000]
    nearest_location=[np.nan,np.nan,np.nan]
    for s in range(len(lat)):
        distance = haversine(reference_lat, reference_lon, lat[s], lon[s])
        match_setting=int(reference_isurban+isurban[s]) # index of SearchDist_km
        if distance < min_distance[match_setting]:
            min_distance[match_setting] = distance
            nearest_location[match_setting] = s
    #print(min_distance)
    #print(nearest_location)
    for i in range(3):
        if min_distance[i]>SearchDist_km[i]:
            nearest_location[i]=np.nan
    #print(min_distance)
    #print(nearest_location)

    # return prefernce: both urban/non-urban, then mismatched land setting
    for index in [0,2,1]:
        if ~np.isnan(nearest_location[index]):
            #print(nearest_location[index])
            return nearest_location[index]
    return np.nan

def smooth_BLm2m(DS_aqsioda,dst,DS_aqs):
    """
    Produce month-to-month smoothed baseline at obs time 
    In: obs, obs time, monthly baseline
    Out: baseline at the times of obs 
    """
    # Temp ref BL to deal with Jan and Dec
    BLL=np.concatenate((DS_aqs,DS_aqs,DS_aqs),axis=1) # site*36*24
         
    
    if dst.day>(calendar.monthrange(dst.year, dst.month)[1]-7): # smooth m2m transition for last
        y1=BLL[:,dst.month+12-1,dst.hour]
        y2=BLL[:,dst.month+12,dst.hour]
        x1=calendar.monthrange(dst.year, dst.month)[1]-7 
        x2=calendar.monthrange(dst.year, dst.month)[1]+8
        BLsmooth=y1+(dst.day-x1)* ((y2 - y1) / (x2 - x1))
    elif dst.day<8: # smooth m2m transition for first week
        y1=BLL[:,dst.month+12-1-1,dst.hour]
        y2=BLL[:,dst.month+12-1,dst.hour]
        x1=-7 
        x2=8
        BLsmooth=y1+(dst.day-x1)* ((y2 - y1) / (x2 - x1))
    else:  # center of month use monthly BL directly 
            BLsmooth=BLL[:,dst.month+12-1,dst.hour]
    return BLsmooth


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
    required.add_argument(
        '-l', '--aqslandusefile',
        help="path of land use file",
        type=str, required=True)

    args = parser.parse_args()

    
    if sitefile == 'True':
      print('Input files:', args.input, args.sitefile, args.baselinefile, args.aqslandusefile)
      print('Output ioda file:', args.output)
      f = add_data(args.input, args.sitefile).drop_duplicates(subset=['PM2.5', 'OZONE', 'BC', 'CO', 'SO2','PM10', 'siteid', 'latitude', 'longitude'])  
      #print(f) #index is not clean  
      f=f.reset_index(drop=True)
      #print(f)
      ## Baseline removal
            
      # Step 1: Temporal interpolate baseline to obs time space with month to month smoothing
      [DS_blsite,DS_blraw]=read_bl(args.baselinefile,args.aqslandusefile)
      #print(DS_blsite)
      DS_blsmooth=smooth_BLm2m(f['PM2.5'],f.time[0],DS_blraw)
      
      # Step 2: Spatial matching and baseline removal
      lu=read_lu(args.aqslandusefile)
      DS_aqsfinal=np.zeros([len(f['PM2.5'])])
      DS_aqsfinal[:]=np.nan
      DS_aqscali=np.zeros([len(f['PM2.5'])])
      counter=0
      print('When obs site location setting not found to match with nearby sites, used non-urban as default.')
      #BLsitelist=DS_blsite.siteid
      #print(BLsitelist)
      #df=DS_blsite
      #print(int(df[df.siteid.str.match('000030701')].index[0]))

      #print(len(df[df.siteid.str.match('huh')].index))
      #print(f.siteid[2])
      #print(f.loc[2,'siteid'])
      #print(f.loc[3,'PM2.5'])
      #print(DS_blsmooth)
      #print(DS_blsmooth[1])
      #print()
      for s in range(len(f['PM2.5'])):
          #print(s)
          if len(DS_blsite[DS_blsite.siteid.str.match(f.siteid[s])].index)==0:
              # find matching nearby
            
              # obs site location settings
              try:
                  #print('Obs site location setting found')
                  obs_isurban=lu.lu_isurban[np.where(f.siteid[s]==lu.lu_id)[0][0]]
              except:# no info as not urban
                  obs_isurban=0
            
              nearest = find_nearest_within_threshold(f.latitude[s], f.longitude[s], obs_isurban,DS_blsite.lat,DS_blsite.lon,DS_blsite.isurban)
              if np.isnan(nearest):
                  #print('No matching site found..................')
                  counter=counter+1
                  if KeepNoncalib==0:
                      DS_aqsfinal[s]=np.nan
                  else:
                      DS_aqsfinal[s]=f['PM2.5'][s]
              else:
                  #print('Matching site found..................')
                  DS_aqsfinal[s]=f['PM2.5'][s]-DS_blsmooth[nearest]
                  DS_aqscali[s]=1
          else: # direct match id
              #print('Direct match found..............')
              #print(f.iloc[s,1])
              #print(DS_blsite[DS_blsite.siteid.str.match(f.iloc[s,1])].index)
              match = DS_blsite[DS_blsite.siteid.str.match(f.siteid[s])].index[0]
              #print(match)
              #print(DS_blsmooth[match])
              DS_aqsfinal[s]=f['PM2.5'][s]-DS_blsmooth[match]
              DS_aqscali[s]=1
      DS_aqsfinal[DS_aqsfinal<0]=0.0
      DS_aqsfinal=np.round(DS_aqsfinal,2)
      print()
      if KeepNoncalib==0:
          print(str(counter)+' out of '+str(len(f['PM2.5']))+' observation sites discarded. Change KeepNoncalib to 1 to keep raw observation at these locations.')
      else:
          print(str(counter)+' out of '+str(len(f['PM2.5']))+' observation sites not calibrated. Change KeepNoncalib to 0 to discard raw observation sites.')
      
      print()
    else:
      print('infile=', args.input)
      # f = add_data_1(args.input)
    #np.set_printoptions(threshold=50)
    #print(f['PM2.5'][0:50].to_numpy())
    f['PM2.5']=DS_aqsfinal
    #print(f['PM2.5'][0:50].to_numpy())
    f3 = f.dropna(subset=['PM2.5'], how='any').reset_index()
    nlocs, columns = f3.shape
    
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
    data[var1] = np.array(f3[key1].fillna(float_missing_value)) #PM2.5 bkg removed
    data[var2] = np.array((f3[key2]/1000).fillna(float_missing_value))
    data[var3] = np.array(f3[key3].fillna(float_missing_value))
    data[var4] = np.array(f3[key4].fillna(float_missing_value))
    data[var5] = np.array(f3[key5].fillna(float_missing_value))
    data[var6] = np.array(f3[key6].fillna(float_missing_value)) 
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
    print('Airnow ioda file saved for baseline-removed PM2.5!')
    print()
