from Modules.audio.src.asc import preprob as asc_preprob
from Modules.audio.src.asc import process as asc_process
from Modules.audio.src.asc import feats as asc_feats
from utils import Logging

import os
import requests
import collections
import tensorflow as tf
import webrtcvad
import time

class AudioEventDetection:
    model = None
    result = None
    path = os.path.dirname(os.path.abspath(__file__))

    def __init__(self):
        start_time = time.time()
        model_dir = os.path.join(self.path, 'model')
        self.asc_model_path = os.path.join(model_dir, '3model-183-0.3535-0.9388.tflite')
        self.asc_model = tf.lite.Interpreter(model_path=self.asc_model_path)
        self.asc_model.allocate_tensors()
        end_time = time.time()
        print(Logging.i("Model is successfully loaded - {} sec".format(end_time - start_time)))

    def inference_by_audio(self, data, infos):
        paths = data['paths']
        sub_dirs = data['sub_dirs']

        asc_result = self.inference_asc(paths[1], sub_dirs[1] + "/")
        asc_result["sequence_results"] = self.merge_sequence(asc_result["audio_results"])
        self.result = asc_result

        return self.result

    def inference_asc(self, path, sub_dir):
        model_name = 'audio_scene_classification'
        asc_preprob(path, sub_dir, False)
        files = sorted([_ for _ in os.listdir(sub_dir) if _.endswith('.wav')])
        asc_results = {
            'model_name': model_name,
            'analysis_time': 0,
            'audio_results': []
        }
        start_time = time.time()
        for i, file in enumerate(files):
            if i % 10 == 0:
                print(Logging.i("Processing... (index: {}/{})".format(i, len(files))))
            wavpath = os.path.join(sub_dir, file)
            logmel_data = asc_feats(wavpath)
            i = int(file.split('/')[-1].replace('.wav', ''))
            threshold = 0.5
            result = asc_process(i, threshold, logmel_data, self.asc_model, wavpath)
            asc_results['audio_results'].append(result)
            os.remove(wavpath)
        end_time = time.time()
        asc_results['analysis_time'] = end_time - start_time
        print(Logging.i("Processing time: {}".format(asc_results['analysis_time'])))

        return asc_results

    def merge_sequence(self, result):
        sequence_results = []
        # TODO
        # - return format
        # [
        #     {
        #         "label": {
        #             "description": "class name",
        #             "score": 100 # 추가여부는 선택사항
        #         },
        #         "position": { # 추가여부는 선택사항
        #             "x": 100,
        #             "y": 100,
        #             "w": 100,
        #             "h": 100
        #         },
        #         "start_time": "00:00:00.00",
        #         "end_time": "00:00:30.00"
        #     }
        #     ...
        # ]

        return sequence_results