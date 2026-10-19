import json
import matplotlib.pyplot as plt

def generate_dashboard():
    with open('results.json', 'r') as f:
        res = json.load(f)

    labels = ['Conventional (Cloud)', 'Proposed (Fog)']
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Q2: Latency-Aware Task Scheduling & Load Balancing Evaluation', fontsize=16, fontweight='bold')

    # 1. Deadline Success
    sr = [res['cloud_only']['success_rate'], res['proposed']['success_rate']]
    axs[0, 0].bar(labels, sr, color=['#e63946', '#2a9d8f'])
    axs[0, 0].set_title('Time-Sensitive Task Deadline Success', fontsize=12)
    axs[0, 0].set_ylabel('Success Rate (%)')
    axs[0, 0].set_ylim(0, 110)
    for i, v in enumerate(sr):
        axs[0, 0].text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')

    # 2. Energy Consumption
    nrg = [res['cloud_only']['energy'], res['proposed']['energy']]
    axs[0, 1].bar(labels, nrg, color=['#f4a261', '#e9c46a'])
    axs[0, 1].set_title('Total Energy Consumption', fontsize=12)
    axs[0, 1].set_ylabel('Energy (Joules)')
    for i, v in enumerate(nrg):
        axs[0, 1].text(i, v + 10, f'{v:.1f}', ha='center', fontweight='bold')

    # 3. Latency Distribution
    lat_c = res['cloud_only']['immediate_latencies']
    lat_f = res['proposed']['immediate_latencies']
    axs[1, 0].boxplot([lat_c, lat_f], patch_artist=True, boxprops=dict(facecolor='#a8dadc'))
    axs[1, 0].set_xticks([1, 2], labels)
    axs[1, 0].set_title('Latency Distribution (Immediate Tasks)', fontsize=12)
    axs[1, 0].set_ylabel('Latency (ms)')
    axs[1, 0].grid(axis='y', linestyle='--', alpha=0.6)

    # 4. CPU & Bandwidth (Varying Workloads)
    t = res['proposed']['time_series']['time']
    cpu = res['proposed']['time_series']['cpu_utilization']
    bw = res['cloud_only']['time_series']['bandwidth']
    
    axs[1, 1].plot(t, cpu, label='Fog CPU Utilization (%)', color='#2a9d8f', lw=2)
    axs[1, 1].plot(t, bw, label='Cloud Network Bandwidth (Mbps)', color='#e63946', ls='--')
    axs[1, 1].axvspan(150, 350, color='gray', alpha=0.15, label='Varying Workload (Traffic Burst)')
    axs[1, 1].set_title('System Parameters Over Time', fontsize=12)
    axs[1, 1].set_xlabel('Time (ms)')
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('q2_evaluation_dashboard.png', dpi=300)
    print("Dashboard saved as 'q2_evaluation_dashboard.png'")

if __name__ == "__main__":
    generate_dashboard()