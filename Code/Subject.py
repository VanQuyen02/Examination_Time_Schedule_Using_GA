class Subject:
    def __init__(self, subject_id: int, subject_code: str, exam_duration: int):
        self.id = subject_id
        self.subject_code = subject_code
        self.exam_duration = exam_duration / 90