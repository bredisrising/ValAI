import dxcam
from PIL import Image
import time
import cv2

camera = dxcam.create()


camera.start(target_fps=20)

for i in range(1000):
    start = time.perf_counter()
    image = camera.get_latest_frame()
    # cv2.imshow("test", image)
    # if cv2.waitKey(1) & 0xFF == ord("q"):
    #     cv2.destroyAllWindows()
    #     break
    end = time.perf_counter()
    print(1/(end-start))

camera.stop()