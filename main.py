import tkinter as tk
from tkinter import ttk, messagebox
from pulp import *


class OptimizationApp:
    def __init__(self, root):
        self.root = root
        root.title("Оптимізація Q_out")

        # ===== Контейнер для обох зон =====
        self.container = ttk.Frame(root)
        self.container.grid(row=0, column=0, padx=10, pady=10)

        # ===== ЗОНА 1: Введення параметрів =====
        self.frame1 = ttk.LabelFrame(self.container, text="1. Дані пацієнта")
        self.frame1.grid(row=0, column=1, padx=20, pady=5, sticky="nw")

        # Дані X (Об'єкт пацієнта)
        X_initial = {
            1: (118.63, "Вік"),
            2: (35.59, "Вага"),
            3: (96.22, "Кінц.-діастол. об’єм"),
            4: (0.0, "Укріп. некоронарної стулки"),
            5: (0.0, "Ішемія серця"),
            6: (0.0, "Серцева слабкість"),
            7: (0.0, "Блокада серця"),
            8: (23.08, "Діаметр кондуїта"),
        }

        self.X_entries = {}
        for i in range(1, 9):
            label_text = f"X{i} ({X_initial[i][1]})"
            label = ttk.Label(self.frame1, text=label_text)
            label.grid(row=i - 1, column=0, sticky="e")
            entry = ttk.Entry(self.frame1, width=8)
            entry.insert(0, str(X_initial[i][0]))
            entry.grid(row=i - 1, column=1)
            self.X_entries[i] = entry

        # Дані S_in (Обмеження змінних стану)
        S_in_initial = {
            1: (54.92, "Градієнт тиску на аорту"),
            2: (2.32, "Аортальна недостатність"),
            3: (67.78, "Фракція викиду"),
            4: (91.97, "Кінцево-діастолічний індекс"),
        }

        self.S_in_entries = {}
        for i in range(1, 5):
            label_text = f"S_in{i} ({S_in_initial[i][1]})"
            label = ttk.Label(self.frame1, text=label_text)
            label.grid(row=i - 1, column=2, sticky="e")
            entry = ttk.Entry(self.frame1, width=8)
            entry.insert(0, str(S_in_initial[i][0]))
            entry.grid(row=i - 1, column=3)
            self.S_in_entries[i] = entry

        # Початкове значення для Q_in
        Q_in_initial = (5.45, "Град. тиску на лег. артер.")
        self.qin_label = ttk.Label(self.frame1, text=f"Q_in ({Q_in_initial[1]})")
        self.qin_label.grid(row=8, column=0, sticky="e")
        self.qin_entry = ttk.Entry(self.frame1, width=8)
        self.qin_entry.insert(0, str(Q_in_initial[0]))
        self.qin_entry.grid(row=8, column=1)

        # ===== ЗОНА 2: Обмеження =====
        self.frame2 = ttk.LabelFrame(self.container, text="2. Обмеження змінних стану")
        self.frame2.grid(row=1, column=1, padx=20, pady=10, sticky="ne")

        self.constraints = {}
        default_constraints = {
            1: (0.0, 11.0),
            2: (0.0, 1.5),
            3: (49.0, 81.0),
            4: (44.0, 97.0),
            "U1": (0.0, 70.0),
            "U2": (0.0, 99.0),
            "U3": (0.0, 79.0),
        }

        # Для S_out1..4
        for i in range(1, 5):
            min_val, max_val = default_constraints[i]
            min_label = ttk.Label(self.frame2, text=f"S_out{i}_min")
            min_label.grid(row=i - 1, column=0, sticky="e")
            min_entry = ttk.Entry(self.frame2, width=6)
            min_entry.insert(0, str(min_val))
            min_entry.grid(row=i - 1, column=1)

            max_label = ttk.Label(self.frame2, text=f"S_out{i}_max")
            max_label.grid(row=i - 1, column=2, sticky="e")
            max_entry = ttk.Entry(self.frame2, width=6)
            max_entry.insert(0, str(max_val))
            max_entry.grid(row=i - 1, column=3)

            self.constraints[i] = (min_entry, max_entry)

        # Для U1, U2, U3
        for j, u in enumerate(["U1", "U2", "U3"]):
            min_val, max_val = default_constraints[u]
            row = 4 + j

            min_label = ttk.Label(self.frame2, text=f"{u}_min")
            min_label.grid(row=row, column=0, sticky="e")
            min_entry = ttk.Entry(self.frame2, width=6)
            min_entry.insert(0, str(min_val))
            min_entry.grid(row=row, column=1)

            max_label = ttk.Label(self.frame2, text=f"{u}_max")
            max_label.grid(row=row, column=2, sticky="e")
            max_entry = ttk.Entry(self.frame2, width=6)
            max_entry.insert(0, str(max_val))
            max_entry.grid(row=row, column=3)

            self.constraints[u] = (min_entry, max_entry)


        # ===== ЗОНА 3: Результати =====
        self.frame3 = ttk.LabelFrame(root, text="3. Результати оптимізації")
        self.frame3.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        self.result_text = tk.Text(self.frame3, height=20, width=50)
        self.result_text.pack()

        # # ===== ЗОНА 4: Формула з підстановкою =====
        # self.frame4 = ttk.LabelFrame(root, text="4. Задача після підстановки")
        # self.frame4.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        #
        # self.filled_formula = tk.Text(self.frame4, height=10)
        # self.filled_formula.pack()

        # ===== ЗОНА 4: Формула з підстановкою =====
        self.frame4 = ttk.LabelFrame(root, text="")
        self.frame4.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Список складових формули (параметри та коефіцієнти)
        q_out_terms  = [
            ("Q_out = Const", "85.286"),
            ("X[1]", "0.090"),
            ("S_in[2]", "8.083"),
            ("S_in[4]", "-0.255"),
            ("X[5]", "-11.690"),
            ("S_in[3]", "-0.405"),
            ("S_in[1]", "0.169"),
            ("X[4]", "12.829"),
            ("X[8]", "-1.891"),
            ("X[3]", "0.157"),
            ("X[6]", "-28.389"),
            ("X[2]", "-0.319"),
            ("U1", "-0.370"),
            ("Q_in", "-0.737"),
            ("U2", "0.084"),
            ("U1*X[6]/S_in[2]", "0.877"),
            ("U3*X[7]/S_in[1]", "112.634")
        ]

        # Додати також список для S_out1
        s_out1_terms = [
            ("S_out1 = Const", "-1.556"),
            ("X[8]", "0.378"),
            ("S_in[4]", "-0.035"),
            ("S_in[2]", "1.606"),
            ("X[5]", "-5.225"),
            ("Q_in", "-0.124"),
            ("U3 * (S_in[4]/S_in[1])", "-0.005"),
            ("U3 * X[7]/X[3]", "-66.756"),
            ("X[4]", "-1.017"),
            ("X[7]", "1.500")
        ]

        s_out2_terms = [
            ("S_out2 = Const", "1.254"),
            ("S_in[4]", "-0.004"),
            ("S_in[3]", "-0.013"),
            ("S_in[2]", "0.071"),
            ("U1", "0.004"),
            ("U3", "-0.002"),
            ("(U2 * X[8])/S_in[1]", "-0.005"),
            ("X[3]", "-0.005"),
            ("(U1 * X[6])/S_in[2]", "-0.014"),
            ("X[8]", "0.032"),
            ("X[4]", "-0.245"),
            ("X[5]", "-0.429"),
            ("X[2]", "0.011"),
            ("X[1]", "-0.002"),
            ("X[7]", "-0.235")
        ]

        s_out3_terms = [
            ("S_out3 = Const", "42.034"),
            ("S_in[3]", "0.188"),
            ("X[6]", "31.260"),
            ("(U1 * X[6])/S_in[2]", "-0.736"),
            ("X[3]", "-0.032"),
            ("X[4]", "-2.995"),
            ("X[8]", "0.942"),
            ("U2", "-0.099"),
            ("U3", "-0.122"),
            ("S_in[4]", "0.022"),
            ("X[7]", "3.424"),
            ("Q_in", "0.149"),
            ("X[2]", "-0.100"),
            ("(U2 * X[8])/S_in[1]", "-0.061"),
            ("U1", "-0.101"),
            ("(U3 * S_in[4])/S_in[1]", "0.004"),
            ("(U1 * X[2])/X[8]", "0.028")
        ]

        s_out4_terms = [
            ("S_out4 = Const", "70.923"),
            ("S_in[4]", "0.101"),
            ("X[4]", "-4.316"),
            ("X[7]", "-14.317"),
            ("U2", "0.220"),
            ("(U1 * X[2])/X[8]", "0.067"),
            ("X[5]", "-11.246"),
            ("(U3 * X[7])/S_in[1]", "77.399"),
            ("X[8]", "-1.219"),
            ("X[2]", "0.269"),
            ("U3", "0.153"),
            ("X[1]", "-0.056"),
            ("Q_in", "-0.376")
        ]

        # Визначаємо максимальну кількість рядків
        max_len = max(len(q_out_terms), len(s_out1_terms), len(s_out2_terms), len(s_out3_terms), len(s_out4_terms))

        # Доповнюємо до однакової довжини
        def pad_list(lst):
            while len(lst) < max_len:
                lst.append(("", ""))
            return lst

        q_out_terms = pad_list(q_out_terms)
        s_out1_terms = pad_list(s_out1_terms)
        s_out2_terms = pad_list(s_out2_terms)
        s_out3_terms = pad_list(s_out3_terms)
        s_out4_terms = pad_list(s_out4_terms)

        # Виводимо у чотири стовпці: Q_out, S_out1, S_out2, S_out3
        self.term_entries = {}
        for i in range(max_len):
            # Q_out
            label_q = tk.Label(self.frame4, text=q_out_terms[i][0])
            label_q.grid(row=i, column=0, sticky="W", padx=5, pady=2)
            entry_q = tk.Entry(self.frame4, width=12)
            entry_q.grid(row=i, column=1, padx=2, pady=2)
            entry_q.insert(0, q_out_terms[i][1])
            if q_out_terms[i][0]:
                self.term_entries[q_out_terms[i][0]] = entry_q

            # S_out1
            label_s1 = tk.Label(self.frame4, text=s_out1_terms[i][0])
            label_s1.grid(row=i, column=2, sticky="W", padx=20, pady=2)
            entry_s1 = tk.Entry(self.frame4, width=12)
            entry_s1.grid(row=i, column=3, padx=2, pady=2)
            entry_s1.insert(0, s_out1_terms[i][1])
            if s_out1_terms[i][0]:
                self.term_entries[s_out1_terms[i][0]] = entry_s1

            # S_out2
            label_s2 = tk.Label(self.frame4, text=s_out2_terms[i][0])
            label_s2.grid(row=i, column=4, sticky="W", padx=20, pady=2)
            entry_s2 = tk.Entry(self.frame4, width=12)
            entry_s2.grid(row=i, column=5, padx=2, pady=2)
            entry_s2.insert(0, s_out2_terms[i][1])
            if s_out2_terms[i][0]:
                self.term_entries[s_out2_terms[i][0]] = entry_s2

            # S_out3
            label_s3 = tk.Label(self.frame4, text=s_out3_terms[i][0])
            label_s3.grid(row=i, column=6, sticky="W", padx=20, pady=2)
            entry_s3 = tk.Entry(self.frame4, width=12)
            entry_s3.grid(row=i, column=7, padx=2, pady=2)
            entry_s3.insert(0, s_out3_terms[i][1])
            if s_out3_terms[i][0]:
                self.term_entries[s_out3_terms[i][0]] = entry_s3

            # S_out4
            label_s4 = tk.Label(self.frame4, text=s_out4_terms[i][0])
            label_s4.grid(row=i, column=8, sticky="W", padx=20, pady=2)
            entry_s4 = tk.Entry(self.frame4, width=12)
            entry_s4.grid(row=i, column=9, padx=2, pady=2)
            entry_s4.insert(0, s_out4_terms[i][1])
            if s_out4_terms[i][0]:
                self.term_entries[s_out4_terms[i][0]] = entry_s4

        # # ===== ЗОНА 5: Початкова форма задачі =====
        # self.frame5 = ttk.LabelFrame(root, text="5. Початкова форма задачі")
        # self.frame5.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)
        #
        # self.formula_text = tk.Text(self.frame5, height=10)
        # self.formula_text.insert("1.0", "Q_out = функція(X1-X8, S_in1-4, Q_in, U1-U3)")
        # self.formula_text.pack()

        # ===== ЗОНА 5: Початкова форма задачі =====
        self.frame5 = ttk.LabelFrame(root, text="Коєфіцієнти")
        self.frame5.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        # --- Ліва частина: Q_out ---
        self.qout_label = ttk.Label(self.frame5, text="Q_out")
        self.qout_label.grid(row=0, column=0, columnspan=2)

        self.const_label = ttk.Label(self.frame5, text="Const")
        self.const_label.grid(row=1, column=0, sticky="e")
        self.const_entry = ttk.Entry(self.frame5)
        self.const_entry.grid(row=1, column=1)
        self.const_entry.insert(0, "Const = ...")

        self.u1_label = ttk.Label(self.frame5, text="U1")
        self.u1_label.grid(row=2, column=0, sticky="e")
        self.u1_entry = ttk.Entry(self.frame5)
        self.u1_entry.grid(row=2, column=1)
        self.u1_entry.insert(0, "U1 = ...")

        self.u2_label = ttk.Label(self.frame5, text="U2")
        self.u2_label.grid(row=3, column=0, sticky="e")
        self.u2_entry = ttk.Entry(self.frame5)
        self.u2_entry.grid(row=3, column=1)
        self.u2_entry.insert(0, "U2 = ...")

        self.u3_label = ttk.Label(self.frame5, text="U3")
        self.u3_label.grid(row=4, column=0, sticky="e")
        self.u3_entry = ttk.Entry(self.frame5)
        self.u3_entry.grid(row=4, column=1)
        self.u3_entry.insert(0, "U3 = ...")

        # --- Права частина: S_out1 ---
        self.sout1_label = ttk.Label(self.frame5, text="S_out1")
        self.sout1_label.grid(row=0, column=2, columnspan=2)

        self.const1_label = ttk.Label(self.frame5, text="Const")
        self.const1_label.grid(row=1, column=2, sticky="e")
        self.const1_entry = ttk.Entry(self.frame5)
        self.const1_entry.grid(row=1, column=3)
        self.const1_entry.insert(0, "Const = ...")

        self.u1_1_label = ttk.Label(self.frame5, text="U1")
        self.u1_1_label.grid(row=2, column=2, sticky="e")
        self.u1_1_entry = ttk.Entry(self.frame5)
        self.u1_1_entry.grid(row=2, column=3)
        self.u1_1_entry.insert(0, "U1 = ...")

        self.u2_1_label = ttk.Label(self.frame5, text="U2")
        self.u2_1_label.grid(row=3, column=2, sticky="e")
        self.u2_1_entry = ttk.Entry(self.frame5)
        self.u2_1_entry.grid(row=3, column=3)
        self.u2_1_entry.insert(0, "U2 = ...")

        self.u3_1_label = ttk.Label(self.frame5, text="U3")
        self.u3_1_label.grid(row=4, column=2, sticky="e")
        self.u3_1_entry = ttk.Entry(self.frame5)
        self.u3_1_entry.grid(row=4, column=3)
        self.u3_1_entry.insert(0, "U3 = ...")

        # --- Нижче: S_out2 ---
        self.sout2_label = ttk.Label(self.frame5, text="S_out2")
        self.sout2_label.grid(row=5, column=0, columnspan=2)

        self.const2_label = ttk.Label(self.frame5, text="Const")
        self.const2_label.grid(row=6, column=0, sticky="e")
        self.const2_entry = ttk.Entry(self.frame5)
        self.const2_entry.grid(row=6, column=1)
        self.const2_entry.insert(0, "Const = ...")

        self.u1_2_label = ttk.Label(self.frame5, text="U1")
        self.u1_2_label.grid(row=7, column=0, sticky="e")
        self.u1_2_entry = ttk.Entry(self.frame5)
        self.u1_2_entry.grid(row=7, column=1)
        self.u1_2_entry.insert(0, "U1 = ...")

        self.u2_2_label = ttk.Label(self.frame5, text="U2")
        self.u2_2_label.grid(row=8, column=0, sticky="e")
        self.u2_2_entry = ttk.Entry(self.frame5)
        self.u2_2_entry.grid(row=8, column=1)
        self.u2_2_entry.insert(0, "U2 = ...")

        self.u3_2_label = ttk.Label(self.frame5, text="U3")
        self.u3_2_label.grid(row=9, column=0, sticky="e")
        self.u3_2_entry = ttk.Entry(self.frame5)
        self.u3_2_entry.grid(row=9, column=1)
        self.u3_2_entry.insert(0, "U3 = ...")

        # === Зона для S_out3 ===
        self.sout3_label = ttk.Label(self.frame5, text="S_out3")
        self.sout3_label.grid(row=5, column=2, columnspan=2)

        self.const3_label = ttk.Label(self.frame5, text="Const")
        self.const3_label.grid(row=6, column=2, sticky="e")
        self.const3_entry = ttk.Entry(self.frame5)
        self.const3_entry.grid(row=6, column=3)

        self.u1_3_label = ttk.Label(self.frame5, text="U1")
        self.u1_3_label.grid(row=7, column=2, sticky="e")
        self.u1_3_entry = ttk.Entry(self.frame5)
        self.u1_3_entry.grid(row=7, column=3)

        self.u2_3_label = ttk.Label(self.frame5, text="U2")
        self.u2_3_label.grid(row=8, column=2, sticky="e")
        self.u2_3_entry = ttk.Entry(self.frame5)
        self.u2_3_entry.grid(row=8, column=3)

        self.u3_3_label = ttk.Label(self.frame5, text="U3")
        self.u3_3_label.grid(row=9, column=2, sticky="e")
        self.u3_3_entry = ttk.Entry(self.frame5)
        self.u3_3_entry.grid(row=9, column=3)

        # === Зона для S_out4 ===
        self.sout4_label = ttk.Label(self.frame5, text="S_out4")
        self.sout4_label.grid(row=18, column=0, columnspan=2)

        self.const4_label = ttk.Label(self.frame5, text="Const")
        self.const4_label.grid(row=19, column=0, sticky="e")
        self.const4_entry = ttk.Entry(self.frame5)
        self.const4_entry.grid(row=19, column=1)

        self.u1_4_label = ttk.Label(self.frame5, text="U1")
        self.u1_4_label.grid(row=20, column=0, sticky="e")
        self.u1_4_entry = ttk.Entry(self.frame5)
        self.u1_4_entry.grid(row=20, column=1)

        self.u2_4_label = ttk.Label(self.frame5, text="U2")
        self.u2_4_label.grid(row=21, column=0, sticky="e")
        self.u2_4_entry = ttk.Entry(self.frame5)
        self.u2_4_entry.grid(row=21, column=1)

        self.u3_4_label = ttk.Label(self.frame5, text="U3")
        self.u3_4_label.grid(row=22, column=0, sticky="e")
        self.u3_4_entry = ttk.Entry(self.frame5)
        self.u3_4_entry.grid(row=22, column=1)

        # ===== Кнопка запуску =====
        self.solve_button = ttk.Button(root, text="Запустити оптимізацію", command=self.solve_model)
        self.solve_button.grid(row=3, column=0, columnspan=2, pady=10)

        self.update_formula_fields()


        # Кнопка для скидання обмежень зони 1
        self.reset_constraints_button_zone1 = ttk.Button(self.container, text="Скинути дані",
                                                         command=self.reset_zone1_constraints)
        self.reset_constraints_button_zone1.grid(row=0, column=2, pady=5)

        # Кнопка для скидання обмежень зони 2
        self.reset_constraints_button = ttk.Button(self.container, text="Скинути обмеження",
                                                   command=self.reset_zone2_constraints)
        self.reset_constraints_button.grid(row=1, column=2, pady=5)

    def get_val(self, name):
            try:
                if name.startswith("X["):
                    i = int(name[2:-1])
                    return float(self.X_entries[i].get())
                elif name.startswith("S_in["):
                    i = int(name[5:-1])
                    return float(self.S_in_entries[i].get())
                elif name == "Q_in":
                    return float(self.qin_entry.get())
            except (ValueError, KeyError):
                return 0.0
    def update_formula_fields(self):


        X = [self.get_val(f"X[{i}]") for i in range(1, 9)]
        S = [self.get_val(f"S_in[{i}]") for i in range(1, 5)]
        Q_in = self.get_val("Q_in")

        # Обчислення U1, U2, U3
        try:
            U1 = -0.370 + 0.877 * X[5] / S[1]
        except ZeroDivisionError:
            U1 = float('inf')
        try:
            U2 = 0.084 - 0.005 * X[7] / S[0]
        except ZeroDivisionError:
            U2 = float('inf')
        try:
            U3 = 112.634 * X[6] / S[0] - 0.002
        except ZeroDivisionError:
            U3 = float('inf')

        # Основна частина формули Q_out
        Const = (
                85.286 + 0.090 * X[0] + 8.083 * S[1] - 0.255 * S[3] - 11.690 * X[4] - 0.405 * S[2] +
                0.169 * S[0] + 12.829 * X[3] - 1.891 * X[7] + 0.157 * X[2] - 28.389 * X[5] -
                0.319 * X[1] - 0.737 * Q_in
        )

        # Запис результатів у відповідні поля
        self.const_entry.delete(0, tk.END)
        self.const_entry.insert(0, f"{Const:.3f}")

        self.u1_entry.delete(0, tk.END)
        self.u1_entry.insert(0, f"{U1:.3f}")

        self.u2_entry.delete(0, tk.END)
        self.u2_entry.insert(0, f"{U2:.3f}")

        self.u3_entry.delete(0, tk.END)
        self.u3_entry.insert(0, f"{U3:.3f}")

        # === Обчислення для S_out1 ===
        try:
            const1 = (
                -1.556 + 0.378 * X[7] - 0.035 * S[3] + 1.606 * S[1]
                - 5.225 * X[4] - 0.124 * Q_in - 1.017 * X[3] + 1.500 * X[6]
            )
        except IndexError:
            const1 = float('inf')

        u1_1 = 0
        u2_1 = 0
        try:
            u3_1 = -((0.005 * S[3]) / S[0] + (66.756 * X[6]) / X[2])
        except ZeroDivisionError:
            u3_1 = float('inf')

        self.const1_entry.delete(0, tk.END)
        self.const1_entry.insert(0, f"{const1:.3f}")

        self.u1_1_entry.delete(0, tk.END)
        self.u1_1_entry.insert(0, f"{u1_1:.3f}")

        self.u2_1_entry.delete(0, tk.END)
        self.u2_1_entry.insert(0, f"{u2_1:.3f}")

        self.u3_1_entry.delete(0, tk.END)
        self.u3_1_entry.insert(0, f"{u3_1:.3f}")

        # === Обчислення для S_out2 ===
        try:
            const2 = (
                    1.254 - 0.004 * S[3] - 0.013 * S[2] + 0.071 * S[1]
                    - 0.005 * X[2] + 0.032 * X[7] - 0.245 * X[3]
                    - 0.429 * X[4] + 0.011 * X[1] - 0.002 * X[0] - 0.235 * X[6]
            )
        except IndexError:
            const2 = float('inf')

        try:
            u1_2 = 0.004 - 0.014 * X[5] / S[1]
        except ZeroDivisionError:
            u1_2 = float('inf')

        try:
            u2_2 = -0.005 * X[7] / S[0]
        except ZeroDivisionError:
            u2_2 = float('inf')

        u3_2 = -0.002

        self.const2_entry.delete(0, tk.END)
        self.const2_entry.insert(0, f"{const2:.3f}")

        self.u1_2_entry.delete(0, tk.END)
        self.u1_2_entry.insert(0, f"{u1_2:.3f}")

        self.u2_2_entry.delete(0, tk.END)
        self.u2_2_entry.insert(0, f"{u2_2:.3f}")

        self.u3_2_entry.delete(0, tk.END)
        self.u3_2_entry.insert(0, f"{u3_2:.3f}")

        # === Обчислення для S_out3 ===
        try:
            const3 = (
                    42.034 + 0.188 * S[2] + 31.260 * X[5] - 0.032 * X[2] - 2.995 * X[3]
                    + 0.942 * X[7] + 0.022 * S[3] + 3.424 * X[6] + 0.149 * Q_in - 0.100 * X[1]
            )
        except IndexError:
            const3 = float('inf')

        try:
            u1_3 = -0.101 - 0.736 * X[5] / S[1] + 0.028 * X[1] / X[7]
        except ZeroDivisionError:
            u1_3 = float('inf')

        try:
            u2_3 = -0.099 - 0.061 * X[7] / S[0]
        except ZeroDivisionError:
            u2_3 = float('inf')

        u3_3 = -0.122 + 0.004 * S[3] / S[0]

        self.const3_entry.delete(0, tk.END)
        self.const3_entry.insert(0, f"{const3:.3f}")

        self.u1_3_entry.delete(0, tk.END)
        self.u1_3_entry.insert(0, f"{u1_3:.3f}")

        self.u2_3_entry.delete(0, tk.END)
        self.u2_3_entry.insert(0, f"{u2_3:.3f}")

        self.u3_3_entry.delete(0, tk.END)
        self.u3_3_entry.insert(0, f"{u3_3:.3f}")

        # === Обчислення для S_out4 ===
        try:
            const4 = (
                    70.923 + 0.101 * S[3] - 4.316 * X[3] - 14.317 * X[6] - 11.246 * X[4]
                    - 1.219 * X[7] + 0.269 * X[1] - 0.056 * X[0] - 0.376 * Q_in
            )
        except IndexError:
            const4 = float('inf')

        try:
            u1_4 = 0.067 * X[1] / X[7]
        except ZeroDivisionError:
            u1_4 = float('inf')

        u2_4 = 0.220

        try:
            u3_4 = 0.153 + 77.399 * X[6] / S[0]
        except ZeroDivisionError:
            u3_4 = float('inf')

        self.const4_entry.delete(0, tk.END)
        self.const4_entry.insert(0, f"{const4:.3f}")

        self.u1_4_entry.delete(0, tk.END)
        self.u1_4_entry.insert(0, f"{u1_4:.3f}")

        self.u2_4_entry.delete(0, tk.END)
        self.u2_4_entry.insert(0, f"{u2_4:.3f}")

        self.u3_4_entry.delete(0, tk.END)
        self.u3_4_entry.insert(0, f"{u3_4:.3f}")

    def reset_zone1_constraints(self):
        # Оновлюємо значення для зони 1 до дефолтних
        self.X_initial = {
            1: (118.63, "Вік"),
            2: (35.59, "Вага"),
            3: (96.22, "Кінц.-діастол. об’єм"),
            4: (0.0, "Укріп. некоронарної стулки"),
            5: (0.0, "Ішемія серця"),
            6: (0.0, "Серцева слабкість"),
            7: (0.0, "Блокада серця"),
            8: (23.08, "Діаметр кондуїта"),
        }
        for i in range(1, 9):
            self.X_entries[i].delete(0, 'end')  # Очищаємо поточне значення
            self.X_entries[i].insert(0, str(self.X_initial[i][0]))  # Вставляємо дефолтне значення

            # Оновлення значень для S_in
        S_in_initial = {
            1: (54.92, "Градієнт тиску на аорту"),
            2: (2.32, "Аортальна недостатність"),
            3: (67.78, "Фракція викиду"),
            4: (91.97, "Кінцево-діастолічний індекс"),
        }

        for i in range(1, 5):
            self.S_in_entries[i].delete(0, 'end')  # Очищаємо поточне значення
            self.S_in_entries[i].insert(0, str(S_in_initial[i][0]))  # Вставляємо дефолтне значення

        # Оновлення значення для Q_in
        Q_in_initial = (5.45, "Град. тиску на лег. артер.")
        self.qin_entry.delete(0, 'end')  # Очищаємо поточне значення
        self.qin_entry.insert(0, str(Q_in_initial[0]))  # Вставляємо дефолтне значення

    def reset_zone2_constraints(self):
        # Дефолтні значення для зони 2
        default_constraints = {
            1: (0.0, 11.0),
            2: (0.0, 1.5),
            3: (49.0, 81.0),
            4: (44.0, 97.0),
            "U1": (0.0, 70.0),
            "U2": (0.0, 99.0),
            "U3": (0.0, 79.0),
        }

        # Оновлення значень для кожного поля
        for var, (min_val, max_val) in default_constraints.items():
            if var in self.constraints:
                min_entry, max_entry = self.constraints[var]
                # Очищаємо поля і встановлюємо дефолтні значення
                min_entry.delete(0, tk.END)
                min_entry.insert(0, str(min_val))
                max_entry.delete(0, tk.END)
                max_entry.insert(0, str(max_val))


    def solve_model(self):
        try:
            # Вхідні значення
            X = {i: float(self.X_entries[i].get()) for i in self.X_entries}
            S_in = {i: float(self.S_in_entries[i].get()) for i in self.S_in_entries}
            Q_in = float(self.qin_entry.get())

            # Створення моделі
            model = LpProblem("Q_out_Optimization", LpMinimize)
            # Зчитування меж з GUI
            U1_min = float(self.constraints["U1"][0].get())
            U1_max = float(self.constraints["U1"][1].get())
            U2_min = float(self.constraints["U2"][0].get())
            U2_max = float(self.constraints["U2"][1].get())
            U3_min = float(self.constraints["U3"][0].get())
            U3_max = float(self.constraints["U3"][1].get())

            # Створення змінних
            U1 = LpVariable("U1", U1_min, U1_max)
            U2 = LpVariable("U2", U2_min, U2_max)
            U3 = LpVariable("U3", U3_min, U3_max)

            Q_out = (
                85.286 + 0.090*X[1] + 8.083*S_in[2] - 0.255*S_in[4] - 11.690*X[5] -
                0.405*S_in[3] + 0.169*S_in[1] + 12.829*X[4] - 1.891*X[8] + 0.157*X[3] -
                28.389*X[6] - 0.319*X[2] - 0.737*Q_in +
                U1 * (-0.370 + 0.877 * X[6]/S_in[2]) +
                U2 * (0.084 - 0.005 * X[8]/S_in[1]) +
                U3 * (112.634 * X[7]/S_in[1] - 0.002)
            )

            model += Q_out

            # Обмеження
            S_out = {}

            S_out[1] = (-1.556 + 0.378 * X[8] - 0.035 * S_in[4] + 1.606 * S_in[2] -
                        5.225 * X[5] - 0.124 * Q_in -
                        U3 * (((0.005 * S_in[4]) / S_in[1]) + ((66.756 * X[7]) / X[3])) -
                        1.017 * X[4] + 1.500 * X[7])

            S_out[2] = (1.254 - 0.004 * S_in[4] - 0.013 * S_in[3] + 0.071 * S_in[2] -
                        0.005 * (U2 * X[8])/S_in[1] - 0.005 * X[3] + 0.032 * X[8] -
                        0.245 * X[4] - 0.429 * X[5] + 0.011 * X[2] - 0.002 * X[1] -
                        0.235 * X[7] + U1 * 0.004 - U3 * 0.002 +
                        U2 * (-0.005 * X[8]/S_in[1]))

            S_out[3] = (42.034 + 0.188 * S_in[3] + 31.260 * X[6] - 0.032 * X[3] -
                        2.995 * X[4] + 0.942 * X[8] + 0.022 * S_in[4] + 3.424 * X[7] +
                        0.149 * Q_in +
                        U1 * (-0.101 - 0.736 * X[6]/S_in[2] + 0.028 * X[2]/X[8]) +
                        U2 * (-0.099 - 0.061 * X[8]/S_in[1]) +
                        U3 * (-0.122 + 0.004 * S_in[4]/S_in[1]))

            S_out[4] = (70.923 + 0.101 * S_in[4] - 4.316 * X[4] - 14.317 * X[7] -
                        11.246 * X[5] - 1.219 * X[8] + 0.269 * X[2] - 0.056 * X[1] -
                        0.376 * Q_in +
                        U1 * (0.067 * X[2]/X[8]) + U2 * 0.220 +
                        U3 * (0.153 + 77.399 * X[7]/S_in[1]))

            for i in range(1, 5):
                min_val = float(self.constraints[i][0].get())
                max_val = float(self.constraints[i][1].get())
                model += S_out[i] >= min_val
                model += S_out[i] <= max_val

            model.solve()

            if LpStatus[model.status] != "Optimal":
                raise Exception(f"Модель не знайдена: статус – {LpStatus[model.status]}")

            # Виведення результатів
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Status: {LpStatus[model.status]}\n")
            self.result_text.insert(tk.END, f"U1 = {value(U1):.4f}\n")
            self.result_text.insert(tk.END, f"U2 = {value(U2):.4f}\n")
            self.result_text.insert(tk.END, f"U3 = {value(U3):.4f}\n")
            self.result_text.insert(tk.END, f"Q_out = {value(Q_out):.4f}\n")

            for i in range(1, 5):
                self.result_text.insert(tk.END, f"S_out{i} = {value(S_out[i]):.4f}\n")
            # for i in range(1, 5):
            #     self.result_text.insert(tk.END, f"S_out{i} = {abs(value(S_out[i])):.4f}\n")

            Q_norm = (value(Q_out) - 0) / (200 - 0)
            self.result_text.insert(tk.END, f"Нормалізований Q_out = {Q_norm:.4f}\n")

            # # Формування виразу з підстановками
            # formula_filled = f"""Q_out = 85.286 + 0.090*{X[1]} + 8.083*{S_in[2]} - 0.255*{S_in[4]} - 11.690*{X[5]} -
            # 0.405*{S_in[3]} + 0.169*{S_in[1]} + 12.829*{X[4]} - 1.891*{X[8]} + 0.157*{X[3]} -
            # 28.389*{X[6]} - 0.319*{X[2]} - 0.737*{Q_in} +
            # U1*(-0.370 + 0.877*{X[6]}/{S_in[2]}) +
            # U2*(0.084 - 0.005*{X[8]}/{S_in[1]}) +
            # U3*(112.634*{X[7]}/{S_in[1]} - 0.002)"""

            self.update_formula_fields()
            # self.filled_formula.delete(1.0, tk.END)
            # self.filled_formula.insert(tk.END, formula_filled)

        except Exception as e:
            messagebox.showerror("Помилка", f"Сталася помилка під час обчислення:\n{e}")


# Запуск програми
if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizationApp(root)
    root.mainloop()
