#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
version:
    20220601

last-editor:
    takeshi-s
    
edit-log:
    minimize waiting time for ASR initialization by using running-flag

export GOOGLE_APPLICATION_CREDENTIALS="/Users/takeshi-s/Desktop/tmp/test/asr_tts_dialogue/credential.json"

queue: https://docs.python.org/ja/3/library/queue.html
multiprocessing: https://docs.python.org/ja/3/library/multiprocessing.html
multiprocessing LIFO: https://stackoverflow.com/questions/33691392/how-to-implement-lifo-for-multiprocessing-queue-in-python

TTS client library: https://cloud.google.com/text-to-speech/docs/libraries?hl=ja
TTS supported language: https://cloud.google.com/text-to-speech/docs/voices?hl=ja

ASR infinite streaming tutorial: https://cloud.google.com/speech-to-text/docs/endless-streaming-tutorial?hl=ja
ASR API reference: https://googleapis.dev/python/speech/latest/speech_v1/speech.html

"""
# from matplotlib import pyplot as plt
# from tqdm import tqdm
# import pprint as pp
# import pandas as pd
# import numpy as np
# import traceback
# import shutil
# import math
# import time
# import csv
# import sys
# import os

import re
import sys
import time

from google.cloud import speech
import pyaudio
from six.moves import queue

import google
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio

import json

#import threading
#import queue

import multiprocessing
from multiprocessing.managers import BaseManager
from queue import LifoQueue
class MyManager(BaseManager):
    pass
MyManager.register('LifoQueue', LifoQueue)

# Audio recording parameters
STREAMING_LIMIT = 240000  # 4 minutes
SAMPLE_RATE = 16000
CHUNK_SIZE = int(SAMPLE_RATE / 10)  # 100ms

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
BLACK = "\033[0;30m"
WHITE = "\033[0;37m"

COM_FILE = 'dialogue_flag.json'

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "sample.json"

def main():
     "Main function"

     scenario = ["すももも、ももも、もものうち",
                 "この竹垣に竹立て掛けたのは、竹立て掛けたかったから竹立て掛けた"]
     tts_client = TTS_client()

     asr_client = ASR_client()
     asr_client.start()
    
     for input_text in scenario:
        
#         print("tts input:", input_text)    
#         tts_client.speak(input_text, block = True)
        
         asr_output = asr_client.get_q()
         print("asr output:", asr_output)
    
     asr_client.stop()
    
class ASR_client():
    
    def __init__(self):
        self.final_flag = [False]
        self.last_transcript = ['']
        
        # Opetion1: Threading
        #self.q = queue.LifoQueue()
        
        # Option2: Multiprocessing
        manager = MyManager()
        manager.start()
        self.q = manager.LifoQueue()
        
        print(id(self.final_flag))
        
        with open(COM_FILE, 'w') as f:
            flags = {}
            flags['running'] = False
            json.dump(flags, f)
        
    def check_running(self):
        
        with open(COM_FILE, 'r') as f:
            data = json.load(f)
            
        return data['running']
    
    def start(self):
        
        # Option1: Threading
        #self.thread = threading.Thread(target = self.asr_thread, args=(self.q, ), daemon=True)
        #self.thread.start()
        
        # Option2: Multiprocessing
        self.proc = multiprocessing.Process(target=self.asr_thread, args=(self.q, ))
        self.proc.start()
        
    def stop(self):

        sys.stdout.write(WHITE)
        print("ASR client successfully stopped")
        
        with open(COM_FILE, 'w') as f:
            flags = {}
            flags['running'] = 0
            json.dump(flags, f)
            
        self.proc.terminate()
        
    def get_all_q(self, time_out = None):
        
        #time.sleep(5)
        
        # init_size = self.q.qsize()
        # i = 0
        # while True:
        #     #sys.stdout.write('waiting for input({:04d}), current queue size {}:\n'.format(i, init_size))
        #     time.sleep(0.1)
        #     i+=1
        #     if init_size != self.q.qsize():
        #         break
        tmp_list = []
        while True:
            try:
                utterance = self.q.get(block = False)
                utterance = utterance.split()
                utterance = '。'.join(utterance)
                tmp_list.insert(0, utterance)
            except:
                break
        time.sleep(0.1)
        
        try:
            output = self.q.get(block = True, timeout = time_out)
        except:
            print("No utterance was recognized (timeout:{})".format(time_out))
            output = ""
            
        output = output.split()
        tmp_list.extend(output)
        output = '。'.join(tmp_list)
        
        return output

        
    def get_q(self):
        
        #time.sleep(5)
        
        # init_size = self.q.qsize()
        # i = 0
        # while True:
        #     #sys.stdout.write('waiting for input({:04d}), current queue size {}:\n'.format(i, init_size))
        #     time.sleep(0.1)
        #     i+=1
        #     if init_size != self.q.qsize():
        #         break
        
        output = self.q.get(block=True)
        self.reset_q()
        
        #output.replace('　', '。')
        #output.replace(' ', '。')
        output = output.split()
        print(output)
        output = '。'.join(output)
        
        return output
                
    def reset_q(self):
        while not self.q.empty():
            try:
                self.q.get(False)
            except:
                continue
            self.q.task_done()  
        
        print('Reset queue done:', self.q.qsize())
        
    def asr_thread(self, q):
        
        self.q = q
        
        self.client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=SAMPLE_RATE,
            #language_code="en-US",
            language_code="ja-JP",
            max_alternatives=1,
            #
            #enable_automatic_punctuation = True,
            #
            model = 'phone_call',
            use_enhanced = True,
            #enable_spoken_punctuation = True,
        )
    
        self.streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        self.stream = ResumableMicrophoneStream(SAMPLE_RATE, CHUNK_SIZE)

        print(self.stream.chunk_size)
        sys.stdout.write(RED)
        sys.stdout.write('##############################\n')
        sys.stdout.write('RED: Listening\n')
        sys.stdout.write(GREEN)
        sys.stdout.write('GREEN: Recognition success\n')
        sys.stdout.write('##############################\n')

        
        with self.stream:
    
            while not self.stream.closed:
                #print(self.stream.closed)
                
                sys.stdout.write(YELLOW)
                sys.stdout.write(
                    "\n" + str(STREAMING_LIMIT * self.stream.restart_counter) + ": NEW REQUEST\n"
                )
                
                with open(COM_FILE, 'w') as f:
                    flags = {}
                    flags['running'] = 1
                    json.dump(flags, f)
    
                self.stream.audio_input = []
                audio_generator = self.stream.generator()
    
                requests = (
                    speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator
                )
                responses = self.client.streaming_recognize(self.streaming_config, requests)

                # Now, put the transcription responses to use.
                self.listen_print_loop(responses, self.stream, q)
                    
                if self.stream.result_end_time > 0:
                    self.stream.final_request_end_time = self.stream.is_final_end_time
                self.stream.result_end_time = 0
                self.stream.last_audio_input = []
                self.stream.last_audio_input = self.stream.audio_input
                self.stream.audio_input = []
                self.stream.restart_counter = self.stream.restart_counter + 1
    
                if not self.stream.last_transcript_was_final:
                    sys.stdout.write("\n")
                self.stream.new_stream = True
                
                if self.stream.last_transcript_was_final:
                    self.final_flag[0] = self.stream.last_transcript_was_final
                    self.last_transcript[0] = self.stream.last_transcript
                    
                    
    
    def listen_print_loop(self, responses, stream, q):
        """Iterates through server responses and prints them.
    
        The responses passed is a generator that will block until a response
        is provided by the server.
    
        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.
    
        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.
        """
    
        for response in responses:
    
            if get_current_time() - stream.start_time > STREAMING_LIMIT:
                stream.start_time = get_current_time()
                break
    
            if not response.results:
                continue
    
            result = response.results[0]
    
            if not result.alternatives:
                continue
    
            transcript = result.alternatives[0].transcript
    
            result_seconds = 0
            result_micros = 0
    
            if result.result_end_time.seconds:
                result_seconds = result.result_end_time.seconds
    
            if result.result_end_time.microseconds:
                result_micros = result.result_end_time.microseconds
    
            stream.result_end_time = int((result_seconds * 1000) + (result_micros / 1000))
    
            corrected_time = (
                stream.result_end_time
                - stream.bridging_offset
                + (STREAMING_LIMIT * stream.restart_counter)
            )
            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
    
            if result.is_final:
    
                sys.stdout.write(GREEN)
                sys.stdout.write("\033[K")
                sys.stdout.write(str(corrected_time) + ": " + transcript + "\n")
    
                stream.is_final_end_time = stream.result_end_time
                stream.last_transcript_was_final = True
                q.put(transcript)
                #print(queue_obj.get())
                
                stream.last_transcript = transcript
                self.last_transcript[0] = transcript
                
                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    sys.stdout.write(YELLOW)
                    sys.stdout.write("Exiting...\n")
                    sys.stdout.write(WHITE)
                    stream.closed = True
                    break
    
                if re.search(r"\b(終了|終わり)\b", transcript, re.I):
                    sys.stdout.write(YELLOW)
                    sys.stdout.write("Exiting...\n")
                    sys.stdout.write(WHITE)
                    stream.closed = True
                    break
    
            else:
                sys.stdout.write(RED)
                sys.stdout.write("\033[K")
                sys.stdout.write(str(corrected_time) + ": " + transcript + "\n")
                sys.stdout.flush()
    
                stream.last_transcript_was_final = False

  
class TTS_client():
    
    def __init__(self):
        
        self.client = texttospeech.TextToSpeechClient()    
        self.voice = texttospeech.VoiceSelectionParams(
        #    language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
            name = "ja-JP-Wavenet-B",
        )
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
    def speak(self, input_text, block = True):
        
        #synthesis_input = texttospeech.SynthesisInput(text="Hello, World!")
        self.synthesis_input = texttospeech.SynthesisInput(text=input_text)
        self.response = self.client.synthesize_speech(
            input=self.synthesis_input, voice=self.voice, audio_config=self.audio_config
        )
        
        with open("output.mp3", "wb") as out:
            out.write(self.response.audio_content)
            print('Audio content written to file "output.mp3"')        
        self.sound = AudioSegment.from_file("output.mp3", format="mp3")
        #play(sound)
        
        self.playback = simpleaudio.play_buffer(
            self.sound.raw_data, 
            num_channels=self.sound.channels, 
            bytes_per_sample=self.sound.sample_width, 
            sample_rate=self.sound.frame_rate
        )
        
        if block:
            time.sleep(self.sound.duration_seconds)
            self.playback.stop()
    
    def stop(self):
        
        try:
            self.playback.stop()
        except:
            print("No audio to stop")
    
def get_current_time():
    """Return Current Time in MS."""

    return int(round(time.time() * 1000))


class ResumableMicrophoneStream():
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk_size):
        self._rate = rate
        self.chunk_size = chunk_size
        self._num_channels = 1
        self._buff = queue.Queue()
        self.closed = True
        self.start_time = get_current_time()
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.bridging_offset = 0
        self.last_transcript_was_final = False
        self.new_stream = True
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=self._num_channels,
            rate=self._rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )
        
        self.last_transcript = ''

    def __enter__(self):

        self.closed = False
        return self

    def __exit__(self, type, value, traceback):

        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, *args, **kwargs):
        """Continuously collect data from the audio stream, into the buffer."""

        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        """Stream Audio from microphone to API and to local buffer"""

        while not self.closed:
            data = []

            if self.new_stream and self.last_audio_input:

                chunk_time = STREAMING_LIMIT / len(self.last_audio_input)

                if chunk_time != 0:

                    if self.bridging_offset < 0:
                        self.bridging_offset = 0

                    if self.bridging_offset > self.final_request_end_time:
                        self.bridging_offset = self.final_request_end_time

                    chunks_from_ms = round(
                        (self.final_request_end_time - self.bridging_offset)
                        / chunk_time
                    )

                    self.bridging_offset = round(
                        (len(self.last_audio_input) - chunks_from_ms) * chunk_time
                    )

                    for i in range(chunks_from_ms, len(self.last_audio_input)):
                        data.append(self.last_audio_input[i])

                self.new_stream = False

            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            self.audio_input.append(chunk)

            if chunk is None:
                return
            data.append(chunk)
            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)

                    if chunk is None:
                        return
                    data.append(chunk)
                    self.audio_input.append(chunk)

                except queue.Empty:
                    break

            yield b"".join(data)



##############################
####### Error case 1 #########
##############################
#
### you shouldn't run outside of "if __name__ == '__main__' block"
#
# asr_client = ASR_client()
# asr_client.start()
# asr_output = asr_client.get_q()
# print("asr output:", asr_output)
# asr_client.stop()

##############################
####### Error case 2 #########
##############################
#
### you shouldn't run outside of "if __name__ == '__main__' block, doesn't matter you call function from there"
#
# def test_func():
#     asr_client = ASR_client()
#     asr_client.start()
#     asr_output = asr_client.get_q()
#     print("asr output:", asr_output)
#     asr_client.stop()
# test_func()

if __name__ == '__main__':

    ##############################
    ####### Success case #########
    ##############################
    #
    ### you can run inside of "if __name__ == '__main__' block or inside of function called from "if __name__ == '__main__' "
    #
    # asr_client = ASR_client()
    # asr_client.start()
    # asr_output = asr_client.get_q()
    # print("asr output:", asr_output)
    # asr_client.stop()    

    main()
    