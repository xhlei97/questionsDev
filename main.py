import tkinter as tk
from tkinter import filedialog
import json
import random
import csv

class QuestionBankApp:
    def __init__(self, root):
        self.root = root
        self.root.title("屹筠题库")
        self.questions = []  # 存储所有题目
        self.current_question = None  # 当前显示的题目

        # 界面布局
        self.label = tk.Label(root, text="屹筠题库", font=("Arial", 16))
        self.label.pack(pady=10)

        self.question_label = tk.Label(root, text="", font=("Arial", 14), wraplength=500)
        self.question_label.pack(pady=10)

        self.answer_entry = tk.Entry(root, font=("Arial", 14))
        self.answer_entry.pack(pady=10)

        self.submit_button = tk.Button(root, text="提交答案", command=self.check_answer)
        self.submit_button.pack(pady=10)

        self.next_button = tk.Button(root, text="下一题", command=self.next_question)
        self.next_button.pack(pady=10)

        self.import_button = tk.Button(root, text="导入题库", command=self.import_questions)
        self.import_button.pack(pady=10)

        # 新增：显示答题结果的标签
        self.result_label = tk.Label(root, text="", font=("Arial", 14), fg="red")
        self.result_label.pack(pady=10)

        # 新增：显示正确答案和解析的文本框
        self.analysis_text = tk.Text(root, height=5, width=50, font=("Arial", 12), state=tk.DISABLED)
        self.analysis_text.pack(pady=10)

        # 初始化
        self.next_question()

    def import_questions(self):
        """导入题库（支持 JSON/TXT/CSV）"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON 文件", "*.json"), ("文本文件", "*.txt"), ("CSV 文件", "*.csv")]
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
                    self.result_label.config(text="不支持的文件格式！", fg="red")
                    return

                self.result_label.config(text=f"已导入 {len(self.questions)} 道题目！", fg="green")
                self.next_question()
            except Exception as e:
                self.result_label.config(text=f"导入失败: {e}", fg="red")

    def load_json_questions(self, file_path):
        """加载 JSON 题库"""
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def load_txt_questions(self, file_path):
        """加载 TXT 题库"""
        questions = []
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split("|")
                    if len(parts) >= 3:  # 题目|答案|解析
                        questions.append({
                            "question": parts[0].strip(),
                            "answer": parts[1].strip(),
                            "analysis": parts[2].strip()
                        })
        return questions

    def load_csv_questions(self, file_path):
        """加载 CSV 题库"""
        questions = []
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                questions.append({
                    "question": row["question"],
                    "answer": row["answer"],
                    "analysis": row["analysis"]
                })
        return questions

    def next_question(self):
        """随机显示下一题"""
        # 清空结果和解析
        self.result_label.config(text="")
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.config(state=tk.DISABLED)

        if self.questions:
            self.current_question = random.choice(self.questions)
            self.question_label.config(text=self.current_question["question"])
            self.answer_entry.delete(0, tk.END)
        else:
            self.question_label.config(text="题库为空，请先导入题目！")

    def check_answer(self):
        """检查答案并显示结果和解析"""
        if not self.current_question:
            return

        user_answer = self.answer_entry.get().strip()
        correct_answer = self.current_question["answer"].strip()
        analysis = self.current_question.get("analysis", "暂无解析")

        # 显示答题结果
        if user_answer == correct_answer:
            self.result_label.config(text="回答正确！", fg="green")
        else:
            self.result_label.config(text="回答错误！", fg="red")

        # 显示正确答案和解析
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert(tk.END, f"正确答案：{correct_answer}\n解析：{analysis}")
        self.analysis_text.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuestionBankApp(root)
    root.mainloop()