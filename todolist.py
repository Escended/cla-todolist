from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

# initialising the parent class for a table
Base = declarative_base()


# a task table
class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    task = Column(String)
    deadline = Column(Date, default=datetime.today())

    def __repr__(self):

        return f"{self.task}"


class ToDoList:
    prompt = "1) Today's tasks\n2) Week's tasks\n3) All tasks\n4) Missed Tasks\n5) Add task\n6) Delete Task\n0) Exit\n"

    def __init__(self, db_name):
        self.engine = create_engine(f"sqlite:///{db_name}.db?check_same_thread=False")
        Base.metadata.create_all(self.engine)

        # Session and interaction with database initialising
        self.session = sessionmaker(bind=self.engine)()

        self.choices = {'1': self.show_today_tasks, '2': self.show_weeks_tasks, '3': self.show_all_tasks,
                        '4': self.missed_tasks, '5': self.add_task, '6': self.delete_task, '0': self.shutdown}
        self.running = True
        self.main()

    def shutdown(self):
        self.running = False

    def show_today_tasks(self, day=datetime.today()):
        """
        collect all the tasks that are happening today
        """
        print(f"Today {day.day} {day.strftime('%b')}:")
        today_tasks = self.session.query(Task).filter(Task.deadline == day.date()).all()

        if today_tasks:
            for idx, task in enumerate(today_tasks):
                print(f"{idx + 1}. {task.task}")
        else:
            print("Nothing to do!")

    def show_weeks_tasks(self):
        """
        Find all the tasks in the following 7 days
        """
        today = datetime.today()
        for i in range(0, 7):
            current_day = today + timedelta(days=i)

            print(f"{current_day.strftime('%A')} {current_day.day} {current_day.strftime('%b')}:")
            today_tasks = self.session.query(Task).filter(Task.deadline == current_day.date()).all()

            if today_tasks:
                for idx, task in enumerate(today_tasks):
                    print(f"{idx + 1}. {task.task}")
            else:
                print("Nothing to do!")
            print()

    def show_all_tasks(self):
        """
        acquires all the rows in the database
        """
        all_tasks = {}
        tasks = self.session.query(Task).order_by(Task.deadline).all()

        if tasks:
            for idx, task in enumerate(tasks, 1):
                print(f"{idx}. {task.task}. {task.deadline.day} {task.deadline.strftime('%b')}")
                all_tasks[idx] = task
        else:
            print("Nothing to do!")

        return all_tasks

    def missed_tasks(self):
        """
        find all rows that date before today
        """
        missed_tasks = self.session.query(Task).order_by(Task.deadline).filter(Task.deadline <
                                                                               datetime.today().date()).all()
        if missed_tasks:
            for idx, task in enumerate(missed_tasks, 1):
                print(f"{idx}. {task.task} {task.deadline.day} {task.deadline.strftime('%b')}")
        else:
            print("Nothing is missed!")

    def add_task(self):
        """
        adds a task to the database
        """
        task = input('Enter task\n')
        deadline = input('Enter deadline\n')
        d = datetime.strptime(deadline, '%Y-%m-%d')
        self.session.add(Task(task=task, deadline=datetime.date(d)))
        self.session.commit()
        print("The task has been added!")

    def delete_task(self):
        """
        Delete rows by storing each row as an object in a dictionary
        to map it correctly with the numbers displayed which may differ
        from the order in the database.
        """
        print("Choose the number of the task you want to delete:")
        task_dict = self.show_all_tasks()
        try:
            row = task_dict[int(input())]
            self.session.delete(row)
            print("The task has been deleted!")
            self.session.commit()
        except KeyError:
            print("Key out of bounds")

    def main(self):
        """
        continuously runs the program

        the two print statements, are for line breaks, to maintain proper format of CMD Gui
        lambda: None defines a function that does nothing, as such, if wrong input was entered,
        it would simply go to the next iteration of the while loop
        if choice != '0' represents the exit input, then the linebreak is replaced by a "Bye!"
        """
        while self.running:
            choice = input(self.prompt)
            print()
            self.choices.get(choice, lambda: None)()
            print() if choice != '0' else print('Bye!')


ToDoList('todo')
