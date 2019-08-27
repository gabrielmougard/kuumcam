## sender 
gst-launch-1.0 -v v4l2src device="/dev/video0" ! videoconvert ! videoscale ! video/x-raw,width=800,height=600 ! vp8enc ! rtpvp8pay ! udpsink host=127.0.0.1 port=5100

### H264enc
gst-launch-1.0 -v avfvideosrc capture-screen=true ! video/x-raw,framerate=20/1 ! videoscale ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay ! udpsink host=127.0.0.1 port=5000

### H265enc

##receiver

gst-launch-1.0 udpsrc port=5100 caps="application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)VP8-DRAFT-IETF-01, payload=(int)96, ssrc=(uint)2990747501, clock-base=(uint)275641083, seqnum-base=(uint)34810" ! rtpvp8depay ! vp8dec ! autovideosink

### H264dec
gst-launch-1.0 -v udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! autovideosink

### H265dec