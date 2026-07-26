"""스마트 안전장비 지원현장 vs 전체 중소규모 건설현장 사망자·부상자 수 비교.

사망자와 부상자는 절대 건수 규모가 크게 달라 각각 별도 패널(고유 y축)로 표시한다.
세 집단은 근로자 규모(전체 약 570만 명 vs 지원현장 4,481명 vs 연구현장)가 크게
다르므로, 절대 건수는 모집단 크기 차이를 반영한다는 점에 유의.

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
COLORS = ["#888888", "#55A868", "#4C72B0"]
DEATHS = [171, 1, 0]
INJURIES = [2485, 15, 0]


def draw_panel(ax, values, title):
    bars = ax.bar(GROUPS, values, color=COLORS, width=0.55)
    top = max(values) if max(values) > 0 else 1
    for bar, val in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + top * 0.02,
            f"{val:,}명",
            ha="center",
            fontsize=12,
            fontweight="bold",
        )
    ax.set_title(title, fontsize=13, pad=10)
    ax.set_ylabel("명", fontsize=10)
    ax.set_ylim(0, top * 1.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(axis="x", length=0, labelsize=9)


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    draw_panel(ax1, DEATHS, "사망자")
    draw_panel(ax2, INJURIES, "부상자")

    fig.suptitle(
        "스마트 안전장비 지원현장의 사망자·부상자 수 비교 (중소규모 건설현장, 2023년 말 기준)",
        fontsize=14,
        y=1.02,
    )

    fig.text(
        0.01,
        -0.04,
        "출처: 류정·박인선 (2025), 「건설현장의 스마트 안전장비 성능과 도입 효과 분석」, Crisisonomy\n"
        "※ 세 집단은 근로자 규모(전체 약 570만 명 vs 지원현장 4,481명)가 크게 달라 절대 건수는 모집단 크기를 반영함 — 규모 보정 비교는 사고재해율(%) 차트 참조",
        fontsize=8,
        color="gray",
        ha="left",
    )

    plt.tight_layout()
    out_path = OUT_DIR / "11_스마트안전장비_사망자_부상자_비교.png"
    plt.savefig(out_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"저장됨: {out_path}")


if __name__ == "__main__":
    main()
