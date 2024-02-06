import cv2

def cameraCheck(url=None):
    cam_status = False
    msg = 'The camera source is inaccessible'

    if url.isdigit():
        url = int(url)

    cap = cv2.VideoCapture(url)
    ret, frame = cap.read()
    cap.release()
    if ret:
        cam_status = True
        msg = 'The camera source is accessible'
    return cam_status, msg, frame