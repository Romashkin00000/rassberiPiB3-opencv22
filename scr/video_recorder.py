

import cv2
import numpy as np
from collections import deque

class VideoRecorder:
    def __init__(self, width, height, fps, buffer_seconds):
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_buffer = deque(maxlen=buffer_seconds * fps)
        self.cap = cv2.VideoCapture(0)

        if not self.cap.isOpened():
            raise Exception("Камера не найдена!")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

    def capture_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Не удалось получить кадр с камеры!")
        self.frame_buffer.append(frame)
        return frame

    def save_video(self, output_path="video.mp4"):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, self.fps, (self.width, self.height))

        for frame in self.frame_buffer:
            out.write(frame)

        out.release()
        return output_path

    def release(self):
        self.cap.release()
