#Switching between test env and prod
IS_TEST = True

#DeepLearning models and parameters
caffe_model                = "../models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
prototxt_file              = "../models/deploy.prototxt"
detection_threshold        = 0.125

#camera parameters
CAP_PROP_FRAME_WIDTH_TEST  = 1280
CAP_PROP_FRAME_HEIGHT_TEST = 720
CAP_PROP_FPS_TEST          = 30
CAP_PROP_FRAME_WIDTH_PROD  = 1280 #we will put values according to RPi capabilities
CAP_PROP_FRAME_HEIGHT_PROD = 720
CAP_PROP_PROD               = 30

H264_PIPELINE              = "appsrc ! videoconvert ! x264enc tune=zerolatency noise-reduction=10000 bitrate=2048 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5000"
H264_FOURCC                = "X264"
##

