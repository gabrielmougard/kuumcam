caffe_model           = "../models/res10_300x300_ssd_iter_140000_fp16.caffemodel"
prototxt_file         = "../models/deploy.prototxt"
CAP_PROP_FRAME_WIDTH  = 640
CAP_PROP_FRAME_HEIGHT = 480
CAP_PROP_FPS          = 20
detection_threshold   = 0.125
VP9_COMPRESSION       = "libvpx" #lossless VP9 compression with adaptative bitrate (ABR)
VP8_COMPRESSION       = "libvpx" #lossless VP8 compression
FILENAME_TEST_VP8     = "output_VP8.webm"
FILENAME_TEST_VP9     = "output_VP9.webm"
H264_COMPRESSION      = "libx264" #lossless VP8 compression
FILENAME_TEST_H264    = "output_h264.mp4"

#FFmpeg params for VP8/VP9 encoding
VP8_PARAMS = {"-c:v":"libvpx","-qmin":0,"-qmax":50,"-crf":5,"-b:v":"1M","-filter:v": "setpts=4.0*PTS" }

##

