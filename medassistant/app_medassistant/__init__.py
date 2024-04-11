import sys
import warnings

warnings.simplefilter("ignore")

sys.path.append('../ml_model')
from model import DiseasePredModel

ML_MODEL_VERSION = '1.0'

ml_model = DiseasePredModel('../ml_model')

def get_disease(symptoms: list):
    
    max_symptoms_number = 17
    
    if len(symptoms) > max_symptoms_number:
        symptoms_to_model = symptoms[:max_symptoms_number]
    else:
        symptoms_to_model = symptoms + [float('nan')] * (max_symptoms_number - len(symptoms))

    return ml_model.predict(symptoms_to_model)[0]
