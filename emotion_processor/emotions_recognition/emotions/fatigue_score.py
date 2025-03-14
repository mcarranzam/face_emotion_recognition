from emotion_processor.emotions_recognition.features.weights_emotion_score import WeightedEmotionScore

class FatigueScore(WeightedEmotionScore):
    def __init__(self):
        super().__init__(eyebrows_weight=0.1, eyes_weight=0.5, nose_weight=0.2, mouth_weight=0.2)
        self.previous_score = 0
        self.smoothed_score = 0
        self.fatigue_accumulation = 0
        self.frames_without_fatigue = 0
        self.fatigue_detected = False

    def calculate_eyebrows_score(self, eyebrows_result: str) -> float:
        score = 0.0
        if 'eyebrows together' in eyebrows_result:
            score += 15.0
        if 'right eyebrow: lowered' in eyebrows_result or 'left eyebrow: lowered' in eyebrows_result:
            score += 20.0
        if 'raised eyebrows' in eyebrows_result:
            score -= 20.0
        return max(0, min(score, 100))

    def calculate_eyes_score(self, eyes_result: str) -> float:
        score = 0.0

        if 'closed eyes' in eyes_result:
            self.fatigue_accumulation += 2
            score = min(100.0, self.fatigue_accumulation)
            self.frames_without_fatigue = 0
        elif 'half-closed eyes' in eyes_result:
            self.fatigue_accumulation += 1.5
            score = min(75.0, self.fatigue_accumulation)
            self.frames_without_fatigue = 0
        elif 'slightly closed eyes' in eyes_result:
            self.fatigue_accumulation += 1
            score = min(60.0, self.fatigue_accumulation)
            self.frames_without_fatigue = 0
        elif 'frequent blinking' in eyes_result:
            if self.fatigue_accumulation > 30:
                score = 40.0
            self.frames_without_fatigue = 0
        elif 'swollen eyes' in eyes_result:
            score = 60.0
        elif 'red eyes' in eyes_result:
            score = 75.0
        else:
            self.frames_without_fatigue += 1
            if self.frames_without_fatigue > 1:
                self.fatigue_accumulation = max(0, self.fatigue_accumulation - 5)
            score = min(self.fatigue_accumulation, 50)

        if 'drooping eyelids' in eyes_result:
            score += 20.0

        return max(0, min(score, 100))

    def calculate_nose_score(self, nose_result: str) -> float:
        score = 0.0
        if 'wrinkled nose' in nose_result:
            score = 50.0
        if 'deep breath' in nose_result:
            score += 25.0
        if 'flared nostrils' in nose_result:
            score += 15.0
        return max(0, min(score, 100))

    def calculate_mouth_score(self, mouth_result: str) -> float:
        score = 0.0
        mouth_result = mouth_result.split(', ')

        if 'yawning' in mouth_result:
            score += 70.0
        if 'open mouth' in mouth_result:
            score += 30.0
        if 'tight lips' in mouth_result:
            score += 20.0
        if 'downturned lips' in mouth_result:
            score += 30.0
        if 'dry lips' in mouth_result:
            score += 40.0

        return max(0, min(score, 100))

    def calculate_fatigue_level(self, eyebrows_result: str, eyes_result: str, nose_result: str, mouth_result: str) -> float:
        eyebrows_score = self.calculate_eyebrows_score(eyebrows_result)
        eyes_score = self.calculate_eyes_score(eyes_result)
        nose_score = self.calculate_nose_score(nose_result)
        mouth_score = self.calculate_mouth_score(mouth_result)

        total_score = (
            self.eyebrows_weight * eyebrows_score +
            self.eyes_weight * eyes_score +
            self.nose_weight * nose_score +
            self.mouth_weight * mouth_score
        )

        if eyes_score > 60 and mouth_score > 50:
            total_score += 5
        if eyes_score > 65 and eyebrows_score > 25:
            total_score += 8
        if 'yawning' in mouth_result and eyes_score > 55:
            total_score += 10
        if 'drooping eyelids' in eyes_result and 'yawning' in mouth_result:
            total_score += 12

        if total_score > 60 and not self.fatigue_detected:
            self.fatigue_detected = True
            self.fatigue_accumulation = 0

        if self.frames_without_fatigue > 5:
            decrement = 3 if self.smoothed_score > 40 else 1.5
            total_score = max(0, total_score - decrement)

        if 'open eyes' in eyes_result or 'wide open eyes' in eyes_result:
            total_score = min(total_score, 30)

        alpha = 0.2
        self.smoothed_score = (
            alpha * total_score + (1 - alpha) * self.previous_score
        )

        self.previous_score = self.smoothed_score

        if self.smoothed_score < 50:
            self.fatigue_detected = False

        return max(0, min(round(self.smoothed_score, 2), 100))
