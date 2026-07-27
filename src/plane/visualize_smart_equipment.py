"""스마트 안전장비 지원현장 vs 전체 중소규모 건설현장 사고재해율 비교.

출처: 류정·박인선 (2025), 「건설현장의 스마트 안전장비 성능과 도입 효과 분석」, Crisisonomy
"""

import platform
from pathlib import Path

import matplotlib.pyplot as plt

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = BASE_DIR / "visualizations"
OUT_DIR.mkdir(exist_ok=True)

GROUPS = ["전체 중소규모\n건설현장 평균", "스마트 안전장비\n지원현장(2021~2023)", "본 연구 현장"]
RATES = [0.461, 0.357, 0.0]
DETAILS = [
    "근로자 576,224명\n사망 171명 · 부상 2,485명",
    "근로자 4,481명(123개소)\n사망 1명 · 부상 15명",
    "사망·부상 0건",
]
COLORS = ["#888888", "#55A868", "#4C72B0"]


def main():
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(GROUPS, RATES, color=COLORS, width=0.55)

    for bar, rate, detail in zip(bars, RATES, DETAILS):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.012,
            f"{rate:.3f}%" if rate > 0 else "0%",
            ha="center",
            fontsize=13,
            fontweight="bold",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            -0.045,
            detail,
            ha="center",
            va="top",
            fontsize=8.5,
            color="dimgray",
        )

    ax.annotate(
        "",
        xy=(1, 0.40),
        xytext=(0, 0.50),
        arrowprops=dict(
            arrowstyle="->", color="#C44E52", lw=1.5,
            connectionstyle="arc3,rad=-0.15",
        ),
    )
    ax.text(
        0.5, 0.475, "-22.56%",
        ha="center", va="bottom",
        fontsize=11, color="#C44E52", fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.5),
    )

    ax.set_ylabel("사고재해율 (%)", fontsize=11)
    ax.set_ylim(-0.09, 0.55)
    ax.set_title(
        "스마트 안전장비 지원현장의 사고재해율 비교\n(중소규모 건설현장, 2023년 말 기준)",
        fontsize=13,
        pad=14,
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, pad=35)

    fig.text(
        0.01,
        -0.02,
        "출처: 류정·박인선 (2025), 「건설현장의 스마트 안전장비 성능과 도입 효과 분석」, Crisisonomy",
        fontsize=8,
        color="gray",
        ha="left",
    )

    plt.tight_layout()
    out_path = OUT_DIR / "10_스마트안전장비_지원현장_사고재해율_비교.png"
    plt.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"저장됨: {out_path}")


if __name__ == "__main__":
    main()
