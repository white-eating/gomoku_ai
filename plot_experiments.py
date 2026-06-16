import matplotlib.pyplot as plt

# 数据
experiments = [
    ("MCTS(500) vs Minimax(depth=3)", 0, 50),
    ("Minimax(depth=3) vs Minimax(depth=4)", 100, 0),
    ("MCTS(300) vs MCTS(300)", 11, 9)
]

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, (title, win1, win2) in zip(axes, experiments):
    labels = ['Player 1', 'Player 2']
    wins = [win1, win2]
    bars = ax.bar(labels, wins, color=['#1f77b4', '#ff7f0e'])
    ax.set_title(title, fontsize=10)
    ax.set_ylabel('Wins')
    for bar, w in zip(bars, wins):
        ax.text(bar.get_x() + bar.get_width()/2, w + 0.5, str(w), ha='center', va='bottom')
    ax.set_ylim(0, max(win1, win2) + 5)

plt.tight_layout()
plt.savefig('experiment_wins.png', dpi=150)
plt.show()