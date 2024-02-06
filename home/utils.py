import cv2


def cameraCheck(url=None):
    status = 'unavailable'
    msg = 'The camera source is inaccessible'

    # if url.startswith('rtsp'):
    #     pass
    # else:
    #     if url.isdigit():
    #         url = url
    #     else:
    #         url = 0

    cap = cv2.VideoCapture(url)
    ret, frame = cap.read()
    if ret:
        status = 'available' 
        msg = 'the url is working fine'
    cap.release()
    return status, msg, frame