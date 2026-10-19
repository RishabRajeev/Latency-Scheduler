class Task:
    def __init__(self, task_id, priority, deadline, arrival_time):
        self.task_id = task_id
        self.priority = priority # "Immediate" or "Intensive"
        self.deadline = deadline
        self.arrival_time = arrival_time
        
        self.completion_time = None
        self.latency = None