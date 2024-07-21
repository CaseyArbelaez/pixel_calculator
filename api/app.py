import os
import re
import math
import numpy as np
from flask import Flask, request, jsonify, send_from_directory, send_file
import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for Matplotlib
import matplotlib.pyplot as plt
from io import BytesIO

# Constants for coordinate indices
X = 0
Y = 1
I = 2
J = 3
G = 4

app = Flask(__name__, static_folder='../frontend')

def read_gcode_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def parse_nc_gcode(lines, start_line, end_line):
    coordinates = []
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')

    for line in lines[start_line - 1: end_line]:
        if line.startswith('G1') or line.startswith('G0'):
            x_match = re.search(r'X([\-0-9.]+)', line)
            y_match = re.search(r'Y([\-0-9.]+)', line)

            if x_match and y_match:
                x = float(x_match.group(1))
                y = float(y_match.group(1))

                # Check for new min and max values
                x_min = min(x_min, x)
                x_max = max(x_max, x)
                y_min = min(y_min, y)
                y_max = max(y_max, y)

                coordinates.append((x, y))
    
    length = x_max - x_min
    width = y_max - y_min

    return coordinates, length, width

def parse_ngc_gcode(lines, start_line, end_line):
    coordinates = []
    x_min, x_max = float('inf'), float('-inf')
    y_min, y_max = float('inf'), float('-inf')
    
    for line in lines[start_line-1:end_line]:
        if line.startswith(('G00', 'G01', 'G02', 'G03')):
            g_match = re.search(r'G(\d+)', line)
            x_match = re.search(r'X([\-0-9.]+)', line)
            y_match = re.search(r'Y([\-0-9.]+)', line)
            i_match = re.search(r'I([\-0-9.]+)', line)
            j_match = re.search(r'J([\-0-9.]+)', line)

            if not (x_match and y_match):
                continue

            g_type = int(g_match.group(1)) if g_match else None
            x = float(x_match.group(1)) if x_match else None
            y = float(y_match.group(1)) if y_match else None
            i = float(i_match.group(1)) if i_match else None
            j = float(j_match.group(1)) if j_match else None

            coordinates.append((x, y, i, j, g_type))

            # Check for new min and max values
            x_min = min(x_min, x)
            x_max = max(x_max, x)
            y_min = min(y_min, y)
            y_max = max(y_max, y)

    length = x_max - x_min
    width = y_max - y_min

    return coordinates, length, width

# Functions to find the ending line of our nc and ncg files

def find_ngc_g00_line(lines):
    for i, line in enumerate(lines):
        if '(End cutting path id' in line:
            return i + 1  # Return line number (1-indexed)
    return -1  # If not found

def find_nc_g90_line(lines):
    count = 0
    for i, line in enumerate(lines):
        if 'G90' in line:
            count += 1
            if count == 2:
                return i + 1  # Return line number (1-indexed)
    return -1  # If not found

def calculate_total_distance_nc(coordinates):
    total_distance = 0

    for i in range(1, len(coordinates)):
        p1 = coordinates[i - 1]
        p2 = coordinates[i]
        distance = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)
        total_distance += distance

    return total_distance

def calculate_total_distance_ngc(coordinates):
    total_distance = 0

    for i in range(1, len(coordinates)):
        p1 = coordinates[i - 1]
        p2 = coordinates[i]

        if (((p1[G] == 1 or p1[G] == 0) and (p2[G] == 1 or p2[G] == 0)) 
            or (p2[G] == 1 or p2[G] == 0)):
            # Linear move
            distance = math.sqrt((p1[X] - p2[X]) ** 2 + (p1[Y] - p2[Y]) ** 2)
            total_distance += distance
        else:
            # Circular interpolation (G02 or G03)
            center_x = p1[X] + p2[I]
            center_y = p1[Y] + p2[J]

            # Vector from p1 to center of the arc
            v1 = np.array([p1[X] - center_x, p1[Y] - center_y])

            # Vector from p2 to center of the arc
            v2 = np.array([p2[X] - center_x, p2[Y] - center_y])

            # Dot product of v1 and v2
            dot_v1_v2 = np.dot(v1, v2)

            # Norm of v1 and v2
            norm_v1_v2 = np.linalg.norm(v1) * np.linalg.norm(v2)

            # Angle in radians between v1 and v2
            theta_radians = math.acos(dot_v1_v2 / norm_v1_v2)

            # Convert radians to degrees
            theta_degrees = math.degrees(theta_radians)

            # Ratio of the angle to a full circle (360 degrees)
            ratio = theta_degrees / 360.0

            # Radius of the circle
            radius = np.linalg.norm(v1)

            # Arc length
            arc_length = ratio * 2 * math.pi * radius

            # Add arc length to total distance
            total_distance += arc_length

    return total_distance

def plot_arc(ax, start, end, center, g_type):
    start_angle = np.arctan2(start[Y] - center[1], start[X] - center[0])
    end_angle = np.arctan2(end[Y] - center[1], end[X] - center[0])
    
    # Correct for the sweep direction based on G2 (clockwise) or G3 (counterclockwise)
    if g_type == 2:
        if end_angle > start_angle:
            end_angle -= 2 * np.pi
    elif g_type == 3:
        if start_angle > end_angle:
            start_angle -= 2 * np.pi
    
    theta = np.linspace(start_angle, end_angle, 100)
    r = np.sqrt((start[X] - center[0])**2 + (start[Y] - center[1])**2)
    
    x = center[0] + r * np.cos(theta)
    y = center[1] + r * np.sin(theta)
    
    ax.plot(x, y, 'b-')

def plot_gcode_path(coordinates, is_ncg):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    for i in range(1, len(coordinates)):
        p1 = coordinates[i - 1]
        p2 = coordinates[i]
        
        if is_ncg and p2[G] in [2, 3]:
            # Arc move
            center = (p1[X] + p2[I], p1[Y] + p2[J])
            plot_arc(ax, p1, p2, center, p2[G])
        else:
            # Linear move
            ax.plot([p1[X], p2[X]], [p1[Y], p2[Y]], 'b-')

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('G-code Path')

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return buf

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        lines = file.readlines()
        start_line = int(request.form['start_line'])
        end_line = int(request.form['end_line'])
        decoded_lines = [line.decode('utf-8') for line in lines]
        
        # Determine the file type based on extension
        if file.filename.lower().endswith('.nc'):
            coordinates, length, width  = parse_nc_gcode(decoded_lines, start_line, end_line)
            total_distance = calculate_total_distance_nc(coordinates)
            g90_line = find_nc_g90_line(decoded_lines)
            line_info = {'g90_line': g90_line}
            is_ncg = False
        elif file.filename.lower().endswith('.ngc'):
            coordinates, length, width = parse_ngc_gcode(decoded_lines, start_line, end_line)
            total_distance = calculate_total_distance_ngc(coordinates)
            g00_line = find_ngc_g00_line(decoded_lines)
            line_info = {'g00_line': g00_line}
            is_ncg = True
        else:
            return jsonify({'error': 'Unsupported file format. Only .nc and .ngc files are supported.'}), 400
        
        # Prepare data to send back to client
        data = {
            'distance': round(total_distance, 4),
            'coordinates': coordinates,
            **line_info,
            'length': length,
            'width': width,
            'is_ncg': is_ncg
        }
        
        return jsonify(data)

@app.route('/api/plot', methods=['POST'])
def plot():
    data = request.json
    coordinates = data['coordinates']
    is_ncg = data['is_ncg']
    buf = plot_gcode_path(coordinates, is_ncg)
    return send_file(buf, mimetype='image/png')

@app.route('/')
def serve_frontend():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    app.run(debug=True)

