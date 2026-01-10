import csv
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not found. Visualization disabled.")

def plot_intent_history(logfile="logs/intent_history.csv"):
    if not MATPLOTLIB_AVAILABLE:
        print("Cannot plot: matplotlib module is missing.")
        return

    path = Path(logfile)
    if not path.exists():
        print(f"Log file not found: {logfile}")
        return

    times, atk, dfs, ctrl, tmp, rsk = [], [], [], [], [], []
    with open(logfile, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or row[0] == "Timestamp": continue # Skip header or empty
            if len(row) < 6: continue
            times.append(row[0])
            atk.append(float(row[1]))
            dfs.append(float(row[2]))
            ctrl.append(float(row[3]))
            tmp.append(float(row[4]))
            rsk.append(float(row[5]))
    
    plt.figure(figsize=(8,4))
    plt.plot(atk, label="Attack")
    plt.plot(dfs, label="Defense")
    plt.plot(ctrl, label="Control")
    plt.plot(tmp, label="Tempo")
    plt.plot(rsk, label="Risk")
    plt.legend()
    plt.title("Intent Parameter Evolution")
    plt.xlabel("Game Index")
    plt.ylabel("Intent Value")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_intent_history()
