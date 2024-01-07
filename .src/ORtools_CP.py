"""Solves a flexible jobshop problems with the CP-SAT solver.

A jobshop is a standard scheduling problem when you must sequence a
series of task_types on a set of machines. Each job contains one task_type per
machine. The order of execution and the length of each job on each
machine is task_type dependent.

The objective is to minimize the maximum completion time of all
jobs. This is called the makespan.
"""


from ortools.sat.python import cp_model
from CONSTANT import import_data, Teacher, Class, master_folder



class Solver:
	def __init__(self, classes, teachers, subjects):
		self.classes = classes
		self.teachers = teachers
		self.subjects = subjects
		self.jobs = self.encode_data()
	
	# encode data
	def encode_data(self):
		# jobs[i][j][k] = (d, t)
		# i: classes[i]
		# j: index of subject in classes[i]
		# k: index of teacher can teach classes[i]-subjects[j
		# d: duration to learn classes[i]-subjects[j]
		# t: ID of classes[i]-subjects[j]-teachers[k]
		# (d, t) = (-1, -1) imply that there are no teacher to teach classes[i]-subjects[j]
		jobs = [
			[
				[
					(self.subjects[subject], teacher.ID-1) for teacher in c.teachers[subject]
				] if c.teachers[subject] else [(-1, -1)] for subject in c.subjects
			] for c in self.classes
		]
		
		# job is class, task is subject
		return jobs
		

	def solve(self):
		num_jobs = len(self.jobs)
		all_jobs = range(num_jobs)

		num_teachers = len(self.teachers)
		all_teachers = range(num_teachers)

		# Model
		model = cp_model.CpModel()


		# Global storage of variables.
		intervals_per_teacher = {} #T_intervals
		intervals_per_classes = {} #C_intervals
		self.starts = {}  # indexed by (job_idx, task_idx).
		self.presences = {}  # indexed by (job_idx, task_idx, alt_idx). #presences = 1 when in jobs[job_idx][task_idx] choose alt_idx to use, 0 otherwise

		self.used = []


		# Scan the jobs and create the relevant variables and intervals.
		for job_idx in all_jobs:
			job = self.jobs[job_idx]
			num_tasks = len(job)
			for task_idx in range(num_tasks):

				task = job[task_idx]

				# if there are no teacher to teach this jobs[job_idx][task_idx]
				if task[0] == (-1,-1):
					continue

				num_alternatives = len(task)
				all_alternatives = range(num_alternatives)


				# Create main interval for the task, startingtime and endingtime of jobs[job_idx][task_idx]
				suffix_name = '_j%i_t%i' % (job_idx, task_idx)

				start = model.NewIntVar(0, 60-task[0][0], 'start' + suffix_name)

				# Store the start for the solution.
				self.starts[(job_idx, task_idx)] = start	

				# Create alternative intervals.
				l_presences = []
				
				for alt_idx in all_alternatives:
					alt_suffix = '_j%i_t%i_a%i' % (job_idx, task_idx, alt_idx)
					# l_presence = 1 if jobs[job_idx][task_idx] use this alt_idx, 0 otherwise
					l_presence = model.NewBoolVar('presence' + alt_suffix)
					l_start = model.NewIntVar(0, 60 - task[alt_idx][0], 'start' + alt_suffix)
					l_duration = task[alt_idx][0]
					l_end = model.NewIntVar(0, 60, 'end' + alt_suffix)
					# interval var of this alt_idx
					l_interval = model.NewOptionalIntervalVar(
						l_start, l_duration, l_end, l_presence,
						'interval' + alt_suffix)
					
					l_presences.append(l_presence)

					# start//6 == (end-1)//6
					temp_s = model.NewIntVar(0, 9, "")
					temp_e = model.NewIntVar(0, 9, "")
					model.AddDivisionEquality(temp_s, l_start, 6) # temp_s = l_start // 6
					model.AddDivisionEquality(temp_e, l_end-1, 6) # temp_e = (l_end-1) // 6
					model.Add(temp_s == temp_e)

					# Link the master variables with the local ones.
					model.Add(start == l_start).OnlyEnforceIf(l_presence)

					# Add the local interval to the right teacher.
					if task[alt_idx][1] not in intervals_per_teacher.keys():
						intervals_per_teacher[task[alt_idx][1]] = []
					intervals_per_teacher[task[alt_idx][1]].append(l_interval)

					# Add the local interval to the right class
					if job_idx not in intervals_per_classes.keys():
						intervals_per_classes[job_idx] = []
					intervals_per_classes[job_idx].append(l_interval)

					# Store the presences for the solution.
					self.presences[(job_idx, task_idx, alt_idx)] = l_presence

				# Select one or none alt_idx in all_alt 
				model.Add(sum(l_presences) <= 1)

				self.used.append(sum(l_presences))


		# Create teachers constraints.
		for teacher_id in all_teachers:
			if teacher_id not in intervals_per_teacher.keys():
				continue

			intervals = intervals_per_teacher[teacher_id]

			if len(intervals) > 1:
				model.AddNoOverlap(intervals)
		
		# Create classes constraints
		for job_idx in all_jobs:
			if job_idx not in intervals_per_classes.keys():
				continue
			intervals = intervals_per_classes[job_idx]
			if len(intervals) > 1:
				model.AddNoOverlap(intervals)

		model.Maximize(sum(self.used))


		# Solve model.
		self.solver = cp_model.CpSolver()

		self.solver.parameters.max_time_in_seconds = 298


		status = self.solver.Solve(model)

		print(status == cp_model.OPTIMAL)

	def print_sol(self):
		ans = ''
		K = 0
		# Print final solution.
		for job_idx in range(len(self.jobs)):
			for task_idx in range(len(self.jobs[job_idx])):
				if self.jobs[job_idx][task_idx][0] == (-1, -1):
					continue
				start_value = self.solver.Value(self.starts[(job_idx, task_idx)])
				for alt_idx in range(len(self.jobs[job_idx][task_idx])):
					if self.solver.Value(self.presences[(job_idx, task_idx, alt_idx)]):
						machine = self.jobs[job_idx][task_idx][alt_idx][1]
						ans += f'{job_idx+1} {self.classes[job_idx].subjects[task_idx]} {start_value+1} {machine+1}\n'
						K += 1
						break 
						
		print(K)
		print(ans)
	
	def export_sol(self, file):
		ans = ''
		K = 0
		# Print final solution.
		for job_idx in range(len(self.jobs)):
			for task_idx in range(len(self.jobs[job_idx])):
				if self.jobs[job_idx][task_idx][0] == (-1, -1):
					continue
				start_value = self.solver.Value(self.starts[(job_idx, task_idx)])
				for alt_idx in range(len(self.jobs[job_idx][task_idx])):
					if self.solver.Value(self.presences[(job_idx, task_idx, alt_idx)]):
						machine = self.jobs[job_idx][task_idx][alt_idx][1]
						ans += f'{job_idx+1} {self.classes[job_idx].subjects[task_idx]} {start_value+1} {machine+1}\n'
						K += 1
						break

					
		
		with open(file, 'w') as f:
			f.write(str(K) + "\n")
			f.write(ans)
	

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

