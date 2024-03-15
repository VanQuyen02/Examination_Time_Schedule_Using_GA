from ortools.linear_solver import pywraplp
from Data import *

def Sub_Take_Slot(subject, slot):
    for invi in range(n_teachers):
        if sol[subject][slot][invi] == 1:
            return 1
    return 0
def Sub_Start(subject):
    for t in range(n_slots):
        if(Sub_Take_Slot[subject][t]==1):
            return t

data = Data()
data.load_data()
# Số lượng môn học, slot thi và giáo viên
n_subjects = data.number_of_subjects
n_slots = data.number_of_total_slots
n_teachers = data.number_of_invigilators
n_students = data.number_of_students
n_days = data.number_of_examination_days
n_rooms = data.number_of_rooms
# Tạo mô hình
model = pywraplp.Solver.CreateSolver("SCIP")

# Tạo biến quyết định
sol = [[[model.IntVar(0, 1, f'sol[{i},{j},{k}]') for k in range(n_teachers)] for j in range(n_slots)] for i in range(n_subjects)]
subTakeSlot = [[model.NewBoolVar(f'subTakeSlot[{i},{j}]') for j in range(n_slots)] for i in range(n_subjects)]
subStart = [model.NewIntVar(f'subStart[{i}]') for i in range(n_subjects)]
studentStart = [[model.NewBoolVar(f'studentStart[{i},{j}]') for j in range(n_slots)] for i in range(n_students)]
studentStart1 = {}

for stu in range(data.number_of_students):
    for i in range(data.number_subjects_of_each_student):
        studentStart1[stu, i] = model.NewIntVar(0, data.number_of_total_slots, f'studentStart1[{stu},{i}]')
        model.AddElement(studentStart1[stu, i], studentStart[stu], 1) # 1 = y[x]
        if i < data.number_subjects_of_each_student-1:
            model.Add(studentStart1[stu, i] <= studentStart1[stu,i+1])  


for stu in range(n_students):
    for slot in range(n_slots):
        model.Add(studentStart[stu, slot] == sum((slot == subStart[sub] and data.student_take_subject[stu, sub] == 1)) for sub in range (n_subjects))

for sub in range(n_subjects):

    model.Add(subStart[sub] == Sub_Start[sub])

    for slot in range(n_slots):
        model.Add(subTakeSlot[sub][slot] == Sub_Take_Slot(sub, slot))

# Constraint 1: No student should be required to sit two examinations simultaneously
for stu in range(n_students):
    for slot in range(n_slots):
        model.Add(sum(subTakeSlot[sub][slot] * data.student_take_subject[stu][sub]) <= 1 for sub in range(n_subjects))


# Constraint 2: In each slot, the number of invigilator must be equal to number of room required for each subjectfor j in range(n_slots):
for s in range(n_subjects):
    for t in range(n_slots):
        model.Add(sum(sol[s][t] for i in range(n_teachers)) ==0 or sum(sol[s][t] for i in range(n_teachers)) == data.number_rooms_of_each_subject[s])

# Constraint 3: No invigilator should be required to sit two examinations simultaneously
for i in range(n_teachers):
    for t in range(n_slots):
        model.Add(sum(sol[s][t][i] for s in range(n_subjects)) <= 1)

 # Constraint 4: Invigilator is scheduled to subject that belong to their capacity
for s in range(n_subjects):
    for i in range(n_teachers):
        for t in range(n_slots):
            model.Add(not (sol[s][t][i] == 1 and data.invigilator_can_supervise_subject[i][s] == 0))

# Constraint 5: Number of rooms used in one slot is not larger than university's capacity
model.Add(np.all(np.sum(sol, axis=(0, 2)<= n_rooms)))      
model

# Constraint 6: One subject only take place at one time
for s in range(n_subjects):
    model.Add(sum(subTakeSlot(s,t) for t in range(n_slots)) == data.length_of_subject[s])

# Constraint 7: All subject must happen only one part of day (in the morning or in the afternoon)
for s in range(n_subjects):
    start = subStart[s]
    end = subStart[s] + data.length_of_subject[s]
    model.Add(np.floor(2*start / data.number_of_slots_per_day) == (np.floor(2*end / data.number_of_slots_per_day)))
    
# Constraint 8: With each subject, Invigilator need to supervise all consecutive slot of this subject happen.
for i in range(n_teachers):
    for s in range(n_subjects):
        start = subStart[s]
        end = subStart[s] + data.length_of_subject[s]
        model.Add(np.sum(sol[s][start:end+1][i]) == data.length_of_subject[s] or 
                  np.sum(sol[s][start:end+1][i]) == 0)
# Xác định hàm mục tiêu (nếu có)
objective_terms = []
w1 = w2 = w3 = 1/3
w4 = w5 = 0.5



# Contribution to the objective function from stundent

payoff_value_student = []
payoffOneStudent = {}
for m in range(data.number_of_students):
    model.
    model.Add(payoffOneStudent[m] == (studentStart1[m, i]
            - studentStart1[m, i + 1]
            - (
                data.number_of_total_slots
                / data.number_subjects_of_each_student[m]
            ))**2 for i in range(0, data.number_subjects_of_each_student[m] - 1))
    # for i in range(0, data.number_subjects_of_each_student[m] - 1):
        # payoff_one_student .append((studentStart1[m, i]
        #     - studentStart1[m, i + 1]
        #     - (
        #         data.number_of_total_slots
        #         / data.number_subjects_of_each_student[m]
        #     ))**2)
        
    # print(m,  data.number_of_total_slots
    #             / data.number_subjects_of_each_student[m])
    payoff_value_student.append(model.sum(payoff_one_student))
    # return payoff_value_student

number_of_slot_schedule_invigilator = np.zeros(
        (data.number_of_invigilators, data.number_of_examination_days))
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
    return pay_off_p0}

# Giải mô hình
solver = cp_model.CpSolver()
status = solver.Solve(model)

# In kết quả
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for i in range(n_subjects):
        for j in range(n_slots):
            for k in range(n_teachers):
                if solver.Value(x[i][j][k]) == 1:
                    print(f'Môn {i} được tổ chức trong slot {j} bởi giáo viên {k}')
else:
    print('Không tìm thấy giải pháp')