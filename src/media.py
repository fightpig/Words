import datetime
import os
import time
import wave
from pathlib import Path
from threading import Thread
from typing import Tuple

import cv2
import pyaudio
import pygame
from PIL import ImageGrab
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from numpy import array


class AudioRecorder(Thread):
    """录制音频"""

    def __init__(
        self,
        save_dir_path: str | Path,
        save_name: str | Path,
        audio_sampling_rate: int = 48000,  # 音频采样率
        audio_channels: int = 2,  # 采样的音频频道
        audio_format: int = pyaudio.paInt16,  # """音频格式"""
        audio_chunk_size: int = 1024,  # """音频块大小"""
        recorder: str = "pyaudio",  # """使用pyaudio或ffmpeg进行录制"""
        ffmpeg_path: str | Path = r"ffmpeg.exe",  # """ffmpeg.exe的本地路径"""
        **kwargs: dict,
    ):

        super().__init__()

        self.save_dir_path = save_dir_path
        self.save_name = save_name
        self.audio_sampling_rate = audio_sampling_rate
        self.audio_channels = audio_channels
        self.audio_format = audio_format
        self.audio_chunk_size = audio_chunk_size
        self.recorder = recorder
        self.ffmpeg_path = ffmpeg_path

        self._running: bool = True
        self._save_path: str | None = None

    @property
    def save_path(self):
        if self._save_path is None:
            self._save_path = (
                str(Path(self.save_dir_path) / self.save_name / ".wav")
                if not self.save_name.endswith(".wav")
                else str(Path(self.save_dir_path) / self.save_name)
            )
        return self._save_path

    def run(self):
        while True:
            if self._running:
                break
        if self.recorder == "pyaudio":
            print("使用pyaudio进行录音...")
            self.record_by_pyaudio()
        else:
            print("使用ffmpeg进行录音...")
            self.record_by_ffmpeg()

    def record_by_ffmpeg(self):
        raise NotImplementedError
        # cmd = f"""
        #       {self.ffmpeg_path}
        #       -y
        #       -f dshow
        #       -i audio="virtual-audio-capturer"
        #       -ar {self.sampling_rate}
        #       -ac {self.channel}
        #       {self._save_path}
        # """
        # cmd = cmd.replace('\n', '').replace(r'\s+', '')
        # cmd = re.sub(r'\s+', ' ', cmd)
        # while True:
        #     if self.begin_record_audio:
        #         break
        #     os.system(cmd)

    def record_by_pyaudio(self):
        py_audio = None
        stream = None
        wf = None
        try:
            py_audio = pyaudio.PyAudio()
            stream = py_audio.open(
                format=self.audio_format,
                channels=self.audio_channels,
                rate=self.audio_sampling_rate,
                input=True,
                frames_per_buffer=self.audio_chunk_size,
            )
            wf = wave.open(str(self.save_path), "wb")
            wf.setnchannels(self.audio_channels)
            wf.setsampwidth(py_audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.audio_sampling_rate)

            s = time.time()
            print_flag = False
            while self._running:
                print_flag = True if print_flag is False else print_flag
                print(f"Begin to audio recording...") if not print_flag else None

                data = stream.read(self.audio_chunk_size)
                wf.writeframes(data)
            e = time.time()
            print(f"Finished audio recording: {e - s:.3f}秒")
        except Exception as e:
            print(f"An error occurred during audio recording: {e}")
        finally:
            if stream is not None:
                stream.stop_stream()
                stream.close()
            wf.close() if wf is not None else None
            py_audio.terminate() if py_audio is not None else None

    def start_record(self):
        self._running = True

    def stop_record(self):
        self._running = False


class ScreenRecorder(Thread):
    """录屏"""

    def __init__(
        self,
        save_dir_path: str | Path,  # """保存目录"""
        save_name: (
            str | Path
        ),  # """保存名称，视频保存为mp4，保存名称可以带.mp4后缀，也可以不带"""
        video_fps: int = 24,  # """截图频率，每秒截多少张图"""
        video_screen_offset: Tuple[int, int] = (
            0,
            0,
        ),  # """录制屏幕的位置偏移，默认全屏，即从屏幕的左上角，没有偏移"""
        video_screen_size: Tuple[int, int] = (0, 0),  # """录制视频的大小，默认为全屏"""
        recorder: str = "cv2",  # """使用cv2进行录制"""
        ffmpeg_path: str | Path = r"ffmpeg.exe",  # """ffmpeg.exe的本地路径""",
        **kwargs: dict,
    ):

        super().__init__()
        self.save_dir_path = save_dir_path
        self.save_name = save_name
        self.video_fps = video_fps
        self.video_screen_offset = video_screen_offset
        self.video_screen_size = video_screen_size
        self.recorder = recorder
        self.ffmpeg_path = ffmpeg_path
        self._running: bool = True
        self._save_path: str | None = None
        self.kwargs = kwargs

    @property
    def save_path(self):
        if self._save_path is None:
            self._save_path = (
                str(Path(self.save_dir_path) / f"{self.save_name}.mp4")
                if not self.save_name.endswith(".mp4")
                else str(Path(self.save_dir_path) / self.save_name)
            )
        return self._save_path

    def run(self):
        while True:
            if self._running:
                break
        if self.recorder == "cv2":
            self.record_by_cv2()

    def record_by_cv2(self):
        video = None
        try:
            w, h = self.get_screen_size()
            min_x, min_y, max_x, max_y = 0, 0, w, h
            if self.video_screen_size is not None and self.video_screen_size != (w, h):
                w, h = self.video_screen_size
                min_x, min_y = self.video_screen_offset
                max_x, max_y = min_x + w, min_y + h
            video = cv2.VideoWriter(
                self.save_path, cv2.VideoWriter_fourcc(*"mp4v"), self.video_fps, (w, h)
            )  # noqa

            s = time.time()
            print_flag = False
            while self._running:
                print_flag = True if print_flag is False else print_flag
                print(f"Begin to screen recording...") if not print_flag else None
                img = array(ImageGrab.grab(bbox=(min_x, min_y, max_x, max_y)))
                video.write(img)
            e = time.time()
            print(f"Finished screen recording: {e - s}秒")
        except Exception as e:
            print(f"An error occurred during screen recording: {e}")
        finally:
            video.release() if video else None

    @staticmethod
    def get_screen_size() -> Tuple[int, int]:
        """获取屏幕的大小"""
        return ImageGrab.grab().size

    def start_record(self):
        self._running = True

    def stop_record(self):
        self._running = False


class Recorder(Thread):
    """录制视频：
    1 录屏
    2 录音
    3 合并成视频
    """

    def __init__(
        self,
        save_dir_path: str | Path,
        save_name: str | Path,
        audio_sampling_rate: int = 48000,  # 音频采样率
        audio_channels: int = 2,  # 采样的音频频道
        audio_format: int = pyaudio.paInt16,  # """音频格式"""
        audio_chunk_size: int = 1024,  # """音频块大小"""
        audio_recorder: str = "pyaudio",  # """使用pyaudio或ffmpeg进行录制"""
        video_fps: int = 24,  # """截图频率，每秒截多少张图"""
        video_screen_offset: Tuple[int, int] = (
            0,
            0,
        ),  # """录制屏幕的位置偏移，默认全屏，即从屏幕的左上角，没有偏移"""
        video_screen_size: Tuple[int, int] = (0, 0),  # """录制视频的大小，默认为全屏"""
        screen_recorder: str = "cv2",  # """使用cv2进行录制"""
        ffmpeg_path: str | Path = r"ffmpeg.exe",  # """ffmpeg.exe的本地路径""",
        **kwargs: dict,
    ):

        super().__init__()

        self.save_dir_path = save_dir_path
        self.save_name = save_name
        self.audio_sampling_rate = audio_sampling_rate
        self.audio_channels = audio_channels
        self.audio_format = audio_format
        self.audio_chunk_size = audio_chunk_size
        self.audio_recorder = audio_recorder

        self.save_dir_path = save_dir_path
        self.save_name = save_name
        self.video_fps = video_fps
        self.video_screen_offset = video_screen_offset
        self.video_screen_size = video_screen_size
        self.screen_recorder = screen_recorder

        self.ffmpeg_path = ffmpeg_path

        self._save_path: str | None = None
        self._audio_recorder_obj: AudioRecorder | None = None
        self._screen_recorder_obj: ScreenRecorder | None = None
        self.kwargs = kwargs

    @property
    def save_path(self) -> str:
        if self._save_path is None:
            self._save_path = (
                str(Path(self.save_dir_path) / f"{self.save_name}.mp4")
                if not self.save_name.endswith(".mp4")
                else str(Path(self.save_dir_path) / self.save_name)
            )
        return self._save_path

    @property
    def audio_recorder_obj(self):
        if self._audio_recorder_obj is None:
            self._audio_recorder_obj = AudioRecorder(
                save_dir_path=self.save_dir_path,
                save_name=f"{str(datetime.datetime.now().timestamp())}.wav",
                audio_sampling_rate=self.audio_sampling_rate,
                audio_channels=self.audio_channels,
                audio_format=self.audio_format,
                audio_chunk_size=self.audio_chunk_size,
                recorder=self.audio_recorder,
                ffmpeg_path=self.ffmpeg_path,
                **self.kwargs,
            )
        return self._audio_recorder_obj

    @property
    def screen_recorder_obj(self):
        if self._screen_recorder_obj is None:
            self._screen_recorder_obj = ScreenRecorder(
                save_dir_path=self.save_dir_path,
                save_name=f"{str(datetime.datetime.now().timestamp())}.mp4",
                video_fps=self.video_fps,
                video_screen_offset=self.video_screen_offset,
                video_screen_size=self.video_screen_size,
                recorder=self.screen_recorder,
                ffmpeg_path=self.ffmpeg_path,
                **self.kwargs,
            )
        return self._screen_recorder_obj

    def run(self):
        self.audio_recorder_obj.start()
        self.screen_recorder_obj.start()

    def start_record(self):
        self.audio_recorder_obj.start_record()
        self.screen_recorder_obj.start_record()

    def stop_record(self):
        self.audio_recorder_obj.stop_record()
        self.screen_recorder_obj.stop_record()

        with open(Path(self.save_dir_path) / "video.txt", "a+", encoding="utf-8") as f:
            f.write(f"name: {self.save_name}\n")
            f.write(f"wav: {self.audio_recorder_obj.save_path}\n")
            f.write(f"mp4: {self.audio_recorder_obj.save_path}\n")
            f.write("\n")

    def compose(self):
        tmp_audio = AudioFileClip(self.audio_recorder_obj.save_path)
        tmp_video = VideoFileClip(self.screen_recorder_obj.save_path)
        ratio = tmp_audio.duration / tmp_video.duration
        tmp_video = tmp_video.fl_time(lambda t: t / ratio, apply_to=["video"]).set_end(
            tmp_audio.duration
        )
        av = tmp_video.set_audio(tmp_audio)
        av = CompositeVideoClip([av])
        av.write_videofile(
            str(self.save_path), codec="libx264", fps=self.screen_recorder_obj.video_fps
        )
        av.close()
        tmp_video.close()
        tmp_audio.close()

        self.remove_tmp_files()
        print(f"录制完成：{self.save_path}")

    def stop_record_and_compose(self):
        self.stop_record()
        Thread(target=self.compose).start()

    def remove_tmp_files(self):
        if Path(self.audio_recorder_obj.save_path).exists():
            os.remove(self.audio_recorder_obj.save_path)
        if Path(self.screen_recorder_obj.save_path).exists():
            os.remove(self.screen_recorder_obj.save_path)


def test():
    recorder = Recorder(
        save_dir_path=r"D:\nreal\ws\python\NextBetter\src\app", save_name="xxx.mp4"
    )
    recorder.start()
    recorder.start_record()
    time.sleep(10)
    recorder.stop_record()
    recorder.compose()


class Audio:
    def __init__(self):
        pygame.mixer.init()

    def play(self, audio_path: str):  # noqa
        """播放mp3"""
        pygame.mixer.Sound(audio_path).play()


if __name__ == "__main__":
    # Audio().play(r'C:\Users\admin\Desktop\words_app\word-audio-libs\oxford5000\us\abandon.mp3')
    #
    v = Recorder(
        "word-mp4",
        "test.mp4",
        video_screen_offset=(100, 100),
        video_screen_size=(400, 400),
    )
    v.start()
    time.sleep(10)
    v.stop_record()
    v.compose()
