from core.gears import NetGear
from core.gears import WriteGear
import config
import cv2

cap_receive = cv2.VideoCapture('udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)

options = {"flag": 0, "copy" : False, "track" : False}
output_params = config.VP8_PARAMS
client = NetGear(address = '127.0.0.1', port = '5454', protocol = 'tcp',  pattern = 0, receive_mode = True, logging = True, **options) #Define netgear clinet at Server IP address
writer = WriteGear(output_filename = config.FILENAME_TEST_VP8, compression_mode = True, logging = True, **output_params) #Define writer with output filename FILENAME_TEST_VP8

while True:
    #receive frame from the network
    #frame = client.recv()
    ret,frame = cap_receive.read()
    if frame is None:
        break

    cv2.imshow("Received frame",frame)
    #writer.write(frame)
    key = cv2.waitKey(1) & 0xFF
    # check for 'q' key-press
    if key == ord("q"):
		#if 'q' key-pressed break out
		break

# close output window
cv2.destroyAllWindows()
# safely close client
client.close()