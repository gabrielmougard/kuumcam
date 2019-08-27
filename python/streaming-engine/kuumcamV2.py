import cv2
import FaceDetector
import config


def send():
    
    cap = cv2.VideoCapture(0) #open the camera
    global fourcc = cv2.VideoWriter_fourcc(*config.H264_FOURCC)
    global out
    if (config.IS_TEST):
        out = cv2.VideoWriter(config.H264_PIPELINE,fourcc,config.CAP_PROP_FPS_TEST, (config.CAP_PROP_FRAME_WIDTH_TEST,config.CAP_PROP_FRAME_HEIGHT_TEST),True) #ouput GStreamer pipeline
    else: #meaning that we are in prod
        out = cv2.VideoWriter(config.H264_PIPELINE,fourcc,config.CAP_PROP_FPS_PROD, (config.CAP_PROP_FRAME_WIDTH_PROD,config.CAP_PROP_FRAME_HEIGHT_PROD),True) #ouput GStreamer pipeline


    #Facedetector 
    faceDetector = FaceDetector.FaceDetector(config.caffe_model,config.prototxt_file,config.detection_threshold)

    if not out.isOpened():
        print('VideoWriter not opened')
        exit(0)

    while cap.isOpened():
        ret,frame = cap.read()
       
        if ret:
            frame = faceDetector.recognition(frame)


            # Write to pipeline
            out.write(frame)

            if cv2.waitKey(1)&0xFF == ord('q'):
                break

    cap.release()
    out.release()

send()