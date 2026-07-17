import cv2
import os
import numpy as np
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load YOLOv8n model with simplified error handling
def load_yolo_model():
    try:
        from ultralytics import YOLO
        
        # Get the absolute path to the yolov8n.pt model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        yolov8n_path = os.path.join(project_root, "model", "yolov8n.pt")
        
        # Try to load local yolov8n.pt first
        if os.path.exists(yolov8n_path):
            logger.info(f"Loading YOLOv8n model from: {yolov8n_path}")
            model = YOLO(yolov8n_path)
            logger.info("✅ Successfully loaded local YOLOv8n model")
            return model
        else:
            # Download yolov8n.pt if not found locally
            logger.info("Local YOLOv8n not found, downloading...")
            model = YOLO("yolov8n.pt")
            logger.info("✅ Successfully downloaded and loaded YOLOv8n model")
            return model
        
    except ImportError as e:
        logger.error(f"❌ Failed to import YOLO: {e}. Please check ultralytics installation.")
        return None
    except Exception as e:
        logger.error(f"❌ Error loading YOLOv8n model: {e}. Using mock detection instead.")
        return None

# Initialize YOLOv8n model on module import
model = None
try:
    logger.info("🚀 Initializing YOLOv8n model...")
    model = load_yolo_model()
    if model is not None:
        logger.info("✅ YOLOv8n model loaded successfully - ready for vehicle detection!")
    else:
        logger.warning("⚠️ YOLOv8n model loading failed, will use mock detection")
except Exception as e:
    logger.error(f"❌ Critical error during model initialization: {e}")
    model = None

def preprocess_image(img):
    """Apply preprocessing to enhance vehicle detection"""
    if img is None:
        return None
        
    # Adjust brightness and contrast
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    alpha = 1.5 if mean_brightness < 100 else 1.0  # Increase contrast if too dark
    beta = 50 if mean_brightness < 80 else 20      # Adjust brightness
    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    
    # Apply light Gaussian blur to reduce noise
    img = cv2.GaussianBlur(img, (3, 3), 0)
    
    # Resize to 640x640 while preserving aspect ratio
    h, w = img.shape[:2]
    max_dim = max(h, w)
    scale = 640 / max_dim
    new_w, new_h = int(w * scale), int(h * scale)
    img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Pad to 640x640 with black borders
    padded_img = np.zeros((640, 640, 3), dtype=np.uint8)
    top = (640 - new_h) // 2
    left = (640 - new_w) // 2
    padded_img[top:top + new_h, left:left + new_w] = img
    
    return padded_img

def detect_vehicles(image_path):
    """Detect and count vehicles in an image"""
    if model is None:
        logger.warning("No YOLO model available, using mock detection")
        # Mock detection for debugging: return a random number of vehicles
        import random
        mock_count = random.randint(0, 5)
        logger.info(f"Mock detection for {image_path}: {mock_count} vehicles")
        return mock_count
        
    if not os.path.exists(image_path):
        logger.error(f"Image not found: {image_path}")
        return 0
        
    img = cv2.imread(image_path)
    if img is None:
        logger.error(f"Failed to load image: {image_path}")
        return 0
    
    img = preprocess_image(img)
    if img is None:
        return 0
    
    try:
        results = model(img, conf=0.25, iou=0.45)
        vehicle_classes = [1, 2, 3, 5, 7]  # Bicycle, Car, Motorcycle, Bus, Truck
        vehicle_count = sum(1 for result in results[0].boxes if int(result.cls[0]) in vehicle_classes)
        logger.info(f"Total vehicles detected in {image_path}: {vehicle_count}")
        return vehicle_count
        
    except Exception as e:
        logger.error(f"Error during vehicle detection: {e}")
        return 0