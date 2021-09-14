import os

import tensorflow as tf
from Modules.audio.src.aed import preprob as aed_preprob
from Modules.audio.src.aed import process as aed_process
from Modules.audio.src.aed import feats as aed_feats
from utils import Logging


class AudioEventDetection:
    model = None
    result = None
    path = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        model_dir = os.path.join(self.path, 'model')
        self.aed_model_path = os.path.join(model_dir, '11model-035-0.6208-0.8758.tflite')

        self.aed_model = tf.lite.Interpreter(model_path=self.aed_model_path)

        self.aed_model.allocate_tensors()

    def inference_by_audio(self, data, infos):
        paths = data['paths']
        sub_dirs = data['sub_dirs']
        file_list = data['file_lists']

        result = []

        # AED(Audio Event Detection)
        aed_result = self.inference_aed(paths[0], sub_dirs[0] + "/")
        result.append(aed_result)

        self.result = result

        return self.result

    def inference_aed(self, path, sub_dir):
        model_name = 'audio_event_detection'
        aed_preprob(path, sub_dir, False)
        files = sorted([_ for _ in os.listdir(sub_dir) if _.endswith('.wav')])
        aed_results = {
            'model_name': model_name,
            'model_result': []
        }
        for i, file in enumerate(files):
            if i % 50 == 0:
                print(Logging.i("{} {}/{}".format(model_name, i, len(files))))
            wavpath = os.path.join(sub_dir, file)
            logmel_data = aed_feats(wavpath)
            i = int(file.split('/')[-1].replace('.wav', ''))
            threshold = 0.5
            result = aed_process(i, threshold, logmel_data, self.aed_model, wavpath)
            aed_results['model_result'].append(result)
            os.remove(wavpath)
        return aed_results