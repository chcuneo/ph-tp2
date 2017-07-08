#!/usr/bin/env python
# coding=utf-8
import pickle
import subprocess
import copy
import os
from watson_developer_cloud import SpeechToTextV1, TextToSpeechV1

stt = SpeechToTextV1(username='312048ab-670b-44dd-9df6-6cc8186da695', password='jP2BmFpK6YZW')
tts = TextToSpeechV1(username='f4501711-7f21-46c8-aaf6-a242a559bac4', password='6V4vm6ZFNSny')

def speech_to_text(filename, stt=stt):
  audio_file = open(filename, "rb")
  ibm_recognized = stt.recognize(audio_file,
                                 content_type="audio/wav",
                                 model="es-ES_BroadbandModel",
                                 timestamps="true",
                                 max_alternatives="1",
                                 smart_formatting=True)
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
	text_to_speech("prueba.wav", "alvarez thomas al 2325", rate_change="+0%", f0mean_change="+0%")

	# Y ahora probamos el reconocimiento...
	print(speech_to_text("prueba.wav"))

