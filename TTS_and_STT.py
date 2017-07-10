#!/usr/bin/env python
# coding=utf-8
import pickle
import subprocess
import copy
import os
from google.cloud import speech
import io
from watson_developer_cloud import SpeechToTextV1, TextToSpeechV1

gs2t = speech.Client()
access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzY29wZSI6Imh0dHBzOi8vc3BlZWNoLnBsYXRmb3JtLmJpbmcuY29tIiwic3Vic2NyaXB0aW9uLWlkIjoiMDdjOTgxYzc3OWM1NDRhZGE0YTczYWJjZjhkOTQwNTMiLCJwcm9kdWN0LWlkIjoiQmluZy5TcGVlY2guRjAiLCJjb2duaXRpdmUtc2VydmljZXMtZW5kcG9pbnQiOiJodHRwczovL2FwaS5jb2duaXRpdmUubWljcm9zb2Z0LmNvbS9pbnRlcm5hbC92MS4wLyIsImF6dXJlLXJlc291cmNlLWlkIjoiL3N1YnNjcmlwdGlvbnMvYThmYjkzMjItN2JmMS00MmU4LWFlMDEtYTk0ZDlmMmE3ZmVjL3Jlc291cmNlR3JvdXBzL1RQUEgvcHJvdmlkZXJzL01pY3Jvc29mdC5Db2duaXRpdmVTZXJ2aWNlcy9hY2NvdW50cy9jaHJpc3RpYW4iLCJpc3MiOiJ1cm46bXMuY29nbml0aXZlc2VydmljZXMiLCJhdWQiOiJ1cm46bXMuc3BlZWNoIiwiZXhwIjoxNDk5NjQzMTY2fQ.nyEkxqQQEJM2Qa6CiKcW2ndrexiGgS3VmCBFJG4lxvM~'

stt = SpeechToTextV1(username='312048ab-670b-44dd-9df6-6cc8186da695', password='jP2BmFpK6YZW')
tts = TextToSpeechV1(username='f4501711-7f21-46c8-aaf6-a242a559bac4', password='6V4vm6ZFNSny')
# [END import_libraries]


def speech_to_text_google(speech_file):
    """Transcribe the given audio file."""
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()
        audio_sample = gs2t.sample(
            content=content,
            source_uri=None,
            encoding='FLAC',
            sample_rate_hertz=44100)

    try:
      alternatives = audio_sample.recognize('es-AR')
    except ValueError:
      return ''
    return alternatives[0].transcript

def speech_to_text(filename, stt=stt):
  audio_file = open(filename, "rb")
  ibm_recognized = stt.recognize(audio_file,
                                 content_type="audio/wav",
                                 model="es-ES_BroadbandModel",
                                 timestamps="true",
                                 max_alternatives="1",
                                 smart_formatting=True)

  if len(ibm_recognized['results']) != 0 and len(ibm_recognized['results'][0]['alternatives']) != 0:
    ibm_recognized = ibm_recognized['results'][0]['alternatives'][0]['transcript']
  else:
    ibm_recognized = ''
  return(ibm_recognized)

# Síntesis del texto 'text', especificando cambios en tasa de habla y f0, ambos en
# porcentaje respecto del default del sistema. El resultado se guarda en 'filename'.
# Es posible que el wav generado tenga mal el header, lo cual se arregla con:
# sox -r 22050 filename.wav tmp.wav && mv tmp.wav filename.wav
def text_to_speech(filename, text, rate_change="+0%", f0mean_change="+0%", tts=tts):
  ssml_text = '<prosody rate="%s" pitch="%s"> %s </prosody>' % (rate_change, f0mean_change, text)
  with open(filename, 'wb') as audio_file:
    audio_file.write(tts.synthesize(ssml_text,
                                    accept='audio/wav',
                                    voice="es-US_SofiaVoice"))
    audio_file.close()


if __name__ == "__main__":
  # Probamos la síntesis...
	#text_to_speech("prueba.wav", "alvarez thomas al 2325", rate_change="+0%", f0mean_change="+0%")

	# Y ahora probamos el reconocimiento...
	#print(speech_to_text("prueba.wav"))
  pass
