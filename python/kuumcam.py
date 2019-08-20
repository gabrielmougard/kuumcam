import cv2
import numpy as np
import config
import FaceDetector
from core.gears import CamGear
from core.gears import WriteGear
from core.gears import NetGear

options = {"CAP_PROP_FRAME_WIDTH ":config.CAP_PROP_FRAME_WIDTH, "CAP_PROP_FRAME_HEIGHT":config.CAP_PROP_FRAME_WIDTH, "CAP_PROP_FPS ":config.CAP_PROP_FPS} # define tweak parameters
#output_params = {"-vcodec":config.H264_COMPRESSION, "-crf": 0, "-preset": "fast","-filter:v": "setpts=2.0*PTS"} #define (Codec,CRF,preset) FFmpeg tweak parameters for writer
output_params = config.VP8_PARAMS
stream = CamGear(source=0, time_delay=1, logging=True, **options).start() # To open video stream on first index(i.e. 0) device
#cap = cv2.VideoCapture(0)
faceDetector = FaceDetector.FaceDetector(config.caffe_model,config.prototxt_file,config.detection_threshold)
#writer = WriteGear(output_filename = config.FILENAME_TEST_VP8, compression_mode = True, logging = True, **output_params) #Define writer with output filename FILENAME_TEST_VP8
server = NetGear(address = '127.0.0.1',port='5454',protocol='udp',pattern = 2, receive_mode = False, logging = True, **options) #Define netgear at system IP address
count = 0
while(True):
    
    frame = stream.read()
    frame = faceDetector.recognition(frame)
    #cv2.imshow('frame',frame)
    #writer.write(frame)
    server.send(frame)
    print("frame : "+str(count)+" has been sent to zeroMQ !")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    count += 1

cv2.destroyAllWindows()
#close eventual windows
stream.stop()
#safely close the video stream
server.close()
#safely close the writer
