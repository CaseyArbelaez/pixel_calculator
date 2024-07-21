let unit = 'mm';

document.getElementById('upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('file-input').files[0];
    const formData = new FormData();
    formData.append('file', fileInput);
    formData.append('start_line', document.getElementById('start-line').value);
    formData.append('end_line', document.getElementById('end-line').value);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        // Set default unit to mm

        const unitConversions = {
            'mm': 1,
            'cm': 0.1,
            'm': 0.001,
            'in': 0.0393701,
            'ft': 0.00328084
        }

        // Adding event listener for unit toggle

        document.getElementById('unit').addEventListener('change', function() {
            unit = this.value;
        })

        const data = await response.json();

        const fontSize = '24px';

        console.log(data);  // Log response data to console

        const distanceInMM = data.distance;
        const distanceInUnits = distanceInMM * unitConversions[unit]; // Converting mm to desired units
        
        // Display the distance calculation result
        document.getElementById('result').style.display = 'block';
        document.getElementById('distance').textContent = `Distance between lines ${formData.get('start_line')} and ${formData.get('end_line')}: ${distanceInUnits.toFixed(4)} ${unit}`;
        document.getElementById('distance').style.fontSize = fontSize;
        document.getElementById('distance').classList.add('bold-text'); // Add a class for styling

        if (data.g00_line) {
            document.getElementById('end-of-file').textContent = `The last valid line in this file is line ${data.g00_line}`;
        }
        if (data.g90_line) {
            document.getElementById('end-of-file').textContent = `The last valid line in this file is line ${data.g90_line}`;
        }

        // Display Dimensions of the current plot

        const width = data.width * unitConversions[unit];
        const length = data.length * unitConversions[unit];

        document.getElementById('dimensions').textContent = `Dimensions: ${length.toFixed(3)} ${unit} x ${width.toFixed(3)} ${unit} (Length x Height)`;

        
        // Request plot from the server
        const plotResponse = await fetch('/api/plot', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                coordinates: data.coordinates,
                is_ncg: data.is_ncg
            })
        });

        if (!plotResponse.ok) {
            throw new Error(`HTTP error! Status: ${plotResponse.status}`);
        }

        const plotBlob = await plotResponse.blob();
        const plotUrl = URL.createObjectURL(plotBlob);
        
        // Display the plot
        const plotImg = document.getElementById('plot-img');
        plotImg.src = plotUrl;
        plotImg.style.display = 'block';

    } catch (error) {
        console.error('Error:', error);
    }
});

// Add event listener for clear button
document.getElementById('clear-button').addEventListener('click', function() {
    // Clear input fields
    document.getElementById('file-input').value = '';
    document.getElementById('start-line').value = '';
    document.getElementById('end-line').value = '';

    // Hide result section
    document.getElementById('result').style.display = 'none';

    // Clear distance text
    document.getElementById('distance').textContent = '';
    document.getElementById('end-of-file').textContent = '';

    // Clear plot image
    const plotImg = document.getElementById('plot-img');
    plotImg.src = '';
    plotImg.style.display = 'none';
});
