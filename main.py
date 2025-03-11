import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import random
import csv

class QuestionBankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("屹筠题库软件")
        self.questions = []
        self.type_questions = {}
        self.current_question = None
        self.current_mode = "random"
        self.question_queue = []
        self.queue_index = 0

        # ---------------------------- 菜单栏 ----------------------------
        self.menubar = tk.Menu(root)

        # 文件菜单
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="导入题库", command=self.import_questions, accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=root.quit)
        self.menubar.add_cascade(label="文件", menu=self.file_menu)

        # 题目类型菜单
        self.type_menu = tk.Menu(self.menubar, tearoff=0)
        self.type_menu.add_radiobutton(label="随机模式", command=lambda: self.set_mode("random"))
        self.type_menu.add_separator()
        self.type_menu.add_radiobutton(label="选择题", command=lambda: self.set_mode("choice"))
        self.type_menu.add_radiobutton(label="填空题", command=lambda: self.set_mode("fill"))
        self.type_menu.add_radiobutton(label="简答题", command=lambda: self.set_mode("short"))
        self.type_menu.add_radiobutton(label="案例分析", command=lambda: self.set_mode("case"))
        self.type_menu.add_radiobutton(label="综合运用", command=lambda: self.set_mode("comprehensive"))
        self.menubar.add_cascade(label="题目类型", menu=self.type_menu)

        # 帮助菜单
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="软件使用方法", command=self.show_usage)
        self.help_menu.add_command(label="联系作者", command=self.show_contact)
        self.menubar.add_cascade(label="帮助", menu=self.help_menu)

        root.config(menu=self.menubar)

        # ---------------------------- 主界面 ----------------------------
        self.type_label = tk.Label(root, text="当前题型：未选择", font=("Arial", 12), fg="#666")
        self.type_label.pack(pady=5)

        self.question_label = tk.Label(root, text="", font=("Arial", 14), wraplength=500)
        self.question_label.pack(pady=10)

        # 单选题的选项显示
        self.options_frame = tk.Frame(root)
        self.options_frame.pack(pady=10)
        self.option_var = tk.StringVar()

        # 填空题的输入框（默认隐藏）
        self.answer_entry = tk.Entry(root, font=("Arial", 14))
        self.answer_entry.pack(pady=10)
        self.answer_entry.pack_forget()

        # 控制按钮
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)
        self.submit_button = tk.Button(self.control_frame, text="提交答案", command=self.check_answer, width=10)
        self.submit_button.pack(side=tk.LEFT, padx=5)
        self.next_button = tk.Button(self.control_frame, text="下一题", command=self.next_question, width=10)
        self.next_button.pack(side=tk.LEFT, padx=5)

        # 显示答题结果和解析
        self.result_label = tk.Label(root, text="", font=("Arial", 14), fg="red")
        self.result_label.pack(pady=10)
        self.analysis_text = tk.Text(root, height=5, width=50, font=("Arial", 12), state=tk.DISABLED)
        self.analysis_text.pack(pady=10)
        self.analysis_text.pack_forget()

        # 快捷键绑定
        root.bind("<Control-o>", lambda event: self.import_questions())

    # ---------------------------- 核心功能 ----------------------------
    def import_questions(self):
        """通过菜单导入题库"""
        file_path = filedialog.askopenfilename(
            filetypes=[("题库文件", "*.json;*.txt;*.csv")]
        )
        if file_path:
            try:
                if file_path.endswith(".json"):
                    self.questions = self.load_json_questions(file_path)
                elif file_path.endswith(".txt"):
                    self.questions = self.load_txt_questions(file_path)
                elif file_path.endswith(".csv"):
                    self.questions = self.load_csv_questions(file_path)
                else:
                    messagebox.showerror("错误", "不支持的文件格式！")
                    return

                # 按类型分类题目
                self.type_questions = {
                    "choice": [],
                    "fill": [],
                    "short": [],
                    "case": [],
                    "comprehensive": []
                }
                for q in self.questions:
                    if q["type"] in self.type_questions:
                        self.type_questions[q["type"]].append(q)
                self.update_mode()
                messagebox.showinfo("成功", f"已导入 {len(self.questions)} 道题目！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def set_mode(self, mode):
        """通过菜单设置模式"""
        self.current_mode = mode
        self.type_label.config(text=f"当前题型：{self.get_type_name(mode)}")
        self.update_mode()

    def get_type_name(self, type_code):
        """获取题型中文名称"""
        names = {
            "random": "随机模式",
            "choice": "选择题",
            "fill": "填空题",
            "short": "简答题",
            "case": "案例分析",
            "comprehensive": "综合运用"
        }
        return names.get(type_code, "未知题型")

    def update_mode(self):
        """更新题目队列"""
        self.question_queue = []
        if self.current_mode == "random":
            # 按类型顺序生成队列：choice → fill → short → case → comprehensive
            for q_type in ["choice", "fill", "short", "case", "comprehensive"]:
                if self.type_questions.get(q_type):
                    random.shuffle(self.type_questions[q_type])
                    self.question_queue.extend(self.type_questions[q_type])
        else:
            if self.type_questions.get(self.current_mode):
                self.question_queue = self.type_questions[self.current_mode].copy()
                random.shuffle(self.question_queue)
        self.queue_index = 0
        self.next_question()

    def next_question(self):
        """显示下一题"""
        # 清空界面元素
        self.result_label.config(text="")
        self.analysis_text.pack_forget()
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.config(state=tk.DISABLED)
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_var.set(None)
        self.answer_entry.delete(0, tk.END)

        if self.queue_index < len(self.question_queue):
            self.current_question = self.question_queue[self.queue_index]
            self.queue_index += 1
            self.question_label.config(text=self.current_question["question"])
            self.type_label.config(text=f"当前题型：{self.get_type_name(self.current_question['type'])}")

            # 动态显示组件
            if self.current_question["type"] == "choice":
                self.answer_entry.pack_forget()
                options = self.current_question["options"]
                for i, option in enumerate(options):
                    rb = tk.Radiobutton(
                        self.options_frame,
                        text=f"{chr(65 + i)}. {option}",
                        variable=self.option_var,
                        value=chr(65 + i),
                        font=("Arial", 12)
                    )
                    rb.pack(anchor="w", pady=2)
            else:
                self.options_frame.pack_forget()
                self.answer_entry.pack(pady=10)
        else:
            self.question_label.config(text="题目已全部完成！")
            self.type_label.config(text="当前题型：已完成所有题目")

    def check_answer(self):
        """检查答案"""
        if not self.current_question:
            return

        user_answer = ""
        if self.current_question["type"] == "choice":
            user_answer = self.option_var.get()
            if user_answer:
                user_answer = self.current_question["options"][ord(user_answer) - 65]
        else:
            user_answer = self.answer_entry.get().strip()

        correct_answer = self.current_question["answer"].strip()
        analysis = self.current_question.get("analysis", "暂无解析")

        # 显示结果
        if user_answer == correct_answer:
            self.result_label.config(text="✓ 回答正确", fg="green")
        else:
            self.result_label.config(text="✗ 回答错误", fg="red")

        # 显示解析
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, f"【正确答案】\n{correct_answer}\n\n【解析】\n{analysis}")
        self.analysis_text.config(state=tk.DISABLED)
        self.analysis_text.pack(pady=10)

    # ---------------------------- 帮助菜单功能 ----------------------------
    def show_usage(self):
        """显示软件使用方法"""
        usage_text = """
        【软件使用方法】
        1. 导入题库：通过菜单栏“文件 → 导入题库”选择题库文件（支持 JSON/TXT/CSV 格式）。
        2. 选择题型：通过菜单栏“题目类型”选择随机模式或指定题型。
        3. 答题：根据题目类型选择答案或填写答案，点击“提交答案”查看结果。
        4. 下一题：点击“下一题”继续练习。
        """
        messagebox.showinfo("软件使用方法", usage_text)

    def show_contact(self):
        """显示联系作者信息"""
        contact_text = """
        【联系作者】
        如有问题或建议，请联系：
        - 邮箱：xhlei1234@163.com
        - GitHub：https://github.com/xhlei97/questionsDev
        """
        messagebox.showinfo("联系作者", contact_text)

    # ---------------------------- 文件加载 ----------------------------
    def load_json_questions(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_txt_questions(self, file_path):
        questions = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        question = {
                            "type": parts[0].strip(),
                            "question": parts[1].strip(),
                            "answer": parts[2].strip(),
                            "analysis": parts[3].strip()
                        }
                        if question["type"] == "choice" and len(parts) >= 5:
                            question["options"] = parts[4].strip().split(",")
                        questions.append(question)
        return questions

    def load_csv_questions(self, file_path):
        questions = []
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                question = {
                    "type": row["type"],
                    "question": row["question"],
                    "answer": row["answer"],
                    "analysis": row["analysis"]
                }
                if question["type"] == "choice":
                    question["options"] = row["options"].split(",")
                questions.append(question)
        return questions

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionBankApp(root)
    root.mainloop()