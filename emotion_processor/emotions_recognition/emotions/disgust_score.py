from emotion_processor.emotions_recognition.features.weights_emotion_score import WeightedEmotionScore


class DisgustScore(WeightedEmotionScore):
    def __init__(self):
        super().__init__(eyebrows_weight=0.25, eyes_weight=0.25, nose_weight=0.35, mouth_weight=0.15)

    def calculate_eyebrows_score(self, eyebrows_result: str) -> float:
        score = 0.0
        if 'eyebrows together' in eyebrows_result:
            score += 33.33
        if 'right eyebrow: lowered' in eyebrows_result:
            score += 33.33
        if 'left eyebrow: lowered' in eyebrows_result:
            score += 33.33
        return score

    def calculate_eyes_score(self, eyes_result: str) -> float:
        if 'closed eyes' in eyes_result:
            return 100.0
        return 0.0

    def calculate_nose_score(self, nose_result: str) -> float:
        if 'wrinkled nose' in nose_result:
            return 100.0
        return 0.0

    def calculate_mouth_score(self, mouth_result: str) -> float:
        score = 0.0
        mouth_result = mouth_result.split(', ')
        if 'open mouth' in mouth_result:
            score += 50.0
        if 'right smile' in mouth_result:
            score += 25.0
        if 'left smile' in mouth_result:
            score += 25.0
        return score
