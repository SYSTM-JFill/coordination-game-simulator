import random
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.widgets import Button, TextBox
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import filedialog

# ==== CONFIG ====

strategies = ["Early", "Wait"]
strategy_to_idx = {"Early": 0, "Wait": 1}
xticks = ["Early", "Wait"]
yticks = ["Early", "Wait"]

alpha_strategy_weights = {"Early": 0.7, "Wait": 0.3}
beta_strategy_weights = {"Early": 0.4, "Wait": 0.6}

payoff_matrix = {
    ("Early", "Early"): (3, 3),
    ("Early", "Wait"): (5, 1),
    ("Wait", "Early"): (1, 5),
    ("Wait", "Wait"): (4, 4)
}

NUM_GAMES = 1000
SEED = 22
random.seed(SEED)

# ==== DATA STRUCTURES ====

results = {"Alpha wins": 0, "Beta wins": 0, "Draw": 0}
outcome_matrix = {(a, b): 0 for a in strategies for b in strategies}

win_rate_history = {
    "Alpha wins": [],
    "Beta wins": [],
    "Draw": []
}

# ==== DASHBOARD SETUP ====

fig = plt.figure(figsize=(11, 10))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 0.6], hspace=0.4, bottom=0.3, left=0.1, right=0.85)

bar_ax = fig.add_subplot(gs[0, 0])
heat_ax_all = fig.add_subplot(gs[0, 1])
winrate_ax = fig.add_subplot(gs[1, :])

# Bar Chart of Wins
bars = bar_ax.bar(results.keys(), results.values(), color=["blue", "red", "gray"])
bar_ax.set_ylim(0, NUM_GAMES)
bar_ax.set_title("Win Counts")
bar_ax.set_ylabel("Games Won")

# Heatmap: All Outcomes
data = np.zeros((2, 2), dtype=int)
sns_ax = sns.heatmap(
    data,
    annot=True,
    fmt="d",
    cmap="Blues",
    cbar=False,
    vmin=0,
    vmax=NUM_GAMES // 2,
    xticklabels=xticks,
    yticklabels=yticks,
    ax=heat_ax_all,
    square=True
)
heat_ax_all.set_title("All Strategy Outcomes (with % and winner)")
annot_texts = sns_ax.texts

# Rolling Win-Rate Plot
winrate_ax.set_title("Rolling Win Rate (%) Over Time")
winrate_ax.set_xlim(0, NUM_GAMES)
winrate_ax.set_ylim(0, 100)
winrate_ax.set_xlabel("Games Simulated")
winrate_ax.set_ylabel("Win Rate (%)")
line_alpha, = winrate_ax.plot([], [], color='blue', label='Alpha wins')
line_beta, = winrate_ax.plot([], [], color='red', label='Beta wins')
line_draw, = winrate_ax.plot([], [], color='gray', label='Draws')
winrate_ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), frameon=False)

# ==== SIM CONTROL STATE ====
is_running = [False]

# ==== FUNCTIONS ====

def reset_data():
    for k in results:
        results[k] = 0
    for key in outcome_matrix:
        outcome_matrix[key] = 0
    for bar in bars:
        bar.set_height(0)
    for i, text in enumerate(annot_texts):
        text.set_text("0")
    for key in win_rate_history:
        win_rate_history[key].clear()
    line_alpha.set_data([], [])
    line_beta.set_data([], [])
    line_draw.set_data([], [])
    fig.canvas.draw_idle()

def toggle_sim(event):
    is_running[0] = not is_running[0]

def reset_sim(event):
    is_running[0] = False
    reset_data()

def update_seed(text):
    global SEED
    try:
        SEED = int(text.strip())
        random.seed(SEED)
        reset_sim(None)
    except ValueError:
        print("Invalid seed input.")

def save_figure(event):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Files", "*.png")],
        title="Save simulation plot"
    )
    if file_path:
        fig.savefig(file_path, dpi=300)
        print(f"Plot saved to: {file_path}")

# ==== BUTTONS ====

ax_play = plt.axes([0.05, 0.15, 0.12, 0.05])
ax_reset = plt.axes([0.2, 0.15, 0.12, 0.05])
ax_seed = plt.axes([0.35, 0.15, 0.12, 0.05])
ax_seedbox = plt.axes([0.49, 0.15, 0.1, 0.05])
ax_save = plt.axes([0.61, 0.15, 0.15, 0.05])

btn_play = Button(ax_play, "\u25B6 Play/Pause")
btn_reset = Button(ax_reset, "\u27F2 Reset")
btn_seed_label = Button(ax_seed, "Set Seed")
seed_box = TextBox(ax_seedbox, "", initial=str(SEED))
btn_save = Button(ax_save, "\U0001F4BE Save Plot")

btn_play.on_clicked(toggle_sim)
btn_reset.on_clicked(reset_sim)
btn_seed_label.on_clicked(lambda _: update_seed(seed_box.text))
seed_box.on_submit(update_seed)
btn_save.on_clicked(save_figure)

# ==== ANIMATION LOOP ====

def update(frame):
    if not is_running[0]:
        return

    total_games = sum(results.values())
    if total_games >= NUM_GAMES:
        is_running[0] = False
        print("\n=== Simulation Summary ===")
        print(f"Total Games: {total_games}")
        for outcome in results:
            pct = results[outcome] / total_games * 100
            print(f"{outcome}: {results[outcome]} games ({pct:.1f}%)")
        most_common = max(outcome_matrix.items(), key=lambda x: x[1])
        print(f"Most common strategy pair: {most_common[0]} -> {most_common[1]} times\n")
        return

    alpha = random.choices(strategies, weights=[alpha_strategy_weights[s] for s in strategies])[0]
    beta = random.choices(strategies, weights=[beta_strategy_weights[s] for s in strategies])[0]
    alpha_score, beta_score = payoff_matrix[(alpha, beta)]
    outcome = (alpha, beta)
    outcome_matrix[outcome] += 1

    if alpha_score > beta_score:
        results["Alpha wins"] += 1
    elif beta_score > alpha_score:
        results["Beta wins"] += 1
    else:
        results["Draw"] += 1

    for bar, key in zip(bars, results):
        bar.set_height(results[key])

    data = np.zeros((2, 2), dtype=int)
    total = sum(outcome_matrix.values())
    for (a, b), count in outcome_matrix.items():
        i, j = strategy_to_idx[a], strategy_to_idx[b]
        data[i, j] = count
    sns_ax.collections[0].set_array(data.ravel())

    for i, text in enumerate(annot_texts):
        row, col = divmod(i, 2)
        val = data[row][col]
        a_strat, b_strat = (yticks[row], xticks[col])
        a_score, b_score = payoff_matrix[(a_strat, b_strat)]
        winner = "A" if a_score > b_score else "B" if b_score > a_score else "Draw"
        if total > 0 and val > 0:
            percent = (val / total) * 100
            label = f"{val}\n({percent:.0f}%)\n[{winner}]"
        else:
            label = "0"
        text.set_text(label)

    if total_games > 0:
        win_rate_history["Alpha wins"].append(results["Alpha wins"] / total_games * 100)
        win_rate_history["Beta wins"].append(results["Beta wins"] / total_games * 100)
        win_rate_history["Draw"].append(results["Draw"] / total_games * 100)

        x = list(range(1, total_games + 1))
        line_alpha.set_data(x, win_rate_history["Alpha wins"])
        line_beta.set_data(x, win_rate_history["Beta wins"])
        line_draw.set_data(x, win_rate_history["Draw"])

    fig.canvas.draw_idle()

ani = FuncAnimation(fig, update, interval=50)
plt.show()
