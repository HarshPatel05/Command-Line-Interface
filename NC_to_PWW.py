import json
import cdsapi
import xarray
from datetime import datetime
import calendar
import os
import glob
import numpy as np
import pandas as pd
import struct
import shutil

from GoogleDriveAPI import UploadFileToGoogleDrive, AuthenticateGoogleDrive

# Path to the configuration file
config_file = 'config.json'


def load_config():
    with open(config_file, 'r') as f:
        return json.load(f)


def fetch_data():
    config = load_config()

    start_day = datetime.strptime(config['start_date'], "%m-%d-%Y").day
    start_month = datetime.strptime(config['start_date'], "%m-%d-%Y").month
    year = datetime.strptime(config['start_date'], "%m-%d-%Y").year
    end_day = datetime.strptime(config['end_date'], "%m-%d-%Y").day
    end_month = datetime.strptime(config['end_date'], "%m-%d-%Y").month

    ListOfDays = []
    if start_month == end_month:
        for i in range(start_day, end_day + 1):
            ListOfDays.append(str(i).zfill(2))

    ListOfMonths = []
    for i in range(start_month, end_month + 1):
        ListOfMonths.append(str(i).zfill(2))

    if start_month != end_month:
        # Find the month with the highest number of days
        max_days = 0
        for month in ListOfMonths:
            days_in_month = calendar.monthrange(year, int(month))[1]
            if days_in_month > max_days:
                max_days = days_in_month
        
        # Generate the list of all days for the month with the highest number of days
        ListOfDays = [str(day).zfill(2) for day in range(1, max_days + 1)]
    
    ListOfYears = []
    ListOfYears.append(str(year))

    ListOfCoordinates = [config['NorthernLimit'], config['WesternLimit'], config['SouthernLimit'], config['EasternLimit']]
    
    #fileName = f"data_from_{start_month}-{start_day}-{year}_to_{end_month}-{end_day}-{year}.nc"

    if config['area'] == "1": # whole available region data

        dataset = "reanalysis-era5-single-levels"
        request = {
            'product_type': ['reanalysis'],
            'year': ListOfYears,
            'month': ListOfMonths,
            'day': ListOfDays,
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'data_format': 'netcdf',
            'download_format': 'unarchived',
            'variable': ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature', '2m_temperature', 
                         '100m_u_component_of_wind', '100m_v_component_of_wind', 'total_sky_direct_solar_radiation_at_surface', 
                         'high_cloud_cover', 'low_cloud_cover', 'medium_cloud_cover', 'total_cloud_cover', 'geopotential', 
                         'surface_solar_radiation_downwards']
        }

    
    else: # sub-region data
        dataset = "reanalysis-era5-single-levels"
        request = {
            'product_type': ['reanalysis'],
            'year': ListOfYears,
            'month': ListOfMonths,
            'day': ListOfDays,
            'time': ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00',
                    '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'],
            'data_format': 'netcdf',
            'download_format': 'unarchived',
            'variable': ['10m_u_component_of_wind', '10m_v_component_of_wind', '2m_dewpoint_temperature', '2m_temperature', 
                         '100m_u_component_of_wind', '100m_v_component_of_wind', 'total_sky_direct_solar_radiation_at_surface', 
                         'high_cloud_cover', 'low_cloud_cover', 'medium_cloud_cover', 'total_cloud_cover', 'geopotential', 
                         'surface_solar_radiation_downwards'],
            'area': ListOfCoordinates
        }

    # NOTE: Change the key to your own API key from ERA5 website
    client = cdsapi.Client(
        url="https://cds-beta.climate.copernicus.eu/api",
        key="YOUR_KEY"
    )

    # Initiate the request and download the file
    response = client.retrieve(dataset, request)
    response.download()  # Download to default location

    # Assuming the file is downloaded in the current working directory
    list_of_files = glob.glob('*.nc')
    if not list_of_files:
        print("No files found in the current working directory.")
        exit(1)

    latest_file = max(list_of_files, key=os.path.getctime)

    # Define the new filename and move the file to the Downloads directory
    new_filename = config['new_filename']
    if os.path.exists(latest_file):
        new_file_path = os.path.join(os.path.expanduser('~/Downloads'), new_filename)
        shutil.move(latest_file, new_file_path)
        print(f"\nFile moved and renamed to: {new_file_path}\n")
    else:
        print("Download file not found.")
        exit(1)

    # Authenticate and upload to Google Drive
    AuthenticateGoogleDrive()
    UploadFileToGoogleDrive(new_file_path)


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#


def to_str(x, lens) -> str:
    if (x // 100) == 0:      return f"{x:.2f}".zfill(lens)
    elif ((-x) // 100) == 0: return f"{x:.2f}".zfill(lens + 1)
    else:                    return f"{x:.2f}"


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#


def clean_data(df: xarray.Dataset) -> tuple[xarray.Dataset, np.ndarray]:
    df = df.drop_vars(['number', 'expver'])
    
    # Calculate speed and direction
    df['sped'] = np.sqrt(df['u10'] ** 2 + df['v10'] ** 2)
    df['sped100'] = np.sqrt(df['u100'] ** 2 + df['v100'] ** 2)
    df['drct'] = np.arctan2(df['u10'], df['v10'])
    
    # Handle temperature and dew point conversion
    df['tcc'].where(df['tcc'].isnull(), (df['hcc'] + df['mcc'] + df['lcc']) / 3)
    df['t2m'] = np.round((df['t2m'] - 273.15) * 9 / 5 + 32 + 115)  # convert to degF with 115 offset
    df['d2m'] = np.round((df['d2m'] - 273.15) * 9 / 5 + 32 + 115)  # convert to degF
    
    # Convert speed and cloud cover
    df['sped'] = np.round(df['sped'] * 2.23694)  # convert from mps to mph
    df['tcc'] = np.round(df['tcc'] * 100)  # convert to %
    df['drct'] = np.round(df['drct'] * 180 / np.pi + 180) / 5  # convert to deg
    
    # Check if 'ssrd' and 'fdir' variables exist before processing
    if 'ssrd' in df.variables:
        df['ssrd'] = df['ssrd'] / (3600 * 5)  # J/m^2 => W/m^2
    if 'fdir' in df.variables:
        df['fdir'] = df['fdir'] / (3600 * 5)  # J/m^2 => W/m^2
    
    df['WindSpeed100mph'] = df['sped100'] * 2.23694  # convert from mps to mph
    
    if 'z' in df.variables:
        df['z'] = df['z'] / 9.81  # Something to do with Gravity?
        alt = df['z'].isel(valid_time=0).values.astype(int)  # get the altitude values
    else:
        alt = None
    
    df = df.sortby(['valid_time', 'latitude', 'longitude'])


    if 'ssrd' in df.variables and 'fdir' in df.variables:
        df = df.rename({
            't2m': 'tempF',
            'd2m': 'DewPointF',
            "sped": "WindSpeedmph",
            "drct": "WindDirection",
            'tcc': 'CloudCoverPerc',
            'ssrd': 'GlobalHorizontalIrradianceWM2',
            'fdir': 'DirectHorizontalIrradianceWM2'
        })
        
        df = df.drop_vars(["u10", "v10", "u100", "v100", "hcc", "mcc", "lcc", "sped100", "z"])
        
        df = df.transpose('valid_time', 'latitude', 'longitude')
        
        df = df.astype({
            'tempF': 'int16',
            'DewPointF': 'int16',
            'WindSpeedmph': 'int16',
            'WindDirection': 'int16',
            'CloudCoverPerc': 'int16',
            'WindSpeed100mph': 'int16',
            'GlobalHorizontalIrradianceWM2': 'int16',
            'DirectHorizontalIrradianceWM2': 'int16'
        })
        
        df_new_columnlist = [
            "tempF",
            "DewPointF",
            "WindSpeedmph",
            "WindDirection",
            "CloudCoverPerc",
            "WindSpeed100mph",
            "GlobalHorizontalIrradianceWM2",
            "DirectHorizontalIrradianceWM2"
        ]
        
        df = df[df_new_columnlist]
        df = df.fillna(-255)

    else:
        df = df.rename({
            't2m': 'tempF',
            'd2m': 'DewPointF',
            "sped": "WindSpeedmph",
            "drct": "WindDirection",
            'tcc': 'CloudCoverPerc'
        })
        
        df = df.drop_vars(["u10", "v10", "u100", "v100", "hcc", "mcc", "lcc", "sped100", "z"])
        
        df = df.transpose('valid_time', 'latitude', 'longitude')
        
        df = df.astype({
            'tempF': 'int16',
            'DewPointF': 'int16',
            'WindSpeedmph': 'int16',
            'WindDirection': 'int16',
            'CloudCoverPerc': 'int16',
            'WindSpeed100mph': 'int16'
        })
        
        df_new_columnlist = [
            "tempF",
            "DewPointF",
            "WindSpeedmph",
            "WindDirection",
            "CloudCoverPerc",
            "WindSpeed100mph"
        ]
        
        df = df[df_new_columnlist]
        df = df.fillna(-255)
    
    return df, alt


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#


def xarrayDataset_to_PWW(df: xarray.Dataset, alt: np.ndarray):
    config = load_config()

    lat,lon = df.latitude, df.longitude
    aMinLat = lat.max()
    aMaxLat = lat.min()
    aMinLon = lon.min()
    aMaxLon = lon.max()

    lon,lat =np.meshgrid(lon,lat) # create a grid of lat/lon 

    vfunc5 = np.vectorize(lambda x: to_str(x, 5))
    vfunc6 = np.vectorize(lambda x: to_str(x, 6))
    vfunc_header=np.vectorize(lambda x:  f"+{x}+/b\x00".encode('ascii','replace'))
    lats=vfunc5(lat)
    lons=vfunc6(lon)

    LOC = vfunc_header(np.char.add(lats, lons))
    #print(f"share: {LOC.shape} {LOC[0,0]} {LOC[0,-1]} {LOC[-1,0]} {LOC[-1,-1]}")
    LOC = LOC.flatten('C')

    df_station = pd.read_parquet("station.parquet")
    df_station.sort_values(by=['Latitude', 'Longitude'], inplace=True)

    DATE=(df.valid_time.astype('int64') + 2209075200 * 10**9) / (10**9 * 86400)  # convert to days since 1970-01-01
    aStartDateTimeUTC = DATE.min()
    aEndDateTimeUTC = DATE.max()
    COUNT= len(DATE)

    arr=df.to_array().values
    #print(f"Shape: {arr.shape}")
    arr=arr.transpose(1,0,2,3)
    #print(f"trans Shape: {arr.shape}")

    sta=df_station["ascii_null_terminated_WhoAmI"].values
    country=df_station["ascii_null_terminated_Country2"].values
    state=df_station["ascii_null_terminated_Region"].values

    lon=lon.flatten('C').astype(np.double)
    lat=lat.flatten('C').astype(np.double)
    alt=alt.flatten('C').astype(np.int16)

    LOCs=np.array([lat,lon,alt,sta,country,state]).transpose()
    LOCs.shape
    LOC=len(LOCs)

    # Save the .pww file to the current working directory first
    temp_pww_file_name = f"{config['new_filename'].replace('.nc', '.pww')}"
    temp_pww_file_path = os.path.join(os.getcwd(), temp_pww_file_name)

    aPWWFileName = rf"{config['new_filename'].replace(".nc", ".pww")}"
    aPWWVersion = 1
    LOC_FC: int = 0  # for extra loc variables from table 1
    VARCOUNT: int = 8  # Set this to the number of weather variable types you have

    with open(aPWWFileName, 'wb') as file:
            # ......... VOODOO MAGIC
            file.write(struct.pack('<h', 2001))
            file.write(struct.pack('<h', 8065))
            file.write(struct.pack('<h', aPWWVersion))
            file.write(struct.pack('<d', aStartDateTimeUTC))
            file.write(struct.pack('<d', aEndDateTimeUTC))
            file.write(struct.pack('<d', aMinLat))
            file.write(struct.pack('<d', aMaxLat))
            file.write(struct.pack('<d', aMinLon))
            file.write(struct.pack('<d', aMaxLon))
            file.write(struct.pack('<h', 0))
            file.write(struct.pack('<i', COUNT))    #countNumber of datetime values (COUNT)
            file.write(struct.pack('<i', 3600))
            file.write(struct.pack('<i', LOC)) #Number of weather measurement locations (LOC)
            file.write(struct.pack('<h', LOC_FC)) #Loc_FC # Pack the data into INT16 format and write to stream
            file.write(struct.pack('<h', VARCOUNT))
            file.write(struct.pack('<h', 102))      # Temp in F
            file.write(struct.pack('<h', 104))      # Dew point in F
            file.write(struct.pack('<h', 106))      # Wind speed at surface (10m) in mph
            file.write(struct.pack('<h', 107))      # Wind direction at surface (10m) in 5-degree increments
            file.write(struct.pack('<h', 119))      # Total cloud cover percentage
            file.write(struct.pack('<h', 110))      # Wind speed at 100m in mph
            file.write(struct.pack('<h', 120))      # Global Horizontal Irradiance in W/m^2 divided by 4
            file.write(struct.pack('<h', 121))      # Direct Horizontal Irradiance in W/m^2 divided by 4
            file.write(struct.pack('<h', 8))        # BYTECOUNT
            for row in df_station.index:
                    file.write(struct.pack('<d', df_station['Latitude'][row]))          # Write Latitude (DOUBLE)
                    file.write(struct.pack('<d', df_station['Longitude'][row]))         # Write Longitude (DOUBLE)
                    file.write(struct.pack('<h', df_station['ElevationMeters'][row]))   # Write AltitudeM (INT16)
                    file.write(df_station['ascii_null_terminated_WhoAmI'][row])         # Write Name (CSTRING)
                    file.write(df_station['ascii_null_terminated_Country2'][row])
                    file.write(df_station['ascii_null_terminated_Region'][row])
            file.write(arr.astype(np.uint8).tobytes())
    
    # Move the .pww file to the Downloads folder
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    pww_file_name = f"{config['new_filename'].replace('.nc', '.pww')}"
    pww_file_path = os.path.join(downloads_folder, pww_file_name)
    shutil.move(temp_pww_file_path, pww_file_path)

    # Upload the .pww file
    UploadFileToGoogleDrive(pww_file_path)


#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#
#---------------------------------------------------------------------------------------------------------------------------------------------------------#


def main() -> None:
    config = load_config()

    fetch_data()

    # Define the path to the Downloads directory and the filename
    downloads_dir = os.path.expanduser('~/Downloads')
    file_name = config['new_filename']
    file_path = os.path.join(downloads_dir, file_name)

    # Open the dataset using xarray
    try:
        dataset = xarray.open_dataset(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while opening the dataset: {e}")

    #dataset = xarray.open_dataset(config['new_filename'])

    new_dataset, alt = clean_data(dataset)

    list1 = ["Yes", "yes", "1", "Y", "y"]

    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

    if config['wantCSV'] in list1:
        df = new_dataset.to_dataframe().reset_index()
    
        # Create the full path for the CSV file in the Downloads folder
        csv_file_name = f"{config['new_filename'].replace('.nc', '.csv')}"
        csvfile_path = os.path.join(downloads_folder, csv_file_name)
        
        # Save the DataFrame to a CSV file in the Downloads folder
        df.to_csv(csvfile_path)

        UploadFileToGoogleDrive(csvfile_path)

    xarrayDataset_to_PWW(new_dataset, alt)
