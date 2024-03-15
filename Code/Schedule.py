import numpy as np
import re
from Random import DistributedRandom
from Data import Data
import sys
class Schedule:
    def __init__(self, data):
        self.data = data

    # Constraint 1: No student should be required to sit two examinations simultaneously
    def check_no_simultaneous_exams(self, chromosome):
        subject_held_at_slot = self.create_subject_held_at_slot(chromosome)
        flag = True
        for m in range(self.data.number_of_students):
            for t in range(self.data.number_of_total_slots):
                subject_counts = []
                for s in range(self.data.number_of_subjects):
                    if (
                        subject_held_at_slot[s, t]
                        * self.data.student_take_subject[m, s]
                    ):
                        subject_counts.append(s)               
                    if len(subject_counts) > 1:
                        flag = False
        return flag

    # Constraint 2: In each slot, the number of invigilator must be equal to number of room required for each subject
    def check_invigilator_room_match(self, chromosome):
        for s in range(self.data.number_of_subjects):
            for t in range(self.data.number_of_total_slots):
                invigilator_counts = np.sum(chromosome[s, t])
                if invigilator_counts != 0 and invigilator_counts != self.data.number_rooms_of_each_subject[s]:
                    return False
        return True

    # Constraint 3: No invigilator should be required to sit two examinations simultaneously
    def check_no_invigilator_clashes(self, chromosome):
        for i in range(self.data.number_of_invigilators):
            for t in range(self.data.number_of_total_slots):
                subject_counts = np.sum(chromosome[:, t, i])
                if subject_counts > 1:
                    return False
        return True

    # Constraint 4: Invigilator is scheduled to subject that belong to their capacity
    def check_invigilator_capacity(self, chromosome):
        for s in range(self.data.number_of_subjects):
            for i in range(self.data.number_of_invigilators):
                for t in range(self.data.number_of_total_slots):
                    if chromosome[s, t, i] == 1 and self.data.invigilator_can_supervise_subject[i, s] == 0:
                        return False
        return True

    # Constraint 5: Number of rooms used in one slot is not larger than university's capacity
    def check_room_capacity(self, chromosome):
        total_rooms_needed = np.sum(chromosome, axis=(0, 2))
        return np.all(total_rooms_needed <= self.data.number_of_rooms)

    # Constraint 6: One subject only take place at one time
    def check_single_subject_at_a_time(self, chromosome):
        for s in range(self.data.number_of_subjects):
            cnt = []
            for t in range(self.data.number_of_total_slots):
                number_of_invigilators = np.sum(chromosome[s, t])
                if number_of_invigilators > 0:
                    cnt.append(t)
            if len(cnt) != self.data.length_of_subject[s]:
                return False
        return True

    # Constraint 7: All subject must happen only one part of day (in the morning or in the afternoon)
    def check_subject_part_of_day(self, chromosome):
        subject_held_at_slot = self.create_subject_held_at_slot(chromosome)
        slot_start_of_subject = self.create_slot_start_of_subject(subject_held_at_slot)
        slot_end_of_subject = self.create_slot_end_of_subject(slot_start_of_subject)
        return np.all(
            np.floor(2 * slot_start_of_subject / self.data.number_of_slots_per_day)
            == np.floor(2 * slot_end_of_subject / self.data.number_of_slots_per_day)
        )

    # Constraint 8: With each subject, Invigilator need to supervise all consecutive slot of this subject happen.
    def check_invigilator_consecutive_slots(self, chromosome):
        subject_held_at_slot = self.create_subject_held_at_slot(chromosome)
        slot_start_of_subject = self.create_slot_start_of_subject(subject_held_at_slot)
        slot_end_of_subject = self.create_slot_end_of_subject(slot_start_of_subject)
        for s in range(self.data.number_of_subjects):
            for i in range(self.data.number_of_invigilators):
                consecutive_count = np.sum(chromosome[s, int(slot_start_of_subject[s,0]):int(slot_end_of_subject[s,0])+1, i])
                if consecutive_count != 0 and consecutive_count != self.data.length_of_subject[s]:
                    return False
        return True
    
    def create_subject_held_at_slot(self, chromosome):
        subject_held_at_slot = np.zeros(
            (self.data.number_of_subjects, self.data.number_of_total_slots), dtype=int
        )
        for s in range(self.data.number_of_subjects):
            for t in range(self.data.number_of_total_slots):
                number_of_invigilators = 0
                for i in range(self.data.number_of_invigilators):
                    number_of_invigilators += chromosome[s, t, i]
                if number_of_invigilators > 0:
                    subject_held_at_slot[s, t] = 1
        return subject_held_at_slot
    
    def create_slot_start_of_subject(self, subject_held_at_slot):
        slot_start_of_subject = np.zeros((self.data.number_of_subjects, 1), dtype=int)
        for s in range(self.data.number_of_subjects):
            for t in range(1, self.data.number_of_total_slots):
                if (
                    subject_held_at_slot[s, t - 1] == 0
                    and subject_held_at_slot[s, t] == 1
                ):
                    slot_start_of_subject[s] = t
        return slot_start_of_subject
    
    def create_slot_end_of_subject(self, slot_start_of_subject):
        slot_end_of_subject = np.zeros((self.data.number_of_subjects, 1), dtype=int)
        for s in range(self.data.number_of_subjects):
            slot_end_of_subject[s] = (
                slot_start_of_subject[s] + self.data.length_of_subject[s] - 1
            )
        return slot_end_of_subject

    def pass_all_constraints(self, chromosome):
        print(self.check_no_simultaneous_exams(chromosome),
             self.check_invigilator_room_match(chromosome),
             self.check_no_invigilator_clashes(chromosome),
             self.check_invigilator_capacity(chromosome),
             self.check_room_capacity(chromosome),
             self.check_single_subject_at_a_time(chromosome),
             self.check_subject_part_of_day(chromosome),
             self.check_invigilator_consecutive_slots(chromosome)),
        return (
            self.check_no_simultaneous_exams(chromosome)
            and self.check_invigilator_room_match(chromosome)
            and self.check_no_invigilator_clashes(chromosome)
            and self.check_invigilator_capacity(chromosome)
            and self.check_room_capacity(chromosome)
            and self.check_single_subject_at_a_time(chromosome)
            and self.check_subject_part_of_day(chromosome)
            and self.check_invigilator_consecutive_slots(chromosome)
        )

    def create_chromosome(self):
        #Strategy:
        # 1. For each subject:
        #   - Randomly assign a slot (distribute according to the number of available rooms).
        #   - Choose invigilators who can supervise this slot (higher slots have higher preference).
        # 2. Implement the above logic to populate the chromosome.
        
        # while True:
            chromosome = np.zeros(
                (
                    self.data.number_of_subjects,
                    self.data.number_of_total_slots,
                    self.data.number_of_invigilators,
                ),
                dtype=int,
            )
            number_of_slot_schedule_invigilator = np.zeros(self.data.number_of_invigilators, dtype= int)
            for i in range(self.data.number_of_invigilators):
                number_of_slot_schedule_invigilator[i] = self.data.number_of_slots_required_for_invigilators[i]
            invigilator_take_slot = np.zeros((self.data.number_of_invigilators, self.data.number_of_total_slots), dtype=int)
            subject_held_at_slot = np.zeros((self.data.number_of_subjects, self.data.number_of_total_slots), dtype=int)
            random_slot = DistributedRandom.new_distributed_random_slot(self.data.number_of_total_slots, self.data.number_of_rooms)
            for i in range(self.data.number_of_invigilators):
                number_of_slot_schedule_invigilator[i] += 10
            
            for s in range(self.data.number_of_subjects): 
                s_length = self.data.length_of_subject[s]
                t = random_slot.get_random()
                while True:
                    if self.check_subject_fit_slot(s_length, t, self.data.number_of_slots_per_day) and\
                    self.check_subject_overlap_slot(s, t, s_length, self.data.number_of_subjects, subject_held_at_slot, self.data.overlap_subject) and\
                    self.check_room_capacity_at_one_time(chromosome, t, s):
                        break
                    t = random_slot.get_random()
                random_invigilator = DistributedRandom()
                count_invigilator = 0

                # Calc number invi need for this subject
                invigilator_need = self.data.number_rooms_of_each_subject[s]
                for i in range(self.data.number_of_invigilators):
                    can_add = True
                    for eachSlot in range(int(t), int(t + s_length)):
                        if self.data.invigilator_can_supervise_subject[i, s] == 1 and invigilator_take_slot[i,eachSlot] == 0 and number_of_slot_schedule_invigilator[i]>0:
                            can_add = True
                        else:
                            can_add = False
                            break
                    if can_add:
                        random_invigilator.add(i, number_of_slot_schedule_invigilator[i])
                        count_invigilator += 1 
                if count_invigilator < invigilator_need:
                    print("not enough invigilators", s)
                
                for i in range(invigilator_need):
                    current_invigilator = random_invigilator.get_random()
                    if self.data.invigilator_can_supervise_subject[current_invigilator, s] !=1:
                        print("Invalid invigilator assign for subject")
                    
                    for each_slot in range(int(t), int(t+ s_length)):
                        if invigilator_take_slot[current_invigilator][each_slot] !=0:
                            print("Invalid slot assignment for invigilator ", current_invigilator)
                        
                        chromosome[s,each_slot, current_invigilator] = 1
                        invigilator_take_slot[current_invigilator,each_slot] = 1
                        subject_held_at_slot[s,each_slot] = 1
                        random_slot.add(each_slot, -1)
                    random_invigilator.delete(current_invigilator)
                    number_of_slot_schedule_invigilator[current_invigilator] -= 1

            # if self.pass_all_constraints(chromosome):
            return chromosome
    
    
    def check_room_capacity_at_one_time(self, chromosome, t, s):
        return self.data.number_of_rooms - np.sum(chromosome, axis = (0,2))[t] - self.data.number_rooms_of_each_subject[s] >=0
    def check_subject_fit_slot(self,sub_length, slot, slots_per_day):
        half = slots_per_day // 2
        if (slot // half) == ((slot + sub_length - 1) // half):
            return True
        return False


    def check_subject_overlap_slot(self, current_subject, current_time, subject_length, number_of_subjects, subject_take_slot, overlap_subject):
        for slot in range(int(current_time), int(current_time+subject_length)):
            for pre_subject in range(number_of_subjects):
                if pre_subject == current_subject:
                    continue
                if overlap_subject[current_subject][pre_subject]==0:
                    continue
                if subject_take_slot[pre_subject][slot]==1:
                    return False

        return True   
    def cal_payoff_student(self, chromosome):
        subject_held_at_slot = self.create_subject_held_at_slot(chromosome)
        slot_start_of_subject = self.create_slot_start_of_subject(subject_held_at_slot)
        slot_start_of_student = np.zeros(
            (self.data.number_of_students, self.data.number_of_subjects)
        )
        for m in range(self.data.number_of_students):
            for s in range(self.data.number_of_subjects):
                slot_start_of_student[m, s] = (
                    self.data.student_take_subject[m, s] * slot_start_of_subject[s]
                )
        
        sorted_slot_desc = np.sort(slot_start_of_student, axis=1)[:, ::-1]
      
        payoff_value_student = 0
        for m in range(self.data.number_of_students):
            payoff_one_student = 0
            for i in range(0, self.data.number_subjects_of_each_student[m] - 1):
                payoff_one_student += abs(
                    sorted_slot_desc[m, i]
                    - sorted_slot_desc[m, i + 1]
                    - (
                        self.data.number_of_total_slots
                        / self.data.number_subjects_of_each_student[m]
                    )
                )
            print(m,  self.data.number_of_total_slots
                        / self.data.number_subjects_of_each_student[m])
            payoff_value_student += payoff_one_student
        return payoff_value_student

    def cal_payoff_invigilator(self, chromosome):
        number_of_slot_schedule_invigilator = np.zeros(
            (self.data.number_of_invigilators, self.data.number_of_examination_days)
        )
        for i in range(self.data.number_of_invigilators):
            for d in range(self.data.number_of_examination_days):
                count = 0
                for t in range(
                    self.data.number_of_slots_per_day * d,
                    self.data.number_of_slots_per_day * (d + 1),
                ):
                    for s in range(self.data.number_of_subjects):
                        count += chromosome[s, t, i]
                if count > 0:
                    number_of_slot_schedule_invigilator[i, d] = 1

        payoff_value_invigilator = 0
        payoff_1 = 0
        payoff_2 = 0
        w1 = 1/2
        w2 = 1/2
        for i in range(self.data.number_of_invigilators):
            for d in range(self.data.number_of_examination_days):
                payoff_1 += number_of_slot_schedule_invigilator[i,d]

        for i in range(self.data.number_of_invigilators):
            total_slot_of_invigilator = 0
            for s in range(self.data.number_of_subjects):
                for t in range(self.data.number_of_total_slots):
                    total_slot_of_invigilator += chromosome[s, t, i]
            payoff_2 += abs(
                total_slot_of_invigilator
                - self.data.number_of_slots_required_for_invigilators[i]
            )
    
        
        payoff_value_invigilator = w1 * payoff_1 + w2 * payoff_2

        return payoff_value_invigilator

    def cal_payoff_p0(self, chromosome):
        mean_room_each_slot = 0
        total_rooms = 0
        for t in range(self.data.number_of_total_slots):
            for s in range(self.data.number_of_subjects):
                for i in range(self.data.number_of_invigilators):
                    total_rooms += chromosome[s, t, i]
        mean_room_each_slot = total_rooms / self.data.number_of_total_slots
        pay_off_p0 = 0
        for t in range(self.data.number_of_total_slots):
            total_rooms_each_slot = 0
            for s in range(self.data.number_of_subjects):
                for i in range(self.data.number_of_invigilators):
                    total_rooms_each_slot += chromosome[s, t, i]
            pay_off_p0 += (total_rooms_each_slot - mean_room_each_slot) ** 2
        pay_off_p0 = np.sqrt(pay_off_p0 / (self.data.number_of_total_slots - 1))
        # print(mean_room_each_slot)
        return pay_off_p0

    def get_fitness(self, chromosome):
        w3 = 1/3
        w4 = 1/3
        w5 = 1/3
        # if self.pass_all_constraints(chromosome):
        fitness_value =  w3 * self.cal_payoff_student(chromosome) + w4 * self.cal_payoff_invigilator(chromosome)+ w5 * self.cal_payoff_p0(chromosome)
        #     )
        # else:
        #     fitness_value = 99999999999
        print(self.cal_payoff_student(chromosome))
        print( self.cal_payoff_invigilator(chromosome))
        print(self.cal_payoff_p0(chromosome))
        return fitness_value

    
    def read_chromosome_from_file(self, file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        chromosome = np.zeros((self.data.number_of_subjects,
                            self.data.number_of_total_slots,
                            self.data.number_of_invigilators), dtype=int)
        for line in lines:
            parts = re.findall(r'\d+', line)  # Extract all numeric parts using regex
            if len(parts) == 4:
                subject, slot, invigilator, value = map(int, parts)
                chromosome[subject, slot, invigilator] = value
        return chromosome

    def test_chromosome_from_file(self, file_path):
        chromosome = self.read_chromosome_from_file(file_path)

        if self.pass_all_constraints(chromosome):
            print("Chromosome passes all constraints.")
        else:
            print("Chromosome does not pass all constraints.")
    
    def write_chromosome_to_file(self, file_path, chromosome):
        with open(file_path, 'w') as file:
            for s in range(self.data.number_of_subjects):
                for t in range(self.data.number_of_total_slots):
                    for i in range(self.data.number_of_invigilators):
                        line = f"Subject {s}, Slot {t}, Invigilator {i}: {chromosome[s, t, i]}\n"
                        file.write(line)

if __name__ == "__main__":
    data = Data()
    data.load_data()
    # print(data.number_rooms_of_each_subject)
    s = Schedule(data)
    file_path = "chromosome_output.txt"
    chromosome = s.read_chromosome_from_file(file_path)
    print("sucess_created")
    print(s.get_fitness(chromosome))
    # print(data.invigilator_can_supervise_subject[274][4])