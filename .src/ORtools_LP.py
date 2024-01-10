from ortools.linear_solver import pywraplp
from CONSTANT import import_data, Teacher, Class

BIG_NUM = 100


class Solver:
	def __init__(self, classes, teachers, subjects):
		self.classes = classes
		self.teachers = teachers
		self.time_subjects = subjects


		self.jobs = self.encode_data()
	
	# encode data
	def encode_data(self):
		jobs = [
			[
				[
					(self.time_subjects[subject], teacher.ID-1) for teacher in c.teachers[subject]
				] if c.teachers[subject] else [(-1, -1)] for subject in c.subjects 
			] for c in self.classes
		]

		
		return jobs

	def solve(self):
		self.solver = pywraplp.Solver.CreateSolver("SAT")

		num_jobs = len(self.jobs)
		all_jobs = range(num_jobs)

		num_teachers = len(self.teachers)
		all_teachers = range(num_teachers)

		# Global storage of variables.
		intervals_per_teachers: dict[int, list] = {}
		intervals_per_classes: dict[int, list] = {}

		self.presences = []


		for job_id in all_jobs:
			job = self.jobs[job_id]
			num_tasks = len(job)
			for task_id in range(num_tasks):
				task = job[task_id]

				if task[0] == (-1, -1):
					continue

				num_alternatives = len(task)
				all_alternatives = range(num_alternatives)

				l_presences = []

				for alt_id in all_alternatives:
					alt_suffix = '_j%i_t%i_a%i' % (job_id, task_id, alt_id)
					# l_presence = 1 if jobs[job_idx][task_idx] use this alt_idx, 0 otherwise
					l_presence = self.solver.BoolVar('presence' + alt_suffix)
					l_start = self.solver.IntVar(0, 60-task[alt_id][0], 'start' + alt_suffix)
					l_end = self.solver.IntVar(1, 60, 'end' + alt_suffix)
					# interval var of this alt_idx
					self.solver.Add(l_start+ task[alt_id][0] == l_end)
					l_interval = [job_id, task_id, alt_id, l_presence, l_start, l_end]

					l_presences.append(l_presence)


					# Add the local interval to the right teacher.
					if task[alt_id][1] not in intervals_per_teachers.keys():
						intervals_per_teachers[task[alt_id][1]] = []
					intervals_per_teachers[task[alt_id][1]].append(l_interval)

					if job_id not in intervals_per_classes.keys():
						intervals_per_classes[job_id] = []
					intervals_per_classes[job_id].append(l_interval)

				# Select exactly one presence variable.
				if l_presences:
					self.presences.append(sum(l_presences))
					self.solver.Add(sum(l_presences) <= 1)

		# Create teachers constraints.
		for teacher_id in all_teachers:
			intervals = intervals_per_teachers[teacher_id] + [[None, None, None, self.solver.IntVar(1, 1, ""), self.solver.IntVar(-1, -1, ""), self.solver.IntVar(-1, -1, "")]]
			_temp = len(intervals)

			for i in range(_temp-1):
				job_id, task_id, alt_id, is_presence, start, end = intervals[i]

				# starts//6 = (end-1)//6
				q1 = self.solver.IntVar(0, 9, "start quotient")
				q2 = self.solver.IntVar(0, 9, "end quotient")

				r1 = self.solver.IntVar(0, 5, "start remainder")
				r2 = self.solver.IntVar(0, 5, "end remainder")

				self.solver.Add(start == q1 * 6 + r1)
				self.solver.Add(end-1 == q2 * 6 + r2)
		
				self.solver.Add(q1 == q2)	

				for j in range(i+1, _temp):
					first = intervals[i] # [job_id, task_id, alt_id, l_presence, l_start, l_end] or [i, j, t, presence, start, end]
					second = intervals[j] # [job_id, task_id, alt_id, l_presence, l_start, l_end] or [i, j, t, presence, start, end]
					
					first_gt_second = self.solver.BoolVar(" ")
					second_gt_first = self.solver.BoolVar(" ")
					nor = self.solver.BoolVar(" ")

					self.solver.Add(first_gt_second + second_gt_first + nor == 1)

					ct1 = self.solver.Constraint(-BIG_NUM, BIG_NUM*3, " ")
					ct1.SetCoefficient(first[3], BIG_NUM)
					ct1.SetCoefficient(second[3], BIG_NUM)
					ct1.SetCoefficient(first_gt_second, BIG_NUM)
					ct1.SetCoefficient(first[4], -1)
					ct1.SetCoefficient(second[5], 1)

					ct2 = self.solver.Constraint(-BIG_NUM, BIG_NUM*3, " ")
					ct2.SetCoefficient(first[3], BIG_NUM)
					ct2.SetCoefficient(second[3], BIG_NUM)
					ct2.SetCoefficient(second_gt_first, BIG_NUM)
					ct2.SetCoefficient(second[4], -1)
					ct2.SetCoefficient(first[5], 1)

					self.solver.Add(nor + first[3] + second[3] <= 2)
		
		# Create classes constraints.
		for job_id in all_jobs:
			if job_id not in intervals_per_classes.keys():
				continue
			intervals = intervals_per_classes[job_id] + [[None, None, None, self.solver.IntVar(1, 1, ""), self.solver.IntVar(-1, -1, ""), self.solver.IntVar(-1, -1, "")]]
			_temp = len(intervals)

			for i in range(_temp-1):
				for j in range(i+1, _temp):
					first = intervals[i] # [job_id, task_id, alt_id, l_presence, l_start, l_end] or [i, j, t, presence, start, end]
					second = intervals[j]# [job_id, task_id, alt_id, l_presence, l_start, l_end] or [i, j, t, presence, start, end]
					
					first_gt_second = self.solver.BoolVar(" ")
					second_gt_first = self.solver.BoolVar(" ")
					nor = self.solver.BoolVar(" ")

					self.solver.Add(first_gt_second + second_gt_first + nor == 1)

					ct1 = self.solver.Constraint(-BIG_NUM, BIG_NUM*3, " ")
					ct1.SetCoefficient(first[3], BIG_NUM)
					ct1.SetCoefficient(second[3], BIG_NUM)
					ct1.SetCoefficient(first_gt_second, BIG_NUM)
					ct1.SetCoefficient(first[4], -1)
					ct1.SetCoefficient(second[5], 1)

					ct2 = self.solver.Constraint(-BIG_NUM, BIG_NUM*3, " ")
					ct2.SetCoefficient(first[3], BIG_NUM)
					ct2.SetCoefficient(second[3], BIG_NUM)
					ct2.SetCoefficient(second_gt_first, BIG_NUM)
					ct2.SetCoefficient(second[4], -1)
					ct2.SetCoefficient(first[5], 1)

					self.solver.Add(nor + first[3] + second[3] <= 2)
		
		self.solver.Maximize(sum(self.presences))

		self.solver.SetTimeLimit(298000) # milisecond

		status = self.solver.Solve()

		# print(status == pywraplp.Solver.OPTIMAL)

		self.temp = intervals_per_teachers


	def print_sol(self):
		ans = {}
		for teacher_id in range(len(self.teachers)):
			intervals = self.temp[teacher_id]
			for interval in intervals:
				job, task, alt, presence, start, end = interval
				if presence.solution_value() and end.solution_value() <= 60:
					ans[(job+1, self.classes[job].subjects[task])] = [int(start.solution_value())+1, self.jobs[job][task][alt][1] + 1]

		print(self.solver.Objective().Value())
		print(len(ans))
		ans = dict(sorted(ans.items(), key = lambda x: x[0]))
		for key, value in ans.items():
			print(*key, *value)
	
	def export_sol(self, file):
		ans = {}
		for teacher_id in range(len(self.teachers)):
			intervals = self.temp[teacher_id]
			for interval in intervals:
				job, task, alt, presence, start, end = interval
				if presence.solution_value() and end.solution_value() <= 60:
					ans[(job+1, self.classes[job].subjects[task])] = [int(start.solution_value())+1, self.jobs[job][task][alt][1] + 1]
	
		ans = dict(sorted(ans.items(), key = lambda x: x[0]))
		
		with open(file, 'w') as f:
			f.write(f'{len(ans)}\n')
			for key, value in ans.items():
				f.write(f'{key[0]} {key[1]} {value[0]} {value[1]}\n')

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