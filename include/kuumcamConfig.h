#define kuumcam_VERSION_MAJOR 1
#define kuumcam_VERSION_MINOR 0

#define KUUMCAM_WIDTH_HD 1920
#define KUUMCAM_HEIGHT_HD 1080

#define KUUMCAM_WIDTH_MAX 3280
#define KUUMCAM_HEIGHT_MAX 2464
 
 #define VIDEO_PIPELINE_SENDER "v4l2src device='/dev/video0' ! videoconvert ! videoscale ! video/x-raw,width=800,height=600 ! vp8enc ! rtpvp8pay ! udpsink host=127.0.0.1 port=5100"
 #define VIDEO_PIPELINE_SENDER_FPS 30
 #define VIDEO_PIPELINE_SENDER_WIDTH 800
 #define VIDEO_PIPELINE_SENDER_HEIGHT 600