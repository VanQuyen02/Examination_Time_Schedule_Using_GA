import numpy as np

class GeneticAlgorithm:
    def __init__(self, schedule, population_size, mutation_rate, crossover_rate, elite_rate):
        self.schedule = schedule
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_rate = elite_rate

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            chromosome = self.schedule.create_chromosome()
            population.append(chromosome)
        return population

    def selection(self, population):
        # Randomly select φ individuals from population and return the best individual based on fitness value among them
        phi = 5
        selected_parents = np.random.choice(population, phi, replace=False)
        best_parent = min(selected_parents, key=lambda x: self.schedule.get_fitness(x))
        return best_parent

    def crossover(self,population):
        # Rearrange population in ascending fitness order
        population_sorted = sorted(population, key=lambda x: self.schedule.get_fitness(x))
        top_phi_items = population_sorted[:(self.population_size*self.elite_rate)]
        parent_1 = self.selection(top_phi_items)
        parent_2 = self.selection(top_phi_items)
        while parent_1 == parent_2:
            parent_2 = self.selection(top_phi_items)
        crossover_prob = np.random.random()
        w = self.crossover_rate # Example crossover rate
        omega = self.mutation_rate # Example mutation rate

        if crossover_prob <= w:
            # Exchange genes between parents
            child_1 = np.copy(parent_1)
            child_2 = np.copy(parent_2)
            for s in range(child_1.shape[0]):
                if np.random.random() < w:  # Randomly choose to exchange genes
                    child_1[s], child_2[s] = child_2[s], child_1[s]
        elif w < crossover_prob <= omega:
            # Perform mutation on one parent
            if np.random.random() < w:
                child_1 = self.mutation(parent_1)
                child_2 = np.copy(parent_2)
            else:
                child_1 = np.copy(parent_1)
                child_2 = self.mutation(parent_2)
        else:
            # Keep parents as they are
            child_1 = np.copy(parent_1)
            child_2 = np.copy(parent_2)

        # # Repair offspring
        # child_1 = self.repair(child_1)
        # child_2 = self.repair(child_2)

        return child_1, child_2


    def repair_offspring(self, offspring):
        pass

    def mutation(self, chromosome):
        mutated_chromosome = np.copy(chromosome)
        mutation_prob = self.mutation_rate

        # Randomly select two different subjects within the chromosome
        subject_indices = np.random.choice(chromosome.shape[0], 2, replace=False)

        if np.random.random() < mutation_prob:
            # Swap the entire data related to the selected subjects
            mutated_chromosome[subject_indices[0]], mutated_chromosome[subject_indices[1]] = mutated_chromosome[subject_indices[1]], mutated_chromosome[subject_indices[0]]

        # Repair the chromosome
        # mutated_chromosome = self.repair_offspring(mutated_chromosome)
        
        return mutated_chromosome

    
    def evolve_population(self, population):
        next_generation = []

        # Elitism: Keep the elite individuals
        next_generation.extend(sorted(population, key=lambda x: self.schedule.get_fitness(x))[:int(self.elite_rate*self.population_size)])

        # Selection, Crossover, Mutation
        while len(next_generation) < self.population_size:
            offspring1, offspring2 = self.crossover(population)
            next_generation.extend([offspring1, offspring2])

        return next_generation 

    def run(self, num_generations):
        population = self.initialize_population()

        for generation in range(num_generations):
            print(f"Generation {generation + 1}")
            population = self.evolve_population(population)

            # Termination condition - you may use various conditions such as reaching a maximum number of generations or finding a satisfactory solution
            # For simplicity, we just print the best fitness value found so far in each generation
            best_fitness = self.schedule.get_fitness(sorted(population, key=lambda x: self.schedule.get_fitness(x))[0])
            print(f"Generation {generation + 1}, Best Fitness: {best_fitness}")

        # After optimization, return the best chromosome found
        best_chromosome = sorted(population, key=lambda x: self.schedule.get_fitness(x))[0]
        return best_chromosome