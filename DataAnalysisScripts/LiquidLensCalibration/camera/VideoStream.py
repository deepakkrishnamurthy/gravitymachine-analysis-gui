import cv2
from camera.WebcamVideoStream import WebcamVideoStream
#import camera.TIS as TIS

class VideoStream:
    def __init__(self, src=0, CAMERA=3, resolution=(320, 240),framerate=32):
        # check to see if the picamera module should be used
        self.Camera=CAMERA
        
        if self.Camera==1: #pi camera
            # only import the picamera packages unless we are
            # explicity told to do so -- this helps remove the
            # requirement of `picamera[array]` from desktops or
            # laptops that still want to use the `imutils` package
            from .pivideostream import PiVideoStream
            # initialize the picamera stream and allow the camera
            # sensor to warmup
            self.stream = PiVideoStream(resolution=resolution,framerate=framerate)

        # otherwise, we are using OpenCV so initialize the webcam
        # stream
        elif self.Camera==2: #WebCam
            self.stream = WebcamVideoStream(src=src, camResolution=resolution,camFPS=framerate)
        
        elif self.Camera==3: #WebCam
            self.stream = TIS.TIS("07810322",1440,1080,120,True)
        
    def start(self):
        # start the threaded video stream
        return self.stream.start()
    
    def update(self):
        # grab the next frame from the stream
        #no update for the TIS Cam
        self.stream.update()
    
    
    def read(self):
        # return the current frame
        image=self.stream.read()
        if self.Camera==3:
            image=cv2.cvtColor(image,cv2.COLOR_BGRA2BGR)
        return image

    def stop(self):
        # stop the thread and release any resources
        self.stream.stop()
