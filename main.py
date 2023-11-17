import numpy as np
import tensorflow as tf
from tensorflow.keras import models
from recording_helper import record_audio, terminate
from tf_helper import preprocess_audiobuffer
import pathlib

commands = ['_background_noise_', 'background', 'eden', 'marvin', 'off', 'on']

loaded_model = models.load_model("model/saved")

def predict_mic():
    audio = record_audio()
    spec = preprocess_audiobuffer(audio)
    prediction = loaded_model(spec)
    label_pred = np.argmax(prediction, axis=1)
    command = commands[label_pred[0]]
    print("Predicted:", command)

if __name__ == "__main__":
    while True:
        predict_mic()
