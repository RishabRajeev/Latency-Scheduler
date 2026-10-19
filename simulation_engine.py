import simpy
import random
import yaml
import json
from entities import Task
from orchestrator import LatencyAwareScheduler

def load_config():
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

def monitor_system(env, scheduler, tracking_data):
    while True:
        tracking_data['time'].append(env.now)
        
        # Track CPU Utilization
        if scheduler.policy == "proposed":
            active = sum(n.count for n in scheduler.fog_nodes)
            capacity = sum(n.capacity for n in scheduler.fog_nodes)
            cpu_util = (active / capacity) * 100
        else:
            cpu_util = 0
        tracking_data['cpu_utilization'].append(cpu_util)
        
        # Track Network Bandwidth (Mbps equivalent)
        bw_usage = scheduler.cloud.count * 4.5 
        tracking_data['bandwidth'].append(bw_usage)
        
        yield env.timeout(10)

def generate_tasks(env, scheduler, config):
    random.seed(config['simulation']['seed'])
    task_id = 1
    
    while True:
        # Varying Workloads Injection
        if config['workload']['burst_start'] <= env.now <= config['workload']['burst_end']:
            gap = config['workload']['burst_gap']
        else:
            gap = random.randint(config['workload']['normal_gap_min'], config['workload']['normal_gap_max'])
        
        yield env.timeout(gap)
        
        if random.random() < config['workload']['critical_ratio']:
            priority = "Immediate"
            deadline = config['workload']['critical_deadline_ms']
        else:
            priority = "Intensive"
            deadline = config['workload']['batch_deadline_ms']
            
        task = Task(f"T{task_id}", priority, deadline, env.now)
        env.process(scheduler.process_task(task))
        task_id += 1

def run_sim(policy, config):
    env = simpy.Environment()
    scheduler = LatencyAwareScheduler(env, config, policy)
    tracker = {'time': [], 'cpu_utilization': [], 'bandwidth': []}
    
    env.process(generate_tasks(env, scheduler, config))
    env.process(monitor_system(env, scheduler, tracker))
    env.run(until=config['simulation']['duration_ms'])
    
    success_rate = (scheduler.deadlines_met / scheduler.completed_tasks) * 100 if scheduler.completed_tasks > 0 else 0
    imm_lat = scheduler.latencies["Immediate"]
    
    return {
        "success_rate": success_rate,
        "energy": scheduler.energy_consumed,
        "immediate_latencies": imm_lat,
        "time_series": tracker
    }

if __name__ == "__main__":
    config = load_config()
    print("Running Conventional Scheduling (Cloud-Only)...")
    res_cloud = run_sim("cloud_only", config)
    print("Running Proposed Load-Balancing Framework (Fog)...")
    res_fog = run_sim("proposed", config)
    
    with open('results.json', 'w') as f:
        json.dump({"cloud_only": res_cloud, "proposed": res_fog}, f, indent=4)
    print("Data exported to results.json")