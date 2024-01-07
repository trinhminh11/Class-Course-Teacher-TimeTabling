from CONSTANT import import_data, Class, Teacher, master_folder
import timeit
from copy import deepcopy

#O(n*m*k)
		
# Solver class to solve the problem
class Solver:
	def __init__(self, classes: list[Class], teachers: list[Teacher], subjects: list[int]):
		
		#working classes and teachers
		self.classes = classes
		self.teachers = teachers

		#subjects
		self.time_subjects = subjects

		#best solution
		self.best_sol: list[list[list[int]]] = []
		self.best_fit = 0
	

	def solve(self):
		#calc upper bound
		upper_bound = 0

		for c in self.classes:
			for subject in c.subjects:
				if c.teachers[subject]:
					upper_bound += 1

		# ans list: i represent class, j represent subject, ans[i][j][0] is slot, ans[i][j][1] is the teacher
		ans = [[[-1, -1] for subject in c.subjects] for c in self.classes]

		def bt(i, j, cur_fit):

			# branch and bound
			_fit = 0
			for c in self.classes[i+1:]:
				for subject in c.subjects:
					for teacher in c.teachers[subject]:
						if teacher.feasible(self.time_subjects[subject]):
							_fit += 1
							break
			
			if cur_fit + _fit <= self.best_fit:
				return False
			# ----------------

			# early stopping
			if timeit.default_timer() - start_time >= max_runtime:
				return True
			
			if j >= len(self.classes[i].subjects):
				j = 0
				i += 1

			# reach 1 solution
			if i == len(self.classes):
				current_fit = 0
				for c in ans:
					for s in c:
						if s != [-1, -1]:
							current_fit += 1
				
				if cur_fit != current_fit:
					print("?")
					exit()
				if self.best_fit < current_fit:
					self.best_fit = current_fit
					self.best_sol = deepcopy(ans)

				if self.best_fit == upper_bound:
					return True

				return False 

			current_class = self.classes[i]
			current_subject = current_class.subjects[j]
			if current_class.teachers[current_subject]:
				for slot in range(60):
					if slot + self.time_subjects[current_subject] > 60:
						break
					if slot // 6 < (slot + self.time_subjects[current_subject] - 1) // 6:
						continue

					for teacher in current_class.teachers[current_subject]:
						for s in range(slot, slot + self.time_subjects[current_subject]):
							if current_class.used[s] or teacher.used[s]:
								break
						else:
							ans[i][j] = [slot+1, teacher.ID]
							for s in range(slot, slot + self.time_subjects[current_subject]):
								current_class.used[s] = True 
								teacher.used[s] = True
							
							cur_fit += 1
							
							if bt(i, j+1, cur_fit):
								return True

							ans[i][j] = [-1, -1]
							cur_fit -= 1

							for s in range(slot, slot + self.time_subjects[current_subject]):
								current_class.used[s] = False 
								teacher.used[s] = False
				
			ans[i][j] = [-1, -1]
			if bt(i, j+1, cur_fit):
				return True

		bt(0, 0, 0)

	def print_sol(self):
		print(self.best_fit)

		for i in range(len(self.best_sol)):
			for j in range(len(self.best_sol[i])):
				if self.best_sol[i][j] != [-1, -1]:
					print(self.classes[i].ID, self.classes[i].subjects[j], *self.best_sol[i][j])
	
	def export_sol(self, file):
		with open(file, 'w') as f:
			f.write(f'{self.best_fit}\n')
			for i in range(len(self.best_sol)):
				for j in range(len(self.best_sol[i])):
					if self.best_sol[i][j] != [-1, -1]:
						f.write(f'{self.classes[i].ID} {self.classes[i].subjects[j]} {self.best_sol[i][j][0]} {self.best_sol[i][j][1]}\n')


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
	# maximum runtime of code
	max_runtime = 298

	start_time = timeit.default_timer()
	
	main(False, False, True)
