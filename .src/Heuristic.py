import random, timeit
from copy import deepcopy
from CONSTANT import import_data, Class, Teacher, random_seed, master_folder

random.seed(random_seed)

# O(n*m*pop_size*gen)

class Individual:
	def __init__(self, classes: list[Class], teachers: list[Teacher], time_subjects: dict[int, int], chromosome = None):
		self.classes = deepcopy(classes)
		self.teachers = deepcopy(teachers)
		self.time_subjects = deepcopy(time_subjects)
		if chromosome == None:
			self.chromosome: list[list[int]] = []
			for c in classes:
				DNA = []

				for cteachers in c.teachers.values():
					try:
						DNA.append(random.choice(cteachers).ID)
					except:
						DNA.append(0)

				self.chromosome.append(DNA)

		else:
			self.chromosome = chromosome

		self.fitness = 0
		self.calc_fitness()

	def calc_fitness(self):

		if self.fitness != 0:
			return self.fitness
		
		count_learn = 0
		max_choice = 0
		
		# temp = zip(self.classes, self.chromosome)

		# temp = sorted(temp, key= lambda x: [len(x[0].teachers[x[0].subjects[0]]), len(x[0].subjects)])

		for c, DNA in zip(self.classes, self.chromosome):
			c.sol = {subject: [0, teacher] for subject, teacher in zip(c.subjects, DNA)}
			# c.sol = dict(sorted(c.sol.items(), key= lambda x: [self.time_subjects[x[0]], len(c.teachers[x[0]])]))

			for subject, (_, teacher) in c.sol.items():
				if teacher == 0:
					continue

				t = self.teachers[teacher-1]

				choice = 0

				for slot in range(1, 61):

					# out of range
					if slot + self.time_subjects[subject] > 61:
						break

					if (slot-1) // 6 < (slot + self.time_subjects[subject]-2) // 6:
						continue

					if not c.used[slot-1] and not t.used[slot-1]:
						
						for j in range(slot, slot+self.time_subjects[subject]):
							if c.used[j-1] or t.used[j-1]:
								break
						else:
							choice = slot
							break
				
				if choice == 0:
					continue

				if choice > max_choice:
					max_choice = choice

				c.sol[subject][0] = choice

				count_learn += 1

				for period in range(choice, choice + self.time_subjects[subject]):
					c.used[period-1] = True
					self.teachers[teacher-1].used[period-1] = True

		self.fitness = [count_learn, -max_choice]
			
	
	def crossover(self, other, mutation_rate):
		mom_chromosome = self.chromosome
		dad_chromosome = other.chromosome
		child_chromosome = []
		for mom_DNA, dad_DNA in zip(mom_chromosome, dad_chromosome):
			child_DNA = mom_DNA[:len(mom_DNA)//2] + dad_DNA[len(mom_DNA)//2:]
			child_chromosome.append(child_DNA)
		
		if random.random() <= mutation_rate:
			self.mutation(child_chromosome)
		
		return child_chromosome

	def mutation(self, chromosome):
		DNA_index = random.randrange(len(chromosome))
		gene_index = random.randrange(len(chromosome[DNA_index]))
		try:
			chromosome[DNA_index][gene_index] = random.choice(self.classes[DNA_index].teachers[self.classes[DNA_index].subjects[gene_index]]).ID
		except:
			chromosome[DNA_index][gene_index] = 0

class GA:
	def __init__(self, n, g_num, mutation_rate, k, classes, teachers, subjects):
		self.n = n
		self.g_num = g_num
		self.mutation_rate = mutation_rate
		self.k = k
		self.classes = classes
		self.teaches = teachers
		self.time_subjects = subjects

		self.K = 0

		for c in self.classes:
			for teacher in c.teachers.values():
				if teacher:
					self.K += 1

		self.population = [Individual(classes, teachers, subjects) for _ in range(self.n)]


		sp = 1.2
		self.Probs = [1/self.n * (sp - (2*sp-2)*(i-1)/(self.n-1)) for i in range(1, self.n+1)]
		self.Probs.reverse()

		

		for i in range(1, len(self.Probs)):
			self.Probs[i] += self.Probs[i-1]

		self.Probs = [0] + self.Probs

		self.calc_fitness()


		self.best_sol = self.population[-1]
	
	def calc_fitness(self):
		# for ind in self.population:
		# 	ind.calc_fitness()

		self.population.sort(key = lambda x: x.fitness)

	def natural_selection(self) -> tuple[Individual, Individual]:

		parent = []
		

		for i in range(2):
			choice = random.uniform(0, self.Probs[-1])

			for i in range(1, len(self.Probs)):
				if self.Probs[i-1] <= choice <= self.Probs[i]:
					parent.append(self.population[i-1])
					break

		return parent

	def k_opt_local_search(self, chromosome, k=1):
		child_chromosome = deepcopy(chromosome)
		for _ in range(k):
			DNA_index = random.randrange(len(child_chromosome))
			gene_index = random.randrange(len(child_chromosome[DNA_index]))
			try:
				child_chromosome[DNA_index][gene_index] = random.choice(self.classes[DNA_index].teachers[self.classes[DNA_index].subjects[gene_index]]).ID
			except:
				child_chromosome[DNA_index][gene_index] = 0
		return child_chromosome
	
	def solve(self):
		
		max_iter = 500
		iteration = 0
		for _ in range(self.g_num):
			if timeit.default_timer() - start_time >= 298:
				break
			iteration += 1
			self.calc_fitness()
			if self.population[-1].fitness > self.best_sol.fitness:
				iteration = 0
				self.best_sol = self.population[-1]
			
			if iteration == max_iter or self.best_sol.fitness[:2] == [self.K, len(self.teaches)]: 
				break

			
			newgen = []
			for _ in range(self.n):
				mom, dad = self.natural_selection()
				child_chromosome = mom.crossover(dad, self.mutation_rate)
				child = Individual(self.classes, self.teaches, self.time_subjects, child_chromosome)

				temp = self.k_opt_local_search(child_chromosome, k = self.k)
				temp = Individual(self.classes, self.teaches, self.time_subjects,temp)

				if temp.fitness > child.fitness:
					child = temp 

				newgen.append(child)
			
			self.population = newgen
	
	def print_sol(self):
		print(self.best_sol.fitness[0])
		for c in self.best_sol.classes:
			c.sol = dict(sorted(c.sol.items()))
			for subject, (period, teacher) in c.sol.items():
				if teacher != 0 and period != 0:
					print(c.ID, subject, period, teacher)
		
	def export_sol(self, file):
		with open(file, 'w') as f:
			f.write(f'{self.best_sol.fitness[0]}\n')
			for c in self.best_sol.classes:
				c.sol = dict(sorted(c.sol.items()))
				for subject, (period, teacher) in c.sol.items():
					if teacher != 0 and period != 0:
						f.write(f'{c.ID} {subject} {period} {teacher}\n')


# inp = file, if inp = False, => reading from input, out is output file, is_print: if print to console
def main(inp, out, is_print):
	classes, teachers, subjects = import_data(inp)
	n = 100
	g_num = 100
	mutation_rate = 0.01
	k = 3

	sol = GA(n, g_num, mutation_rate, k, classes, teachers, subjects)

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

	