from Student import Student
from Subject import Subject
from Invigilator import Invigilator
import pandas as pd
import numpy as np
import os

class Data:
    def __init__(self):
        self.number_of_students = None
        self.number_of_invigilators = None
        self.number_of_rooms = None
        self.number_of_subjects = None
        self.number_of_examination_days = None
        self.maximum_number_students_each_room = None
        self.number_of_slots_per_day = None
        self.student_take_subject = None
        self.length_of_subject = None
        self.invigilator_can_supervise_subject = None
        self.number_of_slots_required_for_invigilators = None
        self.number_of_total_slots = None
        self.number_subjects_of_each_student = None
        self.number_students_of_each_subject = None
        self.number_rooms_of_each_subject = None
        self.list_students = None
        self.list_subjects = None
        self.list_invigilators = None
        self.number_of_slot_schedule_invigilator = None
        self.overlap_subject = None
    
    def load_data(self):
        root_path = "D:/Course_FPT/Term_9/Reiforcement Learning/Data"
        students = pd.read_csv(os.path.join(root_path,"Student.csv"))
        invigilators = pd.read_csv(os.path.join(root_path,"Invigilator.csv"))
        subjects = pd.read_csv(os.path.join(root_path,"Subject.csv"))
        student_take_subject = pd.read_csv(os.path.join(root_path,"Student_Subject.csv"))
        invigilator_can_supervise_subject = pd.read_csv(os.path.join(root_path,"SubjectInvigilator.csv"))

        self.number_of_students = students.shape[0]
        self.number_of_invigilators = invigilators.shape[0]
        self.number_of_subjects = subjects.shape[0]
        self.number_of_rooms = 100
        self.number_of_examination_days = 14
        self.maximum_number_students_each_room = 22
        self.number_of_slots_per_day = 6

        self.student_take_subject = student_take_subject.values
        self.length_of_subject = (subjects['ExamDuration'].values)/90
        self.invigilator_can_supervise_subject = invigilator_can_supervise_subject.values.T
        self.number_of_slots_required_for_invigilators = np.ceil(1.5*invigilators['NumberOfClass'].values)
        
        self.number_of_total_slots = self.number_of_slots_per_day * self.number_of_examination_days
        self.number_subjects_of_each_student = np.sum(self.student_take_subject, axis=1)
        self.number_students_of_each_subject = np.sum(self.student_take_subject, axis=0)
        self.number_rooms_of_each_subject = [None]*self.number_of_subjects
        self.overlap_subject = self.create_overlap_subject()
        for s in range(self.number_of_subjects):
            self.number_rooms_of_each_subject[s] = int((self.number_students_of_each_subject[s]+self.maximum_number_students_each_room-1)/ self.maximum_number_students_each_room)

        self.list_students = [None]*self.number_of_students
        self.list_invigilators = [None]*self.number_of_invigilators
        self.list_subjects = [None]*self.number_of_subjects

        for i in range(0, self.number_of_students):
            student_id = students['Id'][i]
            roll_number = students['RollNumber'][i]
            member_code = students['MemberCode'][i]
            email = students["Email"][i]
            full_name = students['FullName'][i]
            self.list_students[i] = Student(student_id, roll_number, member_code, email, full_name)
        
        for i in range(0, self.number_of_invigilators):
            invigilator_id = invigilators['Id'][i]
            code = invigilators['Code'][i]
            number_of_class = invigilators["NumberOfClass"][i]
            self.list_invigilators[i] = Invigilator(invigilator_id, code, number_of_class)
        
        for i in range(0, self.number_of_subjects):
            subject_id = subjects['Id'][i]
            subject_code = subjects['SubCode'][i]
            exam_duration = subjects['ExamDuration'][i]
            self.list_subjects[i] = Subject(subject_id, subject_code, exam_duration)
            
    def create_overlap_subject(self):
        overlap_subject = np.zeros((self.number_of_subjects, self.number_of_subjects), dtype = int)
        for m in range(self.number_of_students):
            for s_1 in range(self.number_of_subjects):
                for s_2 in range(self.number_of_subjects):
                    if s_1 == s_2:
                        continue
                    if self.student_take_subject[m,s_1] == 1 and self.student_take_subject[m,s_2] ==1:
                        overlap_subject[s_1,s_2] =1
        return overlap_subject