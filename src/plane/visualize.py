# Last updated: 2026-07-19
"""산업재해 데이터 시각화: 로봇밀도, 사고재해자/사망자, 재해정도.""" 

import platform
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CSV_DIR = BASE_DIR / "asset"
OUT_DIR = BASE_DIR / "visualizations"
OUT_DIR.mkdir(exist_ok=True)


def plot_robot_density():
    path = CSV_DIR / "기획_로봇밀도.csv"
    df = pd.read_csv(path, skiprows=3, thousands=",")
    df.columns = ["구분", "기준연도", "값", "단위", "비고", "출처"]

    density = df[df["구분"] == "로봇밀도"].dropna(subset=["기준연도"]).copy()
    density["기준연도"] = density["기준연도"].astype(int)
    density = density.sort_values("기준연도")

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(density["기준연도"].astype(str), density["값"], color="#4C72B0")
    ax.bar_label(bars, padding=3, fontsize=15, fontweight="bold")
    ax.set_title("연도별 로봇밀도 (종업원 1만 명당 가동대수)", fontsize=16, fontweight="bold")
    ax.set_xlabel("연도", fontsize=14, fontweight="bold")
    ax.set_ylabel("로봇밀도 (대)", fontsize=14, fontweight="bold")
    ax.tick_params(axis="both", labelsize=13)
    plt.setp(ax.get_xticklabels(), fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_로봇밀도_연도별.png", dpi=200)
    plt.close(fig)


KEEP_INDUSTRIES = ["제조업", "건설업", "운수·창고·통신업"]


def load_industry_matrix(paths, drop_columns=("합계",)):
    """여러 연도 CSV(대업종 x 항목)를 같은 항목끼리 합산."""
    matrix = None
    for path in paths:
        df = pd.read_csv(path, header=[0, 1], thousands=",")
        df = df.set_index(df.columns[0])
        df.index.name = "대업종"
        df.columns = [c[1] for c in df.columns]
        df = df.loc[[i for i in KEEP_INDUSTRIES if i in df.index]]
        df = df.drop(columns=[c for c in drop_columns if c in df.columns])
        matrix = df if matrix is None else matrix.add(df, fill_value=0)

    matrix = matrix.loc[:, (matrix != 0).any(axis=0)]
    return matrix.loc[matrix.sum(axis=1).sort_values(ascending=False).index]


def plot_heatmap(matrix, title, outfile, cbar_label="건수"):
    fig, ax = plt.subplots(
        figsize=(0.9 * len(matrix.columns) + 2.5, 0.45 * len(matrix.index) + 1.8)
    )
    im = ax.imshow(matrix.values, cmap="OrRd", aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right", fontsize=11)
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index, fontsize=11)

    vmax = matrix.values.max()
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            val = matrix.values[i, j]
            color = "white" if val > vmax * 0.6 else "black"
            ax.text(j, i, f"{val:,.0f}", ha="center", va="center", fontsize=10, color=color)

    cbar = fig.colorbar(im, ax=ax, label=cbar_label)
    cbar.ax.tick_params(labelsize=10)
    cbar.set_label(cbar_label, fontsize=11)
    ax.set_title(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(outfile, dpi=300)
    plt.close(fig)


def main():
    plot_robot_density()

    victims = load_industry_matrix(
        [
            CSV_DIR / "기획_2023사고재해자.csv",
            CSV_DIR / "기획_2024사고재해자.csv",
            CSV_DIR / "기획_2025사고재해자.csv",
        ]
    )
    plot_heatmap(
        victims,
        "대업종별 사고재해자 발생형태 (2023~2025 합계, 제조·건설·운수창고통신업)",
        OUT_DIR / "02_사고재해자_업종별_발생형태.png",
    )

    deaths = load_industry_matrix(
        [
            CSV_DIR / "기획_2023사고사망자.csv",
            CSV_DIR / "기획_2024사고사망자.csv",
            CSV_DIR / "기획_2025사고사망자.csv",
        ]
    )
    plot_heatmap(
        deaths,
        "대업종별 사고사망자 발생형태 (2023~2025 합계, 제조·건설·운수창고통신업)",
        OUT_DIR / "03_사고사망자_업종별_발생형태.png",
    )

    severity = load_industry_matrix(
        [
            CSV_DIR / "기획_22_사고재해정도.csv",
            CSV_DIR / "기획_23_사고재해정도.csv",
            CSV_DIR / "기획_24_사고재해정도.csv",
            CSV_DIR / "기획_25_사고재해정도.csv",
        ],
        drop_columns=("합계", "요양재해자"),
    )
    plot_heatmap(
        severity,
        "대업종별 재해정도 (2023~2025 합계, 제조·건설·운수창고통신업)",
        OUT_DIR / "04_사고재해정도_업종별.png",
    )

    print(f"완료: {OUT_DIR} 에 4개 이미지 저장됨")


if __name__ == "__main__":
    main()
