import cv2
import FaceDetector
import config


def send():
    
    cap = cv2.VideoCapture(0) #open the camera
    fourcc = cv2.VideoWriter_fourcc(*'X264')
  
    out = cv2.VideoWriter('appsrc ! videoconvert ! x264enc tune=zerolatency noise-reduction=10000 bitrate=2048 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5000',fourcc,config.CAP_PROP_FPS, (1280,720),True) #ouput GStreamer pipeline

    #Facedetector 
    faceDetector = FaceDetector.FaceDetector(config.caffe_model,config.prototxt_file,config.detection_threshold)

    if not out.isOpened():
        print('VideoWriter not opened')
        exit(0)

    while cap.isOpened():
        ret,frame = cap.read()
       
        if ret:
            frame = faceDetector.recognition(frame)

            #color space conversion
            #frameRGB = cv2.cvtColor(frame,cv2.COLOR_YUV2RGB)
            #

            # Write to pipeline
            out.write(frame)

            if cv2.waitKey(1)&0xFF == ord('q'):
                break

    cap.release()
    out.release()

send()