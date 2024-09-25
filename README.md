# CNC Distance and Plot Visualizer

This project provides a web application to calculate the distance between two specific lines in a CNC file and visualize the corresponding plot. It also allows unit conversions (mm, cm, meters, inches, feet) and provides essential dimensional data.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Technologies Used](#technologies-used)
- [Future Improvements](#future-improvements)
- [License](#license)

## Project Overview

This project allows users to upload CNC files, calculate the distance between specific lines, and plot the coordinates visually. The interface is intuitive, featuring a unit conversion tool and options for clearing the form inputs. This tool is useful for CNC operators or anyone working with G-code files who needs to quickly compute dimensions and see a visual representation of their toolpaths.

## Features

- Upload CNC files and calculate distances between two specific lines.
- Convert distances into different units (mm, cm, meters, inches, feet).
- Visualize CNC file toolpaths as plots.
- Clear form inputs and reset the visualization easily.
- Display CNC file's width and length in the chosen unit.

## Project Structure

```
.
├── api/                   # Backend API directory
│   └── app.py             # Main server-side logic handling CNC file processing and plotting
├── frontend/              # Frontend assets
│   ├── index.html         # Main HTML file
│   ├── styles.css         # CSS for styling the page
│   └── script.js          # JavaScript for handling the file uploads, unit conversion, and plot visualization
├── README.md              # This README file
└── requirements.txt       # Python dependencies for the project
```

### API Folder

- **app.py**: This Python file runs the server. It handles CNC file parsing, calculates distances between specified lines, and serves plots based on toolpath coordinates.

### Frontend Folder

- **index.html**: The web interface for uploading files, entering line numbers, selecting units, and viewing the results.
- **styles.css**: The stylesheet for customizing the layout and design.
- **script.js**: Handles file submission, distance calculation, and fetching the plot image from the backend.

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/your-username/cnc-distance-visualizer.git
cd cnc-distance-visualizer
```

### 2. Install Python dependencies

First, create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Then, install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Run the backend server

```bash
cd api
python app.py
```

The server will start on `http://localhost:5000`.

### 4. Open the frontend

You can now open the `index.html` file located in the `frontend/` folder in your browser to interact with the application. Ensure that the backend is running so that the form submissions can be processed.

## Usage

1. **Upload a CNC file**: Choose a G-code file for analysis.
2. **Enter line numbers**: Specify the start and end line numbers for distance calculation.
3. **Choose units**: Select a unit for the result (e.g., mm, cm, inches).
4. **Submit**: Click the submit button to process the file and display results.
5. **View results**: The distance and plot will be displayed. Dimensional details are shown for the CNC file's width and height.
6. **Clear**: Use the clear button to reset the form and results.

## Technologies Used

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Flask)
- **Plotting**: Matplotlib (for generating CNC plot images)
- **G-code Processing**: Custom Python logic for parsing CNC files

## Future Improvements

- Add validation for the line input fields to ensure valid line numbers.
- Enhance error handling for unsupported or malformed CNC files.
- Improve the user interface for a more modern, responsive design.
- Include more detailed toolpath visualization with zoom and pan options.

## License

This project is licensed under the MIT License.
