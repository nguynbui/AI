import random


class GeneticScheduler:
    def __init__(self, input_file, population_size=10, generations=100, mutation_rate=0.1):
        self.input_file = input_file
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.fitness_history = []  # Lưu trữ fitness tốt nhất qua các thế hệ

    def load_data(self):
        with open(self.input_file, "r", encoding="utf-8") as file:
            data = [line.strip().split(",") for line in file.readlines()]
        if len(data) < 2:
            raise ValueError("Dữ liệu đầu vào không đủ để tạo thời khóa biểu.")
        return data

    def create_individual(self, data):
        schedule = []
        time_slot = 7
        for i, (subject, teacher, _class) in enumerate(data):
            if time_slot >= 17:
                time_slot = 7
            time = f"Tiết {i+1}: {time_slot}h-{time_slot+1}h"
            schedule.append([time, _class, subject, teacher])
            time_slot += 1
        return schedule

    def initialize_population(self, data):
        population = []
        for _ in range(self.population_size):
            random.shuffle(data)
            individual = self.create_individual(data)
            population.append(individual)
        return population

    def fitness(self, schedule):
        score = 0
        teacher_schedule = {}
        for entry in schedule:
            time, _class, subject, teacher = entry
            teacher_schedule.setdefault(teacher, []).append(time)

        for times in teacher_schedule.values():
            if len(times) > len(set(times)):
                score -= 10

        return score

    def selection(self, population):
        sorted_population = sorted(population, key=self.fitness, reverse=True)
        return sorted_population[:max(2, len(sorted_population) // 2)]

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        return parent1[:crossover_point] + parent2[crossover_point:]

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            mutate_index = random.randint(0, len(individual) - 1)
            individual[mutate_index][1] += "X"
        return individual

    def run(self):
        data = self.load_data()
        population = self.initialize_population(data)

        for generation in range(self.generations):
            selected_population = self.selection(population)
            if len(selected_population) < 2:
                raise ValueError("Quần thể không đủ cá thể để thực hiện giao phối.")
            
            new_population = []
            for i in range(0, len(selected_population) - 1, 2):
                parent1, parent2 = selected_population[i], selected_population[i + 1]
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)

            population = new_population

            # Lưu fitness tốt nhất của thế hệ này
            best_fitness = max(self.fitness(ind) for ind in population)
            self.fitness_history.append(best_fitness)

        best_individual = max(population, key=self.fitness)
        return [["Thời Gian", "Lớp", "Môn", "Giáo Viên"]] + best_individual
