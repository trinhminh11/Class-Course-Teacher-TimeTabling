from CONSTANT import import_data, Class, Teacher, master_folder

#O(n*m*k)

# Solver class to solve the problem
class Solver:
	def __init__(self, classes: list[Class], teachers: list[Teacher], time_subject: dict[int, int]):
		self.classes = classes
		self.teachers = teachers
		self.time_subjects = time_subject

		self.length = 0

	# main solve function
	'''
	Greedy:
		loop through each {class}, loop through each {subject}, loop through each {slot}[1, 60], and loop through each {teacher}
		in the next {subject preiods} slots: 
			if {teacher} hasn't taught any class, assign {teacher} to {class} to teach {subject} in those slots
	'''	
	def solve(self):
		# sorting
		# for c in self.classes:
		# 	c.subjects.sort(key=lambda x: len(c.teachers[x]))

		# self.classes.sort(key = lambda x: [len(x.teachers[x.subjects[0]]), len(x.subjects)])

		# loop through each class
		for c in self.classes:
			# loop through each subject
			for subject in c.subjects:
				# loop through each slot
				for slot in range(1, 61):

					# out of range
					if slot + self.time_subjects[subject] > 61:
						break

					if (slot-1) // 6 < (slot + self.time_subjects[subject]-2) // 6:
						continue
					
					# loop through each teacher
					for teacher in c.teachers[subject]:
						for preiod in range(slot, slot + self.time_subjects[subject]):
							# if teacher or class is being used, break and go to next teacher
							if teacher.used[preiod-1] or c.used[preiod-1]:
								break 
						# if teacher and class are not being used, assign teacher to class
						else:
							c.sol[subject] = [slot, teacher.ID]

							for preiod in range(slot, slot + self.time_subjects[subject]):
								teacher.used[preiod-1] = True
								c.used[preiod-1] = True
							break

					# if class.sol[subject] have teacher assign to it in this time_slot, break and go to next subject
					if c.sol[subject] != []:
						self.length += 1
						break
					
		self.classes.sort(key=lambda x: x.ID)
						
	def print_sol(self):

		print(self.length)
		
		for c in self.classes:
			c.subjects.sort()
			for subject in c.subjects:
				if c.sol[subject] != []:
					print(c.ID, subject, *c.sol[subject])
	
	def export_sol(self, file):
		with open(file, 'w') as f:
			f.write(str(self.length) + "\n")

			for c in self.classes:
				c.subjects.sort()
				for subject in c.subjects:
					if c.sol[subject] != []:
						f.write(f'{c.ID} {subject} {c.sol[subject][0]} {c.sol[subject][1]}\n')

# inp = file, if inp = False, => reading from input, out is output file, is_print: if print to console
def main(inp, out, is_print):
	classes, teachers, subjects = import_data(inp)
	
	sol = Solver(classes, teachers, subjects)

	sol.solve()

	if is_print:
		sol.print_sol()
	
	if out:
		sol.export_sol(out)

if __name__ == "__main__":
	main(False, False, True)

		