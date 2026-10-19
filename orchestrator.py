import simpy
import random

class LoadBalancer:
    def __init__(self, fog_nodes):
        self.fog_nodes = fog_nodes

    def get_optimal_node(self):
        # Load Balancing Strategy: Evaluate CPU utilization
        best_node = min(self.fog_nodes, key=lambda n: n.count)
        if best_node.count < best_node.capacity:
            return best_node
        return None # Fog layer saturated

class LatencyAwareScheduler:
    def __init__(self, env, config, policy):
        self.env = env
        self.config = config
        self.policy = policy
        
        self.fog_nodes = [simpy.Resource(env, capacity=config['topology']['fog_cpu_capacity']) 
                          for _ in range(config['topology']['num_fog_nodes'])]
        self.cloud = simpy.Resource(env, capacity=config['topology']['cloud_cpu_capacity'])
        self.load_balancer = LoadBalancer(self.fog_nodes)
        
        # Scheduling Parameters Tracker
        self.completed_tasks = 0
        self.deadlines_met = 0
        self.latencies = {"Immediate": [], "Intensive": []}
        self.energy_consumed = 0

    def process_task(self, task):
        # Simulate network jitter for realistic variance
        fog_time = random.uniform(self.config['processing_times']['fog_base_ms'] - 1, 
                                  self.config['processing_times']['fog_base_ms'] + 1)
        cloud_time = random.uniform(self.config['processing_times']['cloud_base_ms'] - 4, 
                                    self.config['processing_times']['cloud_base_ms'] + 4)

        if self.policy == "cloud_only":
            # Conventional Baseline
            resource = self.cloud
            proc_time = cloud_time
            self.energy_consumed += 8.0 # High transmission energy
            
        elif self.policy == "proposed":
            # Proposed Framework
            if task.priority == "Immediate":
                target_node = self.load_balancer.get_optimal_node()
                if target_node:
                    resource = target_node
                    proc_time = fog_time
                    self.energy_consumed += 2.5 # Efficient local energy
                else:
                    resource = self.cloud
                    proc_time = cloud_time
                    self.energy_consumed += 8.0
            else:
                # Compute Intensive -> Cloud
                resource = self.cloud
                proc_time = cloud_time
                self.energy_consumed += 8.0

        with resource.request() as req:
            yield req
            yield self.env.timeout(proc_time)
            
            task.completion_time = self.env.now
            task.latency = task.completion_time - task.arrival_time
            
            self.completed_tasks += 1
            self.latencies[task.priority].append(task.latency)
            if task.latency <= task.deadline:
                self.deadlines_met += 1