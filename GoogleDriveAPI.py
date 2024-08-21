from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import os

# Global variable for authenticated GoogleDrive instance
drive = None

def AuthenticateGoogleDrive():
    global drive
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # Creates local webserver and auto handles authentication.
    drive = GoogleDrive(gauth)

def UploadFileToGoogleDrive(file_path): # Specify the file path where the file exsits

    file_name = os.path.basename(file_path)

    # Folder ID for the fixed folder
    if file_name.endswith(".nc"):
        folder_id = "1Mrad-YkHVs83tHgmijfXeMhZMYEDST8X"
    elif file_name.endswith(".csv"):
        folder_id = "1DJDMhU0yquKpnceuEYWlOCl20tA9HGjc"
    elif file_name.endswith(".pww"):
        folder_id = "1gMOF2yw_rdOayxtqEFP1Hch8tbkH2EJB"


    # Create a file object and set its content from the file you want to upload
    file_metadata = {
        'title': file_name,
        'parents': [{'id': folder_id}]
    }
    
    file_to_upload = drive.CreateFile(file_metadata)
    file_to_upload.SetContentFile(file_path)

    # Upload the file.
    file_to_upload.Upload()