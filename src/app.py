# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import os
import subprocess
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

app = Flask(__name__)
CORS(app)  # This allows your frontend to talk to the backend

# This is the main API endpoint that will run your simulation
@app.route('/run-simulation', methods=['POST'])
def run_simulation():
    try:
        # 1. Get the uploaded file from the frontend
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # 2. Save the uploaded file as input.txt in the data directory
        input_file_path = os.path.join('data', 'input.txt')
        uploaded_file.save(input_file_path)
        print(f"Saved uploaded file to {input_file_path}")

        # 3. Run your main.py logic
        # We'll use subprocess to run main.py as a separate process
        # This is cleaner than importing it directly for a first version
        result = subprocess.run([
            sys.executable, 'main.py', input_file_path
        ], capture_output=True, text=True, cwd=os.getcwd())

        # 4. Check if main.py ran successfully
        if result.returncode != 0:
            error_message = f"Backend error: {result.stderr}"
            print(error_message)
            return jsonify({'error': error_message}), 500

        print("Simulation completed successfully!")

        # 5. Read the generated output
        output_file_path = os.path.join('data', 'output.txt')
        output_data = ""
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r') as f:
                output_data = f.read()
        
        # 6. (Optional) Read the log for debugging on the frontend
        log_output = result.stdout

        # 7. Send the results back to the frontend
        return jsonify({
            'success': True,
            'output': output_data,
            'log': log_output
        })

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    # Run the Flask app
    app.run(debug=True, port=5000)