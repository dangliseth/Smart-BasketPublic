import cv2
import numpy as np
import time
from tflite_runtime.interpreter import Interpreter

# Load the TFLite model
model_path = "model.tflite"
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

# Get model input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Open the camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 10)


bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

def load_labels(label_path):
    with open(label_path, 'r') as f:
        return [line.strip() for line in f.readlines()]
    
labels = load_labels('labels.txt')


def preprocess_image(frame, input_shape):
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Resize to the input shape and normalize
    input_data = cv2.resize(gray_frame, (input_shape[1], input_shape[2]))
    input_data = np.expand_dims(input_data, axis=0)
    input_data = np.expand_dims(input_data, axis=-1)
    if input_details[0]['dtype'] == np.float32:
        input_data = np.float32(input_data) / 255.0
    elif input_details[0]['dtype'] == np.uint8:
        input_data = np.uint8(input_data)
    return input_data


# Function to classify a single frame
def classify_frame(interpreter, input_data):
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    return output

# Initialize a variable to store the "baseline" background
def classification():
    baseline = None
    motion_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Apply the background subtraction to detect new items
        fg_mask = bg_subtractor.apply(frame)
        
        # Find the contours of the foreground objects (new items)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if there is a significant motion (new object) in the frame
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Adjust this threshold for object size
                motion_detected = True
                break
        
        if motion_detected:
            # Update the baseline when a new object enters the frame
            if baseline is None:
                baseline = frame.copy()
            
            # Perform image classification only when new motion is detected
            input_data = preprocess_image(frame, input_details[0]['shape'])
            output_data = classify_frame(interpreter, input_data)
            
            # Get the highest confidence prediction
            prediction_index = np.argmax(output_data[0])
            confidence = output_data[0][prediction_index]
            data = None

            # Display prediction only if confidence is high enough
            if confidence > 0.9:  # Adjust confidence threshold as needed
                print(f"New item detected - Prediction: {prediction_index}, Confidence: {confidence}")
                #return str(prediction_index)
                data = str(prediction_index)
            else:
                print("No confident prediction for the new item")
                #return None

        else:
            print("No new items detected, continuing to monitor.")
            #return None
            
        return data
        
        #cv2.imshow('Camera', frame)
    #cv2.imshow('Motion Mask', fgmask)

    # Exit on ESC key
    #if cv2.waitKey(1) & 0xFF == 27:
        #break
        

        #cap.release()
        #cv2.destroyAllWindows()
        
#classification()