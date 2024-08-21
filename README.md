# Command Line Interface for PWW File Generation


## Overview

This Command Line Interface (CLI) program, named **Friday**, assists users in generating PWW files by converting either `.NC` or `.CSV` files (`.CSV` not available right now). The program allows users to specify various parameters, such as date ranges and geographical areas, to fetch data and perform the conversion.


## Features

- **Convert `.NC` to `.PWW`:** Fetch data from the ERA5 website and convert it to `.PWW` format.
- **Convert `.CSV` to `.PWW`:** Convert existing `.CSV` files to `.PWW` format. (`Not Available right now`)
- **User-friendly prompts:** The program guides users through each step with intuitive prompts.
- **Automatic Upload:** The `.nc` files, `.csv` files, and `.pww` files are automatically uploaded to their respective folders in Google Drive, ensuring that your local directory remains clean.


## The files are also locally download on your laptop/computer. They are dowloaded in your "Downloads" folder, which is a standard directory(folder) on most operating systems.


## Accessing Files in Google Drive (PLEASE ACCESS THE LINKS WITH YOU TAMU EMAIL/BROWSER)

- The files generated and uploaded by the program can be accessed in their respective folders in Google Drive:

- `.NC` to `.PWW` file Conversion [NC to PWW](https://drive.google.com/drive/folders/1uBKENHxrBsRg1hSmyP9oBHXLFA0daM-s)
    - `.NC` files: [NC Files](https://drive.google.com/drive/folders/1Mrad-YkHVs83tHgmijfXeMhZMYEDST8X)
    - `.CSV` files: [CSV Files](https://drive.google.com/drive/folders/1DJDMhU0yquKpnceuEYWlOCl20tA9HGjc)
    - `.PWW` files: [PWW Files](https://drive.google.com/drive/folders/1gMOF2yw_rdOayxtqEFP1Hch8tbkH2EJB)

## Installation

Before running the program, ensure you have the required Python packages installed. You can install them using the following command:

```bash
pip install -r requirements.txt
```


## Running the Program

To run the program, use the following command in your terminal:

```bash
python CL_interface.py