from time import time
import numpy as np
import cv2

from fast_ctypes_screenshots import (
    ScreenshotOfOneMonitor,
)

# a simple benchmark function
def show_screenshot(
    screenshotiter, stop_at_frame=100, quitkey="q", show_screenshot=False
):
    def show_screenshotx():
        cv2.imshow("test", screenshot)
        if cv2.waitKey(1) & 0xFF == ord(quitkey):
            cv2.destroyAllWindows()
            return False
        return True

    framecounter = 0
    fps = 0
    start_time = time()
    for screenshot in screenshotiter:
        if stop_at_frame:
            if framecounter > stop_at_frame:
                break
            framecounter += 1
        if show_screenshot:
            sho = show_screenshotx()
        else:
            sho = True
        fps += 1
        if not sho:
            break
    print(f"fast_ctypes_screenshots: {fps / (time() - start_time)}")
    cv2.destroyAllWindows()

print('starting')

with ScreenshotOfOneMonitor() as screenshot_monitor:
    show_screenshot(screenshot_monitor)

print('done')