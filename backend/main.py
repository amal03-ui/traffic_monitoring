import sys
import os

# Add the parent directory to sys.path so 'backend' can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask_cors import CORS
from flask import Flask, request, jsonify, send_from_directory
from backend.image_processing import detect_vehicles
from backend.signal_control import decide_signal, mark_initialized
import logging
import time
from concurrent.futures import ThreadPoolExecutor
import traceback

# Configure logging for detailed debugging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder="../frontend")
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

IMAGES_DIR = "../images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@app.route('/')
def index():
    logger.debug("Attempting to serve index.html from ../frontend")
    index_path = os.path.join('../frontend', 'index.html')
    if not os.path.exists(index_path):
        logger.error(f"index.html not found at {index_path}")
        return "index.html not found", 404
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    logger.debug(f"Serving static file: {path} from ../frontend")
    return send_from_directory('../frontend', path)

def process_image(direction, file):
    try:
        temp_path = os.path.join(IMAGES_DIR, f"temp_{direction}_{int(time.time())}.jpg")
        file.save(temp_path)
        count = detect_vehicles(temp_path)
        return direction, count, temp_path
    except Exception as e:
        logger.error(f"Error processing image for {direction}: {str(e)}")
        logger.debug(traceback.format_exc())
        return direction, 0, temp_path if 'temp_path' in locals() else None

@app.route("/backend/process", methods=["OPTIONS", "POST"])
def process_images():
    if request.method == "OPTIONS":
        response = jsonify({"status": "success"})
        response.headers.update({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        })
        return response
    
    logger.info("Received request at /backend/process")
    logger.debug(f"Request files: {list(request.files.keys())}")
    
    if not request.files:
        logger.error("No files uploaded")
        return jsonify({"error": "No files uploaded"}), 400
    
    start_time = time.time()
    files = request.files
    vehicle_counts = {}
    processed_files = []
    
    # Initialize vehicle counts for all directions
    valid_directions = ["north", "south", "west", "east"]
    for direction in valid_directions:
        vehicle_counts[direction] = 0
    
    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for direction in valid_directions:
                if direction in files and files[direction]:
                    file = files[direction]
                    if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                        logger.error(f"Invalid file type for {direction}: {file.filename}")
                        continue
                    if file.content_length and file.content_length > 5 * 1024 * 1024:
                        logger.error(f"File too large for {direction}: {file.filename}")
                        continue
                    futures.append(executor.submit(process_image, direction, file))
                else:
                    logger.warning(f"No image uploaded for {direction}, defaulting to 0")
            
            for future in futures:
                direction, count, temp_path = future.result()
                vehicle_counts[direction] = count
                if temp_path:
                    processed_files.append(temp_path)
                logger.info(f"Processed {direction}: {count} vehicles")
    
        # Compute signals and timing info
        signals, timing_info = decide_signal(vehicle_counts)
        
        # Mark signals as initialized after first successful processing
        if any(vehicle_counts.values()) > 0 or processed_files:
            mark_initialized()
        
        # Ensure timing_info has the expected structure
        timing_info = {
            "remaining_time": timing_info.get("remaining_time", 0),
            "current_green": timing_info.get("current_green", "").lower(),
            "visited_roads": timing_info.get("visited_roads", [])
        }
        
        # Validate current_green value
        if timing_info["current_green"] and timing_info["current_green"] not in valid_directions:
            logger.warning(f"Invalid current_green value: {timing_info['current_green']}, defaulting to empty")
            timing_info["current_green"] = ""
    
    except Exception as e:
        logger.error(f"Error during image processing or signal decision: {str(e)}")
        logger.debug(traceback.format_exc())
        signals = {direction: "red" for direction in valid_directions}
        timing_info = {
            "remaining_time": 0,
            "current_green": "",
            "visited_roads": []
        }
    finally:
        # Clean up temporary files
        for temp_file in processed_files:
            try:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
            except Exception as e:
                logger.warning(f"Failed to remove temp file {temp_file}: {e}")
    
    processing_time = time.time() - start_time
    logger.info(f"Request processing time: {processing_time:.2f} seconds")
    logger.debug(f"Final Vehicle Counts: {vehicle_counts}")
    logger.debug(f"Final Signals: {signals}")
    logger.debug(f"Timing Info: {timing_info}")
    
    response = jsonify({
        "traffic_signals": signals,
        "vehicle_counts": vehicle_counts,
        "timing_info": timing_info,
        "processing_time": f"{processing_time:.2f} seconds"
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    logger.debug("Sending response to frontend")
    return response

@app.route("/backend/test", methods=["GET"])
def test_server():
    logger.debug("Received request at /backend/test")
    response = jsonify({
        "status": "Server is running correctly",
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == "__main__":
    logger.info("Starting Flask server on http://0.0.0.0:5000")
    app.run(debug=True, host="0.0.0.0", port=5000, threaded=True)