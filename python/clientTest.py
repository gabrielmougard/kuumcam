from core.gears import NetGear
from core.gears import WriteGear
import config
import cv2

options = {"flag": 0, "copy" : False, "track" : False}
output_params = config.VP8_PARAMS
client = NetGear(address = '127.0.0.1', port = '5454', protocol = 'tcp',  pattern = 0, receive_mode = True, logging = True, **options) #Define netgear clinet at Server IP address
writer = WriteGear(output_filename = config.FILENAME_TEST_VP8, compression_mode = True, logging = True, **output_params) #Define writer with output filename FILENAME_TEST_VP8

while True:
    #receive frame from the network
    frame = client.recv()

    if frame is None:
        break

    cv2.imshow("Output frame",frame)
    writer.write(frame)
    key = cv2.waitKey(1) & 0xFF
    # check for 'q' key-press
    if key == ord("q"):
		#if 'q' key-pressed break out
		break

# close output window
cv2.destroyAllWindows()
# safely close client
client.close()