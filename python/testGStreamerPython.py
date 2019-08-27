import time
import cv2
import FaceDetector
import config
# Cam properties
fps = 25.0
frame_width = 800
frame_height = 600


# Define the gstreamer sink
#gst_str_rtp = "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=127.0.0.1 port=5000"
gst_str_rtp = "appsrc ! videoconvert ! videoscale ! video/x-raw,width=800,height=600 ! vp8enc ! rtpvp8pay ! udpsink host=127.0.0.1 port=5100"
cap = cv2.VideoCapture(gst_str_rtp,cv2.CAP_GSTREAMER)
# Set camera properties
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
cap.set(cv2.CAP_PROP_FPS, fps)
# Check if cap is open
if cap.isOpened() is not True:
    print("Cannot open camera. Exiting.")
    quit()

# Create videowriter as a SHM sink
out = cv2.VideoWriter(gst_str_rtp, 0, fps, (frame_width, frame_height), True)
faceDetector = FaceDetector.FaceDetector(config.caffe_model,config.prototxt_file,config.detection_threshold)
# Loop i
while True:
    # Get the frame
    ret, frame = cap.read()
    frame = faceDetector.recognition(frame)
    # Check
    if ret is True:
        # Flip frame
        frame = cv2.flip(frame, 1)
        # Write to SHM
        out.write(frame)
    else:
        print("Camera error.")
        time.sleep(10)

cap.release()
