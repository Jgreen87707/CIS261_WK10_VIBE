"""Student records manager for test scores and grade calculation."""

from __future__ import annotations

import csv
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

DATA_FILE = "student_grades.txt"


def validate_score(value: float) -> float:
    if value < 0 or value > 100:
        raise ValueError("Score must be between 0 and 100.")
    return value


@dataclass
class StudentRecord:
    name: str
    student_id: str
    test1: float
    test2: float
    test3: float

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        self.student_id = self.student_id.strip()
        if not self.name:
            raise ValueError("Student name cannot be empty.")
        if not self.student_id:
            raise ValueError("Student ID cannot be empty.")
        self.test1 = validate_score(self.test1)
        self.test2 = validate_score(self.test2)
        self.test3 = validate_score(self.test3)

    def average_score(self) -> float:
        return round((self.test1 + self.test2 + self.test3) / 3, 2)

    def letter_grade(self) -> str:
        average = self.average_score()
        if average >= 90:
            return "A"
        if average >= 80:
            return "B"
        if average >= 70:
            return "C"
        if average >= 60:
            return "D"
        return "F"

    def summary(self) -> str:
        return (
            f"Student: {self.name}\n"
            f"ID: {self.student_id}\n"
            f"Test 1: {self.test1:.2f}\n"
            f"Test 2: {self.test2:.2f}\n"
            f"Test 3: {self.test3:.2f}\n"
            f"Average: {self.average_score():.2f}\n"
            f"Grade: {self.letter_grade()}"
        )


class StudentManager:
    def __init__(self) -> None:
        self.records: Dict[str, StudentRecord] = {}
        self.load_records()

    def add_student(
        self,
        name: str,
        student_id: str,
        test1: float,
        test2: float,
        test3: float,
    ) -> StudentRecord:
        key = student_id.strip().lower()
        if key in self.records:
            raise KeyError(f"Student ID '{student_id}' already exists.")
        record = StudentRecord(name=name, student_id=student_id, test1=test1, test2=test2, test3=test3)
        self.records[key] = record
        self.save_records()
        return record

    def get_student(self, student_id: str) -> StudentRecord:
        key = student_id.strip().lower()
        if key not in self.records:
            raise KeyError(f"Student ID '{student_id}' not found.")
        return self.records[key]

    def search_students_by_name(self, name: str) -> List[StudentRecord]:
        query = name.strip().lower()
        return [record for record in self.records.values() if query in record.name.lower()]

    def update_scores(
        self,
        student_id: str,
        test1: float,
        test2: float,
        test3: float,
    ) -> None:
        student = self.get_student(student_id)
        student.test1 = validate_score(test1)
        student.test2 = validate_score(test2)
        student.test3 = validate_score(test3)
        self.save_records()

    def remove_student(self, student_id: str) -> None:
        key = student_id.strip().lower()
        if key not in self.records:
            raise KeyError(f"Student ID '{student_id}' not found.")
        del self.records[key]
        self.save_records()

    def list_students(self) -> List[StudentRecord]:
        return sorted(self.records.values(), key=lambda record: record.name)

    def class_statistics(self) -> Optional[Tuple[float, float, float]]:
        if not self.records:
            return None
        averages = [record.average_score() for record in self.records.values()]
        return min(averages), max(averages), round(sum(averages) / len(averages), 2)

    def save_records(self) -> None:
        fieldnames = ["name", "id", "test1", "test2", "test3", "average", "grade"]
        try:
            with open(DATA_FILE, mode="w", newline="", encoding="utf-8") as fp:
                writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter="|")
                writer.writeheader()
                for student in self.list_students():
                    writer.writerow(
                        {
                            "name": student.name,
                            "id": student.student_id,
                            "test1": f"{student.test1:.2f}",
                            "test2": f"{student.test2:.2f}",
                            "test3": f"{student.test3:.2f}",
                            "average": f"{student.average_score():.2f}",
                            "grade": student.letter_grade(),
                        }
                    )
        except OSError as error:
            raise OSError(f"Unable to save records to '{DATA_FILE}': {error}") from error

    def load_records(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, mode="r", encoding="utf-8", newline="") as fp:
                reader = csv.DictReader(fp, delimiter="|")
                for row in reader:
                    if not row:
                        continue
                    try:
                        student_id = row.get("id", "").strip()
                        if not student_id:
                            continue
                        self.records[student_id.lower()] = StudentRecord(
                            name=row.get("name", ""),
                            student_id=student_id,
                            test1=float(row.get("test1", "0") or 0),
                            test2=float(row.get("test2", "0") or 0),
                            test3=float(row.get("test3", "0") or 0),
                        )
                    except (ValueError, KeyError):
                        continue
        except OSError as error:
            raise OSError(f"Unable to read records from '{DATA_FILE}': {error}") from error


def get_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            return validate_score(float(raw))
        except ValueError:
            print("Please enter a valid number between 0 and 100.")


def get_nonempty_text(prompt: str) -> str:
    while True:
        text = input(prompt).strip()
        if text:
            return text
        print("Value cannot be empty.")


def read_single_key() -> str:
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char
    except (ImportError, OSError):
        return input().strip()


def get_menu_choice() -> str:
    print("Choose an option (1-7) or press ESC to exit:", end=" ", flush=True)
    choice = read_single_key()
    if choice == "\x1b":
        return "ESC"
    print()
    return choice.strip()


def print_student_table(students: List[StudentRecord]) -> None:
    if not students:
        print("No student records available.")
        return
    headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    widths = [20, 12, 8, 8, 8, 8, 6]
    header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
    separator = "-" * len(header_line)
    print(separator)
    print(header_line)
    print(separator)
    for student in students:
        print(
            " | ".join(
                [
                    student.name.ljust(widths[0]),
                    student.student_id.ljust(widths[1]),
                    f"{student.test1:.2f}".rjust(widths[2]),
                    f"{student.test2:.2f}".rjust(widths[3]),
                    f"{student.test3:.2f}".rjust(widths[4]),
                    f"{student.average_score():.2f}".rjust(widths[5]),
                    student.letter_grade().center(widths[6]),
                ]
            )
        )
    print(separator)


def print_menu() -> None:
    print("\n=== Student Records Manager ===")
    print("1. Add new student record")
    print("2. Display all students")
    print("3. Display class statistics")
    print("4. Search student by name")
    print("5. Update student scores")
    print("6. Remove student")
    print("7. Exit")


def input_student_scores() -> Tuple[float, float, float]:
    test1 = get_float("Enter Test 1 score (0-100): ")
    test2 = get_float("Enter Test 2 score (0-100): ")
    test3 = get_float("Enter Test 3 score (0-100): ")
    return test1, test2, test3


def print_class_statistics(manager: StudentManager) -> None:
    stats = manager.class_statistics()
    if stats is None:
        print("No student records available to compute statistics.")
        return
    lowest, highest, class_avg = stats
    print(f"Class highest average: {highest:.2f}")
    print(f"Class lowest average: {lowest:.2f}")
    print(f"Class average: {class_avg:.2f}")


def main() -> None:
    manager = StudentManager()
    print(f"Loaded {len(manager.records)} student record(s) from '{DATA_FILE}'.")

    while True:
        print_menu()
        choice = get_menu_choice()
        if choice == "ESC":
            print("\nGoodbye!")
            break

        try:
            if choice == "1":
                name = get_nonempty_text("Enter student name: ")
                student_id = get_nonempty_text("Enter student ID: ")
                test1, test2, test3 = input_student_scores()
                manager.add_student(name, student_id, test1, test2, test3)
                print(f"Added student '{name.title()}' with ID '{student_id}'.")
            elif choice == "2":
                print_student_table(manager.list_students())
            elif choice == "3":
                print_class_statistics(manager)
            elif choice == "4":
                name = get_nonempty_text("Enter student name to search: ")
                matches = manager.search_students_by_name(name)
                if not matches:
                    print(f"No students matched '{name}'.")
                else:
                    print_student_table(matches)
            elif choice == "5":
                student_id = get_nonempty_text("Enter student ID to update: ")
                test1, test2, test3 = input_student_scores()
                manager.update_scores(student_id, test1, test2, test3)
                print(f"Updated scores for student ID '{student_id}'.")
            elif choice == "6":
                student_id = get_nonempty_text("Enter student ID to remove: ")
                manager.remove_student(student_id)
                print(f"Removed student with ID '{student_id}'.")
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Please choose a number between 1 and 7 or press ESC to exit.")
        except KeyError as error:
            print(error)
        except ValueError as error:
            print(error)


if __name__ == "__main__":
    main()
