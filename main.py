import random
import pygal
from remi import gui
from remi import start, App
from io import BytesIO
import base64


class GeneticScheduler:
    def __init__(self, input_file, population_size=20, generations=100, mutation_rate=0.1):
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
        """
        Tạo cá thể thời khóa biểu đảm bảo:
        - Mỗi ngày có ít nhất 3 tiết.
        - Tiết học được sắp xếp từ Tiết 1 trở đi.
        """
        schedule = []
        day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
        time_slots = [f"Tiết {i + 1}" for i in range(5)]  # 5 tiết buổi sáng

        # Shuffle input data
        random.shuffle(data)
        day_schedule = {day: [] for day in day_names}

        for entry in data:
            subject, teacher, _class = entry
            # Phân bổ lớp học vào ngày còn chỗ trống
            for day in day_names:
                if len(day_schedule[day]) < 3:  # Mỗi ngày tối thiểu 3 tiết
                    slot = time_slots[len(day_schedule[day])]  # Lấy tiết học
                    day_schedule[day].append([day, slot, _class, subject, teacher])
                    break

        # Chuyển từ dictionary sang danh sách
        for day in day_names:
            schedule.extend(day_schedule[day])

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
        day_slot_count = {}

        for entry in schedule:
            day, time, _class, subject, teacher = entry

            # Kiểm tra trùng tiết của giáo viên
            teacher_schedule.setdefault(teacher, []).append((day, time))
            if teacher_schedule[teacher].count((day, time)) > 1:
                score -= 10  # Trừ điểm nếu giáo viên bị trùng lịch

            # Đếm số tiết mỗi ngày
            day_slot_count.setdefault(day, []).append(time)

        # Kiểm tra xem mỗi ngày có ít nhất 3 tiết
        for day, slots in day_slot_count.items():
            if len(slots) < 3:
                score -= 5 * (3 - len(slots))  # Trừ điểm nếu ngày đó thiếu tiết

        return score

    def selection(self, population):
        sorted_population = sorted(population, key=self.fitness, reverse=True)
        selected_population = sorted_population[:max(2, len(sorted_population) // 2)]
        
        if len(selected_population) < 2:
            selected_population += sorted_population[:2]
        return selected_population    
    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, len(parent1) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        return child

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            for entry in individual:
                # Thay đổi giờ học
                new_time_slot = random.randint(1, 5)
                entry[1] = f"Tiết {new_time_slot}"
        return individual

    def run(self):
        data = self.load_data()
        population = self.initialize_population(data)

        for generation in range(self.generations):
            selected_population = self.selection(population)
            new_population = []
            for i in range(0, len(selected_population) - 1, 2):
                parent1, parent2 = selected_population[i], selected_population[i + 1]
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            population = new_population

            fitness_values = [self.fitness(ind) for ind in population]
            self.fitness_history.append({"best": max(fitness_values)})

        best_individual = max(population, key=self.fitness)

        # Chuyển thời khóa biểu thành bảng 2D
        timetable = [["" for _ in range(6)] for _ in range(5)]  # 5 tiết, 6 ngày
        day_indices = {"Thứ 2": 0, "Thứ 3": 1, "Thứ 4": 2, "Thứ 5": 3, "Thứ 6": 4, "Thứ 7": 5}

        for entry in best_individual:
            day, time, _class, subject, teacher = entry
            day_index = day_indices[day]
            time_index = int(time.split(" ")[1]) - 1
            timetable[time_index][day_index] = f"{subject} - {_class} ({teacher})"

        return timetable

class TimetableApp(App):
    def __init__(self, *args):
        super(TimetableApp, self).__init__(*args)

    def main(self):
        self.main_container = gui.VBox(width=800, height=600, style={'margin': 'auto', 'padding': '10px'})
        label = gui.Label("Quản lý thời khóa biểu", style={'font-size': '24px', 'font-weight': 'bold'})

        self.btn_input = gui.Button("Nhập Dữ Liệu", width=200, height=30)
        self.btn_input.onclick.connect(self.show_input)

        self.btn_generate = gui.Button("Tạo Thời Khóa Biểu", width=200, height=30)
        self.btn_generate.onclick.connect(self.generate_schedule)

        self.btn_show_chart = gui.Button("Hiển Thị Biểu Đồ Đánh Giá", width=200, height=30)
        self.btn_show_chart.onclick.connect(self.show_fitness_chart)

        self.table = gui.Table.new_from_list([["Ngày", "Tiết", "Lớp", "Môn học", "Giáo viên"]], width='100%')
        self.table = gui.Table.new_from_list([["Ngày", "Tiết", "Lớp", "Môn học", "Giáo viên"]], width='100%', style={'border': '1px solid black', 'text-align': 'center'})

        self.chart_container = gui.Image(width='100%', height='auto')

        self.main_container.append([label, self.btn_input, self.btn_generate, self.btn_show_chart, self.table, self.chart_container])
        return self.main_container

    def show_input(self, widget):
        input_window = gui.VBox(width=400, height=300, style={'margin': 'auto', 'padding': '10px', 'border': '1px solid black'})
        input_window.append(gui.Label("Nhập thông tin", style={'font-size': '18px', 'font-weight': 'bold', 'text-align': 'center'}))

        self.subject_input = gui.TextInput(single_line=True, hint="Nhập môn học", style={'width': '100%'})
        self.teacher_input = gui.TextInput(single_line=True, hint="Nhập giáo viên", style={'width': '100%'})
        self.class_input = gui.TextInput(single_line=True, hint="Nhập lớp học", style={'width': '100%'})

        save_button = gui.Button("Lưu", style={'margin-top': '10px'})
        save_button.onclick.connect(self.save_input_data)

        input_window.append([self.subject_input, self.teacher_input, self.class_input, save_button])
        self.main_container.append(input_window)

    def save_input_data(self, widget):
        subject = self.subject_input.get_value()
        teacher = self.teacher_input.get_value()
        _class = self.class_input.get_value()

        if not all([subject, teacher, _class]):
            self.main_container.append(gui.Label("Vui lòng nhập đầy đủ thông tin.", style={'color': 'red'}))
            return

        with open("input_data.txt", "a", encoding="utf-8") as file:
            file.write(f"{subject},{teacher},{_class}\n")

        self.main_container.append(gui.Label("Đã lưu dữ liệu thành công.", style={'color': 'green'}))

    def generate_schedule(self, widget):
        self.scheduler = GeneticScheduler("input_data.txt")
        try:
            timetable = self.scheduler.run()

            if not timetable:
                self.main_container.append(gui.Label("Thời khóa biểu không thể tạo được do dữ liệu không đủ.", style={'color': 'red'}))
                return

            # Làm trống danh sách hiển thị cũ nếu có
            if hasattr(self, 'list_view'):
                self.main_container.remove_child(self.list_view)

            # Tạo danh sách mới để hiển thị thời khóa biểu
            self.list_view = gui.VBox(width='100%', style={'margin-top': '20px', 'padding': '10px'})

            day_names = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]

            for day_index, day_name in enumerate(day_names):
                day_label = gui.Label(f"{day_name}:", style={'font-size': '18px', 'font-weight': 'bold', 'margin-top': '10px'})
                self.list_view.append(day_label)

                has_schedule = False  # Đánh dấu nếu ngày có lịch học

                for entry in timetable:
                    if entry[0] == day_name:
                        has_schedule = True
                        time, _class, subject, teacher = entry[1], entry[2], entry[3], entry[4]
                        entry_label = gui.Label(
                            f"  - {time}: {subject} - {_class} ({teacher})", 
                            style={'font-size': '16px', 'margin-left': '20px'}
                        )
                        self.list_view.append(entry_label)

                if not has_schedule:
                    no_schedule_label = gui.Label("  - Không có tiết học.", style={'font-size': '16px', 'margin-left': '20px', 'color': 'gray'})
                    self.list_view.append(no_schedule_label)

            self.main_container.append(self.list_view)
            self.main_container.append(gui.Label("Thời khóa biểu đã được tạo thành công.", style={'color': 'green'}))
        except ValueError as e:
            self.main_container.append(gui.Label(str(e), style={'color': 'red'}))

    def show_fitness_chart(self, widget):
        if not hasattr(self, 'scheduler') or not hasattr(self.scheduler, 'fitness_history') or not self.scheduler.fitness_history:
            self.main_container.append(gui.Label("Hãy tạo thời khóa biểu trước khi hiển thị biểu đồ.", style={'color': 'red'}))
            return

        # Tách dữ liệu fitness từ lịch sử
        generations = range(1, len(self.scheduler.fitness_history) + 1)
        best_fitness = [entry["best"] for entry in self.scheduler.fitness_history]

        # Tạo biểu đồ bằng Pygal
        chart = pygal.Line()
        chart.title = 'Biểu đồ Đánh Giá Fitness Qua Các Thế Hệ'
        chart.x_labels = [str(gen) for gen in generations]

        if best_fitness:
            chart.add('Best Fitness', best_fitness)

        # Lưu biểu đồ vào buffer
        chart_data = chart.render()
        chart_data_base64 = base64.b64encode(chart_data).decode('utf-8')

        # Hiển thị biểu đồ trên giao diện
        self.chart_container.attributes['src'] = f"data:image/svg+xml;base64,{chart_data_base64}"
        self.main_container.append(self.chart_container)

if __name__ == "__main__":
    start(TimetableApp, address="0.0.0.0", port=8080)