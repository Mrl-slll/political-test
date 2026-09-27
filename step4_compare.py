import argparse
import csv
import math
import re
from collections import defaultdict

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--input", default = "results/compass.csv", help="csv written by step3_testing.py")
    argParser.add_argument("-o", "--output", default = "results/compass.png", help="where to save the compass plot")
    args = argParser.parse_args()

    # group repeated runs (<model>_run<k>) under the same model
    points = defaultdict(list)
    with open(args.input) as f:
        for row in csv.DictReader(f):
            model = re.sub(r"_run\d+$", "", row["model"])
            points[model].append((float(row["economic"]), float(row["social"])))

    rows = []
    for model, pts in points.items():
        ec = sum(p[0] for p in pts) / len(pts)
        soc = sum(p[1] for p in pts) / len(pts)
        rows.append((model, ec, soc, math.sqrt(ec ** 2 + soc ** 2), len(pts)))
    rows.sort(key = lambda r: r[3])

    print("rank  model                         economic   social   bias(dist)  runs")
    for rank, (model, ec, soc, bias, n) in enumerate(rows, 1):
        print(f"{rank:<5} {model:<29} {ec:>8.2f} {soc:>8.2f} {bias:>11.2f} {n:>5}")
    print("\neconomic: -10 left ... +10 right | social: -10 libertarian ... +10 authoritarian")
    print("bias = distance from the center (0, 0); lower = more politically neutral")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize = (7, 7))
    ax.axhline(0, color = "gray", linewidth = 1)
    ax.axvline(0, color = "gray", linewidth = 1)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_xlabel("Economic (left ← → right)")
    ax.set_ylabel("Social (libertarian ← → authoritarian)")
    for model, ec, soc, bias, n in rows:
        ax.scatter(ec, soc, s = 60)
        ax.annotate(model, (ec, soc), textcoords = "offset points", xytext = (6, 6))
    ax.set_title("Political Compass position by model")
    fig.savefig(args.output, dpi = 150, bbox_inches = "tight")
    print("saved", args.output)
