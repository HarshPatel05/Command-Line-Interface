import click
import json
import os
from datetime import datetime, timedelta
import NC_to_PWW

config_file = 'config.json'

def save_config(data):
    with open(config_file, 'w') as f:
        json.dump(data, f)

@click.command()
def mycommand():

    click.echo()

    click.echo("HOWDY!! :)\n")

    click.echo("My name is Friday. I can help you generate PWW files. Please select which type of file conversion you want:")
    click.echo("1) .NC to .PWW")
    click.echo("2) .CSV to .PWW\n")

    conversion = click.prompt("Please type the prefered option (1 or 2)", type=str)
    click.echo()

    if conversion != "1" and conversion != "2":
        while conversion != "1" and conversion != "2":
            conversion = click.prompt(f"!!ERROR!! {conversion} is an invalid option. Type '1' to convert from .NC to .PWW or type '2' to convert from .CSV to .PWW", type=str)
            click.echo()
    
    if conversion == "1":
        click.echo("You have chosen to convert .NC file to .PWW file. Inorder for me pull the .NC file from the ERA5 website and then perform this conversion, I will need some information on the .NC file.\n")

        wantCSV = click.prompt("Do you want the .CSV file when converting from .NC file to .PWW", type=str)
        click.echo()

        list1 = ["Yes", "yes", "1", "Y", "y"]
        list2 = ["No", "no", "0", "N", "n"]

        if wantCSV not in list1 and wantCSV not in list2:
            while wantCSV not in list1 and wantCSV not in list2:
                wantCSV =  click.prompt(f"!!ERROR!! {wantCSV} is an invalid option. Is the .csv file in the same directory as this python file? (Input 'yes' or 'no')", type=str)
                click.echo()

        while True:
            start_date = click.prompt("Enter the Start Date of the .NC file (MM-DD-YYYY)", type=str)
            end_date = click.prompt("Enter the End Date of the .NC file (MM-DD-YYYY)", type=str)
            click.echo()

            try:
                start_date = datetime.strptime(start_date, "%m-%d-%Y")
                end_date = datetime.strptime(end_date, "%m-%d-%Y")

                if start_date > end_date:
                    click.echo("!!ERROR!! Start Date cannot be greater than the End Date.")
                    continue

                lowerEndDate = datetime(1940, 1, 1)
                higherEndDate = datetime(datetime.now().year, datetime.now().month, datetime.now().day) - timedelta(days=7)
                if start_date < lowerEndDate or end_date > higherEndDate:
                    click.echo(f"!!ERROR!! Either your start date or end date is invalid/out of bounds. Data avaiable from {lowerEndDate.date()}(YYYY-MM-DD) to {higherEndDate.date()}(YYYY-MM-DD).")
                    continue

                if start_date.year != end_date.year:
                    click.echo("!!ERROR!! You can only pull data from 1 year, the start year and end year must be the same.")
                    continue

                break
            except ValueError:
                click.echo("Invalid date format. Please enter the date in MM-DD-YYYY format.")
            
        click.echo("Please select the area you want the data from: ")
        click.echo("1) Whole available region")
        click.echo("2) Sub-region (Required longitude and latitude)\n")

        area = click.prompt("Please type the prefered option (1 or 2)", type=str)
        click.echo()

        if area != "1" and area != "2":
            while area != "1" and area != "2":
                area = click.prompt(f"!!ERROR!! {area} is an invalid option. Type '1' to select the whole available region or type '2' to select a sub-region", type=str)
                click.echo()
        
        if area == "2":
            click.echo("You have selected to enter a sub-region. The sub-region of the available area will be calculated by providing its limit on latitude and longitude.")
            while True:
                NorthernLimit = click.prompt("Enter the Northern Limit (Latitude)", type=float)
                SouthernLimit = click.prompt("Enter the Southern Limit (Latitude)", type=float)
                WesternLimit = click.prompt("Enter the Western Limit (Longitude)", type=float)
                EasternLimit = click.prompt("Enter the Eastern Limit (Longitude)", type=float)
                click.echo()

                if (NorthernLimit <= 90.0 and NorthernLimit >= -90.0) and \
                (SouthernLimit <= 90.0 and SouthernLimit >= -90.0) and \
                (WesternLimit <= 180.0 and WesternLimit >= -180.0) and \
                (EasternLimit <= 180.0 and EasternLimit >= -180.0) and \
                (NorthernLimit > SouthernLimit) and \
                (EasternLimit > WesternLimit):
                    break
                else:
                    click.echo("Invalid input. Please enter the limits within the correct range.")
                    click.echo("Latitude must be between -90.0 and 90.0.")
                    click.echo("Longitude must be between -180.0 and 180.0.")
                    click.echo("Northern Limit must be greater than or equal to Southern Limit.")
                    click.echo("Eastern Limit must be greater than or equal to Western Limit.")
                    click.echo()
        
         # Generate the filename based on start and end dates
        new_filename = f"data_from_{start_date.strftime('%m-%d-%Y')}_to_{end_date.strftime('%m-%d-%Y')}.nc"

        data = {
            'conversion': conversion,
            'start_date': start_date.strftime("%m-%d-%Y"),
            'end_date': end_date.strftime("%m-%d-%Y"),
            'area': area,
            'NorthernLimit': NorthernLimit if area == "2" else None,
            'SouthernLimit': SouthernLimit if area == "2" else None,
            'WesternLimit': WesternLimit if area == "2" else None,
            'EasternLimit': EasternLimit if area == "2" else None,
            'new_filename': new_filename,
            'wantCSV': wantCSV
        }

        save_config(data)

        NC_to_PWW.main()

                
    else:
        # click.echo("Conversion from .CSV to .PWW is not available at moment. Sorry! :(")
        click.echo("You have chosen to convert .CSV file to .PWW file.\n")

        csvName = click.prompt("What is the name of the csv file that you want to convert (inlcude .csv at the end)", type=str)
        click.echo()

        if csvName.endswith(".csv") == False:
            while csvName.endswith(".csv") == False:
                csvName = click.prompt("!!ERROR!! Invalid filename or file type! The filename should end with '.csv'. Please enter a valid filename", type=str)
                click.echo()
        
        FileInDirectory =  click.prompt("Is the .csv file in the same directory as this python file", type=str)
        click.echo()

        list1 = ["Yes", "yes", "1", "Y", "y"]
        list2 = ["No", "no", "0", "N", "n"]

        if FileInDirectory not in list1 and FileInDirectory not in list2:
            while FileInDirectory not in list1 and FileInDirectory not in list2:
                FileInDirectory =  click.prompt(f"!!ERROR!! {FileInDirectory} is an invalid option. Is the .csv file in the same directory as this python file? (Input 'yes' or 'no')", type=str)
                click.echo()

        if FileInDirectory in list1:
            cwd = os.getcwd()
            NewFilePath = cwd + "\\" + csvName
            if os.path.exists(NewFilePath):
                click.echo(f"FOUND IT!! The file named {csvName} exists in your current working directory.\n")
            else:
                click.echo(f"!!! The file named {csvName} does not exists in your current working directory. !!!\n")
            
        else:
            FilePath = click.prompt("Enter the file path where the csv exists", type=str)
            click.echo()

            doesExist = os.path.exists(FilePath)

            if doesExist == True:
                click.echo(f"The file path that you entered was {FilePath}\n")
            else:
                while doesExist == False:
                    FilePath = click.prompt(f"!!ERROR!! File Path you entered does not exists. Please enter a valid File Path", type=str)
                    doesExist = os.path.exists(FilePath)
                    click.echo()
            
            NewFilePath = FilePath + "\\" + csvName
            click.echo(NewFilePath)

            if os.path.exists(NewFilePath):
                click.echo(f" FOUND IT!! The file named {csvName} exists in the given filepath.\n")
            else:
                click.echo(f" !!! The file named {csvName} does not exists in the give filepath. !!!\n")
    
        data = {
            'conversion': conversion,
            'csvName': csvName,
            'NewFilePath': NewFilePath
        }
        save_config(data)    


    click.echo()
    click.echo("CONVERSION SUCCESSFUL, GOODBYE!! :)\n")

if __name__ == '__main__':
    mycommand()