"""
Student Performance Analyzer
Uses: pandas (data storage / CSV I/O) + matplotlib (visualizations)
Assignment-1 — All 5 tasks + bonus
"""

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend (safe for all platforms)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

CSV_FILE   = "students.csv"
CHART_DIR  = "charts"
os.makedirs(CHART_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Task 4 — OOP: Student Class
# ─────────────────────────────────────────────────────────────

class Student:
    def __init__(self, id, name, midterm, final, assignment):
        self.id         = int(id)
        self.name       = str(name).strip()
        self.midterm    = float(midterm)
        self.final      = float(final)
        self.assignment = float(assignment)
        self.final_score = self.compute_final()
        self.grade       = self.compute_grade()

    def compute_final(self) -> float:
        return round(0.4 * self.midterm + 0.5 * self.final + 0.1 * self.assignment, 2)

    def compute_grade(self) -> str:
        s = self.final_score
        if   s >= 85: return "A"
        elif s >= 70: return "B"
        elif s >= 55: return "C"
        elif s >= 40: return "D"
        else:         return "F"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "name": self.name,
            "midterm": self.midterm, "final": self.final,
            "assignment": self.assignment,
            "final_score": self.final_score, "grade": self.grade
        }


# ─────────────────────────────────────────────────────────────
# Pandas DataFrame as the in-memory store
# ─────────────────────────────────────────────────────────────

COLUMNS = ["id", "name", "midterm", "final", "assignment", "final_score", "grade"]

df: pd.DataFrame = pd.DataFrame(columns=COLUMNS)


def _rebuild_derived():
    """Recalculate final_score and grade columns from raw scores."""
    global df
    if df.empty:
        return
    df["final_score"] = (0.4 * df["midterm"] +
                         0.5 * df["final"]   +
                         0.1 * df["assignment"]).round(2)
    df["grade"] = df["final_score"].apply(assign_letter_grade)


# ─────────────────────────────────────────────────────────────
# Task 3 — File Handling  (pandas read_csv / to_csv)
# ─────────────────────────────────────────────────────────────

def load_students():
    global df
    try:
        df = pd.read_csv(CSV_FILE)
        # Ensure correct dtypes
        df["id"]          = df["id"].astype(int)
        df["midterm"]     = df["midterm"].astype(float)
        df["final"]       = df["final"].astype(float)
        df["assignment"]  = df["assignment"].astype(float)
        _rebuild_derived()
        print(f"  ✔  Loaded {len(df)} record(s) from '{CSV_FILE}'.")
    except FileNotFoundError:
        df = pd.DataFrame(columns=COLUMNS)
        print(f"  ℹ  '{CSV_FILE}' not found — starting fresh.")
    except Exception as e:
        df = pd.DataFrame(columns=COLUMNS)
        print(f"  ✖  Error loading file: {e}")


def save_students():
    try:
        df.to_csv(CSV_FILE, index=False)
        print(f"  ✔  Saved {len(df)} record(s) to '{CSV_FILE}'.")
    except Exception as e:
        print(f"  ✖  Error saving: {e}")


# ─────────────────────────────────────────────────────────────
# Task 2 — Core Functions
# ─────────────────────────────────────────────────────────────

def _next_id() -> int:
    return int(df["id"].max()) + 1 if not df.empty else 101


def _get_float(prompt: str, lo=0.0, hi=100.0) -> float:
    while True:
        try:
            val = float(input(prompt))
            if lo <= val <= hi:
                return val
            print(f"    Enter a value between {lo} and {hi}.")
        except ValueError:
            print("    Invalid — enter a number.")


def calculate_final_score(midterm, final, assignment) -> float:
    return round(0.4 * midterm + 0.5 * final + 0.1 * assignment, 2)


def assign_letter_grade(score: float) -> str:
    if   score >= 85: return "A"
    elif score >= 70: return "B"
    elif score >= 55: return "C"
    elif score >= 40: return "D"
    else:             return "F"


def add_student():
    global df
    print("\n  ── Add Student ──")
    name = input("  Name: ").strip()
    if not name:
        print("  Name cannot be empty."); return
    mid  = _get_float("  Midterm score    (0-100): ")
    fin  = _get_float("  Final exam score (0-100): ")
    asgn = _get_float("  Assignment score (0-100): ")

    s   = Student(_next_id(), name, mid, fin, asgn)
    new_row = pd.DataFrame([s.to_dict()])
    df  = pd.concat([df, new_row], ignore_index=True)
    print(f"  ✔  Added → ID {s.id}  {s.name}  Score: {s.final_score}  Grade: {s.grade}")


def remove_student():
    global df
    print("\n  ── Remove Student ──")
    try:
        sid = int(input("  Enter student ID to remove: "))
    except ValueError:
        print("  Invalid ID."); return

    mask = df["id"] == sid
    if mask.any():
        name = df.loc[mask, "name"].values[0]
        df   = df[~mask].reset_index(drop=True)
        print(f"  ✔  Removed: {name} (ID {sid})")
    else:
        print(f"  ✖  No student with ID {sid}.")


def search_student():
    print("\n  ── Search Student ──")
    query = input("  Enter ID or name (partial OK): ").strip()
    if not query:
        return
    if query.isdigit():
        result = df[df["id"] == int(query)]
    else:
        result = df[df["name"].str.contains(query, case=False, na=False)]

    if result.empty:
        print("  No matching student found.")
    else:
        print(f"\n  Found {len(result)} result(s):")
        print(result.to_string(index=False))


def update_student():
    global df
    print("\n  ── Update Student ──")
    try:
        sid = int(input("  Enter student ID to update: "))
    except ValueError:
        print("  Invalid ID."); return

    idx = df.index[df["id"] == sid]
    if idx.empty:
        print(f"  ✖  No student with ID {sid}."); return

    i = idx[0]
    print(f"  Current: {df.loc[i].to_dict()}")
    print("  (Press ENTER to keep current value)")

    def maybe(prompt, current):
        raw = input(f"  {prompt} [{current}]: ").strip()
        if not raw:
            return current
        try:
            val = float(raw)
            return val if 0 <= val <= 100 else current
        except ValueError:
            return current

    df.at[i, "midterm"]    = maybe("Midterm",    df.at[i, "midterm"])
    df.at[i, "final"]      = maybe("Final exam", df.at[i, "final"])
    df.at[i, "assignment"] = maybe("Assignment", df.at[i, "assignment"])
    _rebuild_derived()
    print(f"  ✔  Updated → {df.loc[i].to_dict()}")


def show_all_students():
    print("\n  ── All Students ──")
    if df.empty:
        print("  No records found."); return
    display = df[COLUMNS].copy()
    display.index = range(1, len(display) + 1)
    print(display.to_string())
    print(f"\n  Total: {len(df)} student(s)")


# ─────────────────────────────────────────────────────────────
# Task 5 — Reporting & Statistics  (pandas describe / groupby)
# ─────────────────────────────────────────────────────────────

def generate_report():
    print("\n" + "═" * 62)
    print("            STUDENT PERFORMANCE REPORT")
    print("═" * 62)

    if df.empty:
        print("  No data available."); return

    scores = df["final_score"]

    print(f"\n  Total Students   : {len(df)}")
    print(f"  Average Score    : {scores.mean():.2f}")
    print(f"  Highest Score    : {scores.max():.2f}  "
          f"({df.loc[scores.idxmax(), 'name']})")
    print(f"  Lowest Score     : {scores.min():.2f}  "
          f"({df.loc[scores.idxmin(), 'name']})")
    print(f"  Std Deviation    : {scores.std():.2f}")
    print(f"  Median Score     : {scores.median():.2f}")

    print("\n  ── Pandas describe() ──")
    print(df[["midterm", "final", "assignment", "final_score"]].describe().round(2).to_string())

    print("\n  ── Grade Distribution ──")
    dist = df.groupby("grade")["name"].count().reindex(
            ["A","B","C","D","F"], fill_value=0)
    dist_df = dist.reset_index()
    dist_df.columns = ["Grade", "Count"]
    dist_df["Percentage"] = (dist_df["Count"] / len(df) * 100).round(1).astype(str) + "%"
    print(dist_df.to_string(index=False))

    print("\n  ── Rankings (sorted by final_score DESC) ──")
    ranked = df[["id","name","final_score","grade"]].sort_values(
                "final_score", ascending=False).reset_index(drop=True)
    ranked.index += 1
    ranked.index.name = "Rank"
    print(ranked.to_string())
    print("═" * 62)


# ─────────────────────────────────────────────────────────────
# Bonus — Matplotlib Visualizations
# ─────────────────────────────────────────────────────────────

GRADE_COLORS = {"A": "#2ecc71", "B": "#3498db",
                "C": "#f39c12", "D": "#e67e22", "F": "#e74c3c"}

def _save(fig, name):
    path = os.path.join(CHART_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    print(f"  ✔  Saved → {path}")


def grade_visualization():
    if df.empty:
        print("  No data to visualize."); return

    dist = df["grade"].value_counts().reindex(["A","B","C","D","F"], fill_value=0)
    colors = [GRADE_COLORS[g] for g in dist.index]

    # ── 1. Grade Distribution Bar Chart ──────────────────────
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(dist.index, dist.values, color=colors, edgecolor="white", width=0.55)
    for bar, val in zip(bars, dist.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(val), ha="center", va="bottom", fontweight="bold", fontsize=11)
    ax.set_title("Grade Distribution", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Letter Grade"); ax.set_ylabel("Number of Students")
    ax.set_ylim(0, dist.max() + 2)
    ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    _save(fig, "1_grade_bar.png")

    # ── 2. Grade Pie Chart ────────────────────────────────────
    non_zero = dist[dist > 0]
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts, autotexts = ax.pie(
        non_zero.values,
        labels=non_zero.index,
        autopct="%1.1f%%",
        colors=[GRADE_COLORS[g] for g in non_zero.index],
        startangle=140,
        wedgeprops=dict(edgecolor="white", linewidth=2)
    )
    for t in autotexts:
        t.set_fontsize(11); t.set_fontweight("bold")
    ax.set_title("Grade Distribution (Pie)", fontsize=14, fontweight="bold")
    _save(fig, "2_grade_pie.png")

    # ── 3. Final Score Histogram ──────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    n, bins, patches = ax.hist(df["final_score"], bins=10, range=(0,100),
                               edgecolor="white", linewidth=1.2)
    for patch, left in zip(patches, bins[:-1]):
        mid = left + 5
        if   mid >= 85: patch.set_facecolor(GRADE_COLORS["A"])
        elif mid >= 70: patch.set_facecolor(GRADE_COLORS["B"])
        elif mid >= 55: patch.set_facecolor(GRADE_COLORS["C"])
        elif mid >= 40: patch.set_facecolor(GRADE_COLORS["D"])
        else:           patch.set_facecolor(GRADE_COLORS["F"])
    legend = [mpatches.Patch(color=GRADE_COLORS[g], label=f"Grade {g}")
              for g in ["A","B","C","D","F"]]
    ax.legend(handles=legend, loc="upper left", fontsize=9)
    ax.axvline(df["final_score"].mean(), color="#2c3e50", linestyle="--",
               linewidth=1.8, label=f"Mean: {df['final_score'].mean():.1f}")
    ax.set_title("Final Score Distribution", fontsize=14, fontweight="bold")
    ax.set_xlabel("Final Score"); ax.set_ylabel("Number of Students")
    ax.spines[["top","right"]].set_visible(False)
    _save(fig, "3_score_histogram.png")

    # ── 4. Score Comparison: Midterm vs Final Exam ────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(df))
    w = 0.28
    ax.bar(x - w, df["midterm"],    width=w, label="Midterm",    color="#3498db", edgecolor="white")
    ax.bar(x,     df["final"],      width=w, label="Final Exam", color="#2ecc71", edgecolor="white")
    ax.bar(x + w, df["assignment"], width=w, label="Assignment", color="#e67e22", edgecolor="white")
    ax.set_xticks(x); ax.set_xticklabels(df["name"], rotation=30, ha="right", fontsize=9)
    ax.set_title("Score Comparison per Student", fontsize=14, fontweight="bold")
    ax.set_ylabel("Score"); ax.set_ylim(0, 115)
    ax.legend(); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    _save(fig, "4_score_comparison.png")

    # ── 5. Final Score Line Plot (ranked) ─────────────────────
    sorted_df = df.sort_values("final_score", ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(sorted_df["name"], sorted_df["final_score"],
            marker="o", markersize=8, linewidth=2.2, color="#8e44ad")
    for i, row in sorted_df.iterrows():
        ax.annotate(f"{row['final_score']:.1f}",
                    (row["name"], row["final_score"]),
                    textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=8, color="#2c3e50")
    ax.axhline(sorted_df["final_score"].mean(), color="#e74c3c",
               linestyle="--", linewidth=1.5, label="Class Average")
    ax.set_title("Final Scores Ranked", fontsize=14, fontweight="bold")
    ax.set_ylabel("Final Score"); ax.set_ylim(0, 110)
    ax.tick_params(axis="x", rotation=30)
    ax.legend(); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    _save(fig, "5_score_line.png")

    # ── 6. Scatter: Midterm vs Final Exam ─────────────────────
    fig, ax = plt.subplots(figsize=(7, 5))
    for grade, grp in df.groupby("grade"):
        ax.scatter(grp["midterm"], grp["final"],
                   color=GRADE_COLORS[grade], label=f"Grade {grade}",
                   s=100, edgecolors="white", linewidths=1.2, zorder=3)
    for _, row in df.iterrows():
        ax.annotate(row["name"], (row["midterm"], row["final"]),
                    textcoords="offset points", xytext=(6, 4),
                    fontsize=7.5, color="#555")
    m = np.polyfit(df["midterm"], df["final"], 1)
    x_line = np.linspace(df["midterm"].min()-5, df["midterm"].max()+5, 100)
    ax.plot(x_line, np.polyval(m, x_line), "k--", linewidth=1.2, label="Trend")
    ax.set_title("Midterm vs Final Exam", fontsize=14, fontweight="bold")
    ax.set_xlabel("Midterm Score"); ax.set_ylabel("Final Exam Score")
    ax.legend(fontsize=8); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    _save(fig, "6_scatter_midterm_final.png")

    print(f"\n  ✔  All 6 charts saved to ./{CHART_DIR}/")


# ─────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║    STUDENT PERFORMANCE ANALYZER          ║
║    (Pandas + Matplotlib Edition)         ║
╠══════════════════════════════════════════╣
║  1.  Add Student                         ║
║  2.  Remove Student                      ║
║  3.  Search Student                      ║
║  4.  Update Student                      ║
║  5.  Show All Students                   ║
║  6.  Generate Report (statistics)        ║
║  7.  Grade Visualization (charts)        ║
║  8.  Save & Exit                         ║
╚══════════════════════════════════════════╝"""

def main():
    print("\n  ══  Student Performance Analyzer  ══")
    load_students()
    while True:
        print(MENU)
        choice = input("  Choice (1-8): ").strip()
        if   choice == "1": add_student()
        elif choice == "2": remove_student()
        elif choice == "3": search_student()
        elif choice == "4": update_student()
        elif choice == "5": show_all_students()
        elif choice == "6": generate_report()
        elif choice == "7": grade_visualization()
        elif choice == "8":
            save_students()
            print("\n  Goodbye!\n"); break
        else:
            print("  Invalid — enter 1 to 8.")
        input("\n  Press ENTER to continue...")

if __name__ == "__main__":
    main()
