"""비율검정 검증 과정 시각화 (Z-검정 + Fisher 정확검정).

docu/비율검정_분석문서.md 의 검정 과정을 그림으로 보여준다.
  1) 2표본 비율 Z-검정: 표준정규분포 위에서 관측 z와 기각역/임계값 비교
  2) Fisher 정확검정: H0 하 도입현장 사고건수의 초기하분포와 단측 p-value 영역

동일한 그림을 R로도 그릴 수 있도록 visualizations/proportion_test_R/proportion_test_viz.R 를 함께 둔다.
이 스크립트는 그 PNG 산출물을 Python(matplotlib)으로 생성한다.

출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024)
"""

import platform
from pathlib import Path

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = BASE_DIR / "visualizations" / "proportion_test_R"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- 원자료 (docu/비율검정_분석문서.md) ---
X1, N1 = 2656, 576224  # 전국
X2, N2 = 16, 4481      # 도입현장 123개소

C_REJECT = "#C44E52"   # 기각역 / 임계값 (빨강)
C_OBS = "#4C72B0"      # 관측값 (파랑)
C_TAIL = "#DD8452"     # p-value 영역 (주황)
C_BASE = "#BBBBBB"     # 나머지 (회색)


def plot_ztest():
    """표준정규분포 위에서 2표본 비율 Z-검정(단측)을 시각화."""
    p1, p2 = X1 / N1, X2 / N2
    p_pool = (X1 + X2) / (N1 + N2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / N1 + 1 / N2))
    z = (p1 - p2) / se
    crit = stats.norm.ppf(0.95)          # 단측 α=0.05 임계값 = 1.645
    p_value = 1 - stats.norm.cdf(z)

    x = np.linspace(-3.6, 3.6, 700)
    y = stats.norm.pdf(x)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(x, y, color="#333333", lw=1.8)

    # 기각역 (z > 임계값)
    xr = x[x >= crit]
    ax.fill_between(xr, stats.norm.pdf(xr), color=C_REJECT, alpha=0.30)
    # 관측 z 오른쪽 꼬리 = 단측 p-value
    xt = x[x >= z]
    ax.fill_between(xt, stats.norm.pdf(xt), color=C_TAIL, alpha=0.45)

    ax.axvline(crit, color=C_REJECT, ls="--", lw=1.5)
    ax.axvline(z, color=C_OBS, lw=2.2)

    ax.annotate(f"관측 z = {z:.3f}", xy=(z, stats.norm.pdf(z)),
                xytext=(z - 1.7, 0.33), color=C_OBS, fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_OBS))
    ax.annotate(f"임계값 {crit:.3f}\n(단측 α=0.05)", xy=(crit, 0.06),
                xytext=(crit + 0.35, 0.16), color=C_REJECT, fontsize=10,
                arrowprops=dict(arrowstyle="->", color=C_REJECT))
    ax.text(2.15, 0.028, "기각역", color=C_REJECT, fontsize=10, ha="center")

    ax.text(0.02, 0.97,
            f"단측 p-value = {p_value:.3f} > 0.05\n"
            f"→ 관측 z가 임계값에 못 미침 (기각역 밖)\n"
            f"→ 귀무가설 기각 못 함 = 통계적으로 유의하지 않음",
            transform=ax.transAxes, va="top", fontsize=10.5,
            bbox=dict(boxstyle="round", facecolor="#F5F5F5", edgecolor="#CCCCCC"))

    ax.set_title("2표본 비율 Z-검정 (단측, H1: 도입현장 재해율 < 전국)", fontsize=13, pad=12)
    ax.set_xlabel("표준정규분포 Z")
    ax.set_ylabel("확률밀도")
    ax.set_ylim(0, 0.44)
    ax.spines[["top", "right"]].set_visible(False)

    fig.text(0.01, -0.02,
             "출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024) · 주황=관측 z 꼬리(p), 빨강=기각역",
             fontsize=8, color="gray", ha="left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "01_Z검정_정규분포_기각역.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_fisher():
    """H0 하 도입현장 사고건수의 초기하분포와 Fisher 단측 p-value 영역."""
    M = N1 + N2       # 전체 근로자
    K = X1 + X2       # 전체 사고 건수(모집단 내 '성공')
    n = N2            # 추출 수 = 도입현장 근로자
    mean = n * K / M

    xs = np.arange(0, 46)
    pmf = stats.hypergeom.pmf(xs, M, K, n)
    p_value = stats.hypergeom.cdf(X2, M, K, n)      # P(X <= 16) = Fisher(단측)
    odds_ratio, _ = stats.fisher_exact([[X2, N2 - X2], [X1, N1 - X1]], alternative="less")

    colors = [C_TAIL if xi <= X2 else C_BASE for xi in xs]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(xs, pmf, color=colors, width=0.9)

    ax.axvline(mean, color="#333333", ls="--", lw=1.3)
    ax.annotate(f"H0 기대값 약 {mean:.1f}건", xy=(mean, stats.hypergeom.pmf(int(round(mean)), M, K, n)),
                xytext=(mean + 3, pmf.max() * 0.85), fontsize=10,
                arrowprops=dict(arrowstyle="->", color="#333333"))
    ax.annotate(f"관측 = {X2}건", xy=(X2, stats.hypergeom.pmf(X2, M, K, n)),
                xytext=(X2 - 10.5, pmf.max() * 0.6), color=C_OBS, fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_OBS))

    ax.text(0.98, 0.97,
            f"주황 영역 = P(X ≤ {X2}) = {p_value:.3f}\n"
            f"= Fisher 단측 p-value\n"
            f"오즈비(OR) = {odds_ratio:.3f}\n"
            f"→ p > 0.05, 통계적으로 유의하지 않음",
            transform=ax.transAxes, va="top", ha="right", fontsize=10.5,
            bbox=dict(boxstyle="round", facecolor="#F5F5F5", edgecolor="#CCCCCC"))

    ax.set_title("Fisher 정확검정 — 귀무가설 하 도입현장 사고건수 분포 (초기하분포)",
                 fontsize=13, pad=12)
    ax.set_xlabel("도입현장(4,481명)에서의 사고 건수")
    ax.set_ylabel("확률")
    ax.spines[["top", "right"]].set_visible(False)

    fig.text(0.01, -0.02,
             "출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024) · "
             "H0: 도입 여부와 사고가 무관 → 초기하분포",
             fontsize=8, color="gray", ha="left")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_Fisher_초기하분포_p값.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    plot_ztest()
    plot_fisher()
    print(f"완료: {OUT_DIR} 에 2개 이미지 저장됨")


if __name__ == "__main__":
    main()
