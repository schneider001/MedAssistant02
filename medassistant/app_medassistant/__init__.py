import sys
import warnings
import os

warnings.simplefilter("ignore")

if 'USE_UNIX_SOCKET' in os.environ:
    ml_model_path = '../../ml_model'
else:
    ml_model_path = '../ml_model'

dir_path = os.path.dirname(os.path.realpath(__file__))
ml_model_path = os.path.join(dir_path, ml_model_path)
ml_model_path = os.path.abspath(ml_model_path)


sys.path.append(ml_model_path)

from model import DiseasePredModel

ML_MODEL_VERSION = '1.0'

ml_model = DiseasePredModel(ml_model_path)

def get_disease(symptoms: list):
    
    max_symptoms_number = 17
    
    if len(symptoms) > max_symptoms_number:
        symptoms_to_model = symptoms[:max_symptoms_number]
    else:
        symptoms_to_model = symptoms + [float('nan')] * (max_symptoms_number - len(symptoms))

    return ml_model.predict(symptoms_to_model)[0]
