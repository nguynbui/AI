import random
import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd

class GeneticScheduler:
    def __init__(self, input_file, population_size=20, generations=100, mutation_rate=0.1):
        self.input_file = input_file
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.fitness_history = []

    def load_data(self):
        with open(self.input_file, "r", encoding="utf-8") as file:
            data = [line.strip().split(",") for line in file.readlines()]
        if len(data) < 2:
            raise ValueError("Không đủ dữ liệu để tạo thời khóa biểu.")
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

class TimetableApp:
    def __init__(self, master):
        self.master = master
        master.title("Quản Lý Thời Khóa Biểu")
        master.geometry("800x700")

        # Nút nhập dữ liệu
        self.btn_input = tk.Button(master, text="Nhập Dữ Liệu", command=self.show_input_dialog)
        self.btn_input.pack(pady=10)

        # Nút tạo thời khóa biểu
        self.btn_generate = tk.Button(master, text="Tạo Thời Khóa Biểu", command=self.generate_schedule)
        self.btn_generate.pack(pady=10)

        # Nút hiển thị biểu đồ fitness
        self.btn_show_chart = tk.Button(master, text="Hiển Thị Biểu Đồ Đánh Giá", command=self.show_fitness_chart)
        self.btn_show_chart.pack(pady=10)

        # Bảng thời khóa biểu
        self.table_frame = tk.Frame(master)
        self.table_frame.pack(pady=10)

        self.scheduler = None

    def show_input_dialog(self):
        input_window = tk.Toplevel(self.master)
        input_window.title("Nhập Thông Tin")
        input_window.geometry("300x250")

        # Nhãn và ô nhập
        tk.Label(input_window, text="Nhập Môn Học").pack()
        subject_input = tk.Entry(input_window)
        subject_input.pack()

        tk.Label(input_window, text="Nhập Giáo Viên").pack()
        teacher_input = tk.Entry(input_window)
        teacher_input.pack()

        tk.Label(input_window, text="Nhập Lớp Học").pack()
        class_input = tk.Entry(input_window)
        class_input.pack()

        def save_data():
            subject = subject_input.get()
            teacher = teacher_input.get()
            _class = class_input.get()

            if not all([subject, teacher, _class]):
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin.")
                return

            with open("input_data.txt", "a", encoding="utf-8") as file:
                file.write(f"{subject},{teacher},{_class}\n")
            
            messagebox.showinfo("Thành Công", "Đã lưu dữ liệu thành công.")
            input_window.destroy()

        save_button = tk.Button(input_window, text="Lưu", command=save_data)
        save_button.pack(pady=10)

    def generate_schedule(self):
        try:
            self.scheduler = GeneticScheduler("input_data.txt")
            timetable = self.scheduler.run()

            # Xóa bảng cũ nếu tồn tại
            for widget in self.table_frame.winfo_children():
                widget.destroy()

            # Tạo bảng mới
            headers = ["Tiết"] + ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
            
            # Tạo tiêu đề
            for j, header in enumerate(headers):
                label = tk.Label(self.table_frame, text=header, relief=tk.RIDGE, width=15, font=('Arial', 10, 'bold'))
                label.grid(row=0, column=j, sticky='nsew')

            # Thêm nội dung thời khóa biểu
            for i, row in enumerate(timetable):
                # Cột tiết
                label = tk.Label(self.table_frame, text=f"Tiết {i+1}", relief=tk.RIDGE, width=15)
                label.grid(row=i+1, column=0, sticky='nsew')

                # Các cột ngày
                for j, cell in enumerate(row):
                    label = tk.Label(self.table_frame, text=cell or "", relief=tk.RIDGE, width=15, wraplength=100)
                    label.grid(row=i+1, column=j+1, sticky='nsew')

            messagebox.showinfo("Thành Công", "Thời khóa biểu đã được tạo.")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def show_fitness_chart(self):
        if not self.scheduler or not self.scheduler.fitness_history:
            messagebox.showwarning("Cảnh Báo", "Hãy tạo thời khóa biểu trước khi hiển thị biểu đồ.")
            return

        # Tách dữ liệu fitness từ lịch sử
        generations = range(1, len(self.scheduler.fitness_history) + 1)
        best_fitness = [entry["best"] for entry in self.scheduler.fitness_history]

        # Tạo biểu đồ bằng matplotlib
        plt.figure(figsize=(10, 5))
        plt.plot(generations, best_fitness, marker='o')
        plt.title('Biểu Đồ Đánh Giá Fitness Qua Các Thế Hệ')
        plt.xlabel('Thế Hệ')
        plt.ylabel('Fitness')
        plt.grid(True)
        plt.show()

def main():
    root = tk.Tk()
    app = TimetableApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()