from Data import Data
from Schedule import Schedule
from GA_Algorithm import GeneticAlgorithm

if __name__ == "__main__":
    # Load data
    data = Data()
    data.load_data()

    # Define parameters
    population_size = 50
    num_generations = 100
    crossover_rate = 0.3
    mutation_rate = 0.1
    elite_rate = 0.1
    # Initialize Genetic Algorithm
    ga = GeneticAlgorithm(
        schedule=Schedule(data),
        population_size=population_size,
        mutation_rate=mutation_rate,
        crossover_rate=crossover_rate,
        elite_rate = elite_rate  # Define the elite size here
    )

    # Run Genetic Algorithm
    best_chromosome = ga.run(num_generations)

    # Print the best fitness value and the corresponding schedule
    best_fitness = ga.schedule.get_fitness(best_chromosome)
    print("Best fitness:", best_fitness)
    print("Best schedule:")
    print(best_chromosome)