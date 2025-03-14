from typing import Dict
from emotion_processor.emotions_recognition.features.emotion_score import EmotionScore
from .emotions.suprise_score import SurpriseScore
from .emotions.angry_score import AngryScore
from .emotions.disgust_score import DisgustScore
from .emotions.sad_score import SadScore
from .emotions.happy_score import HappyScore
from .emotions.fear_score import FearScore
from .emotions.fatigue_score import FatigueScore


class EmotionRecognition:
    def __init__(self):
        self.emotions: Dict[str, EmotionScore] = {
            'Surprise': SurpriseScore(),
            'Angry': AngryScore(),
            'Disgust': DisgustScore(),
            'Sad': SadScore(),
            'Happy': HappyScore(),
            'Fear': FearScore(),
            'Fatigue': FatigueScore(),
        }

    def recognize_emotion(self, processed_features: dict) -> dict:
        scores = {}
        for emotion_name, emotion_score_obj in self.emotions.items():
            scores.update(emotion_score_obj.calculate_score(processed_features))
        return scores
