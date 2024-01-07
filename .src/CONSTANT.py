random_seed = 1104
# master_folder = "."
# Teacher class represent a Teacher, contain ID and all subjects of that teacher
class Teacher:
	def __init__(self, ID, subjects: list[int]):
		self.ID = ID
		self.subjects = subjects

		# dictionary with key = slot, value = True if this teacher busy on that slot and False if this teacher free
		self.used = [False for i in range(60)]

	# used for BnB
	def feasible(self, r):
		temp = [False for _ in range(r)]
		for i in range(len(self.used)):
			if self.used[i] == False:
				if self.used[i:i+r] == temp:
					return True
		
		return False
	
	# print for debug
	def __str__(self):
		ans = f'Teacher: {self.ID}, subjects = ['

		for subject in self.subjects[:-1]:
			ans += f'{subject}, '
		
		ans += f'{self.subjects[-1]}]'

		return ans

# Class class represent a Class, contain ID and all subjects that this class have to study
class Class:
	def __init__(self, ID, subjects: list[int]):
		self.ID = ID
		self.subjects = subjects

		# Possible teacher can teach this Class
		# dict with key = subject, value = list of teacher can teach this subject
		self.teachers: dict[int, list[Teacher]] = {subject: [] for subject in self.subjects}

		# dict with key = subject, value = [start time slot that teacher assign to this class, teacher]
		self.sol: dict[int, list[int]] = {s: [] for s in subjects}

		self.used = [False for i in range(60)]


	# print for debug
	def __str__(self):
		ans = f'Class: {self.ID}, subjects = ['

		for subject in self.subjects[:-1]:
			ans += f'{subject}, '
		
		ans += f'{self.subjects[-1]}]'

		return ans

def find_possible_teachers(classes: list[Class], teachers: list[Teacher]):
	for c in classes:
		for subject in c.subjects:
			for teacher in teachers:
				if subject in teacher.subjects:
					c.teachers[subject].append(teacher)
		


# import data, if file == False, read input, read file otherwise
def import_data(file):
	classes: list[Class] = []
	teachers: list[Teacher] = []

	if file:
		f = open(file, 'r')
		read = f.readline
	else:
		read = input
	
	T, N, M = map(int, read().split())

	for i in range(N):
		temp = list(map(int, read().split()))
		temp.pop()


		classes.append(Class(i+1, temp))
	
	for i in range(T):
		temp = list(map(int, read().split()))
		temp.pop()

		teachers.append(Teacher(i+1, temp))
	
	temp = list(map(int, read().split()))
	#dictionary key = subject ID, value = preiods
	subjects = {i+1: temp[i] for i in range(M)}
	
	find_possible_teachers(classes, teachers)

	if file:
		f.close()

	return classes, teachers, subjects