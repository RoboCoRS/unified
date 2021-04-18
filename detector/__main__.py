from detector import Detector
import cv2
import click
import os
import redis
import base64
from decouple import config
from imutils.video import FPS

REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT", cast=int)
REDIS_DB = config("REDIS_DB", cast=int)
client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


def frame_to_serial(frame, *, ext='.jpg', size=(80, 60)):
    global client

    resized = cv2.resize(frame, size)
    _, buf = cv2.imencode(ext, resized)
    to_write = base64.b64encode(buf.tobytes())
    client.set("serial_image", to_write)


@click.command()
@click.argument('device', type=click.INT)
@click.option('--frame-size', type=click.STRING, default=None)
@click.option('-d', '--display', is_flag=True)
@click.option('-s', '--serial', is_flag=True)
def main(device, frame_size, display, serial):
    global client

    frame_size = tuple(
        [int(part) for part in frame_size.split('x')]) if frame_size else None
    size = os.get_terminal_size()
    with Detector(device, frame_size) as detector:
        target, target_type = None, None
        while True:
            fps = FPS().start()
            fps.update()
            frame, target, target_type, center_x, center_y = detector.detect(
                target, target_type)
            fps.stop()
            if display and cv2.waitKey(1) == 27:
                break

            fps_text = f'FPS: {fps.fps():0.0f}'
            if center_x and center_y:
                center_text = f'Center: ({center_x:0.3f}, {center_y:0.3f})'
                client.set("center:x", center_x)
                client.set("center:y", center_y)
            else:
                center_text = "Center: None"
                client.delete("center:x")
                client.delete("center:y")

            if display:
                cv2.putText(frame, center_text, (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                cv2.putText(frame, fps_text, (20, 120),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
                cv2.imshow('Detected', frame)
            else:
                print(f'{center_text} {fps_text}'.ljust(
                    size.columns, ' '), end='\r')

        cv2.destroyAllWindows()


try:
    main()
except KeyboardInterrupt or SystemExit:
    cv2.destroyAllWindows()
    pass
