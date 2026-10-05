"""비율검정 후속 시각화 — 95% 신뢰구간 + 검정력(power) 곡선.

docu/비율검정_분석문서.md 의 결론("유의하지 않음, 표본 규모상 검정력 부족")을
숫자로 확인하기 위한 두 장의 그림.
  12) 재해율 차이의 95% 신뢰구간 (보정 전 / 순수 미도입군 보정 후)
  13) 도입현장 근로자 수에 따른 검정력 곡선 (관측 효과 크기 고정, 단측 α=0.05)

출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024)
"""

import platform
from pathlib import Path

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import font_manager

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    names = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("NanumGothic", "Noto Sans CJK KR", "Noto Sans CJK JP"):
        if cand in names:
            plt.rcParams["font.family"] = cand
            break
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUT_DIR = BASE_DIR / "visualizations"
OUT_DIR.mkdir(parents=True, exist_ok=True)

X1, N1 = 2656, 576224  # 전국 중소규모 건설현장
X2, N2 = 16, 4481      # 스마트 안전장비 지원현장 123개소
ALPHA = 0.05

C_OBS = "#4C72B0"
C_REJECT = "#C44E52"
C_GOOD = "#55A868"
C_INK = "#222222"
C_MUTED = "#777777"


def diff_ci(x1, n1, x2, n2):
    p1, p2 = x1 / n1, x2 / n2
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    d = p1 - p2
    return d, d - 1.96 * se, d + 1.96 * se


def power(n2, p1=X1 / N1, p2=X2 / N2, n1=N1):
    """관측 재해율(p1, p2)이 참일 때, 도입현장 근로자 수가 n2면 단측 Z-검정이 유의할 확률."""
    z_a = stats.norm.ppf(1 - ALPHA)
    pp = (p1 * n1 + p2 * n2) / (n1 + n2)
    se0 = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    se1 = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    return 1 - stats.norm.cdf((z_a * se0 - (p1 - p2)) / se1)


def n_for_power(target):
    lo, hi = N2, 10**7
    while hi - lo > 1:
        mid = (lo + hi) // 2
        lo, hi = (mid, hi) if power(mid) < target else (lo, mid)
    return hi


def plot_ci():
    rows = [
        ("보정 전\n(전국 전체)", diff_ci(X1, N1, X2, N2)),
        ("보정 후\n(순수 미도입군)", diff_ci(X1 - X2, N1 - N2, X2, N2)),
    ]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
    for i, (label, (d, lo, hi)) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.plot([lo * 100, hi * 100], [y, y], color=C_OBS, lw=4, solid_capstyle="round")
        ax.plot(d * 100, y, "o", color="white", mec=C_OBS, mew=3, ms=13, zorder=3)
        ax.text(d * 100, y + 0.24, f"{d*100:.3f}%p", ha="center", fontsize=13, fontweight="bold", color=C_OBS)
        ax.text(lo * 100, y - 0.3, f"{lo*100:.3f}", ha="center", fontsize=11, color=C_MUTED)
        ax.text(hi * 100, y - 0.3, f"{hi*100:.3f}", ha="center", fontsize=11, color=C_MUTED)
    ax.axvline(0, color=C_REJECT, ls="--", lw=2)
    ax.text(0.006, len(rows) - 0.35, "차이 없음 (0)", color=C_REJECT, ha="left", fontsize=12, fontweight="bold")
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=12)
    ax.set_ylim(-0.7, len(rows) - 0.2)
    ax.set_xlim(-0.15, 0.35)
    ax.set_xlabel("재해율 차이 (전국 − 도입현장, %p)", fontsize=12)
    ax.set_title("재해율 차이의 95% 신뢰구간 — 두 경우 모두 0을 포함", fontsize=15, fontweight="bold", pad=14)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.text(0.01, 0.01, "출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024) · unpooled SE, 1.96σ",
             fontsize=9, color=C_MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = OUT_DIR / "12_재해율차이_95신뢰구간.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out


def plot_power():
    ns = np.linspace(1000, 60000, 400)
    pw = np.array([power(n) for n in ns])
    now = power(N2)
    n80 = n_for_power(0.8)

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=200)
    ax.plot(ns, pw * 100, color=C_INK, lw=2.5)
    ax.axhline(80, color=C_GOOD, ls="--", lw=1.6)
    ax.text(59000, 82, "통상 목표 검정력 80%", color=C_GOOD, ha="right", fontsize=11, fontweight="bold")

    ax.plot(N2, now * 100, "o", color=C_REJECT, ms=11, zorder=3)
    ax.annotate(f"현재 표본 {N2:,}명\n검정력 {now*100:.0f}%",
                xy=(N2, now * 100), xytext=(N2 + 4000, now * 100 - 16),
                fontsize=12, fontweight="bold", color=C_REJECT,
                arrowprops=dict(arrowstyle="->", color=C_REJECT, lw=1.4))
    ax.plot(n80, 80, "o", color=C_GOOD, ms=11, zorder=3)
    ax.annotate(f"약 {n80:,}명 필요\n(현재의 {n80/N2:.1f}배)",
                xy=(n80, 80), xytext=(n80 + 5000, 58),
                fontsize=12, fontweight="bold", color=C_GOOD,
                arrowprops=dict(arrowstyle="->", color=C_GOOD, lw=1.4))

    ax.set_xlim(0, 60000)
    ax.set_ylim(0, 102)
    ax.set_xlabel("스마트 안전장비 도입현장 근로자 수 (명)", fontsize=12)
    ax.set_ylabel("검정력 (%)", fontsize=12)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.set_title("관측된 차이(0.461% → 0.357%)가 실제라면, 몇 명을 봐야 유의하게 잡히는가",
                 fontsize=14, fontweight="bold", pad=14)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#EEEEEE")
    fig.text(0.01, 0.01, "2표본 비율 Z-검정, 단측 α=0.05, 전국 n=576,224 고정 · 효과 크기는 관측값을 참으로 가정",
             fontsize=9, color=C_MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = OUT_DIR / "13_표본규모별_검정력곡선.png"
    fig.savefig(out, facecolor="white")
    plt.close(fig)
    return out, now, n80


if __name__ == "__main__":
    print("저장:", plot_ci())
    out, now, n80 = plot_power()
    print("저장:", out)
    print(f"현재 검정력 {now:.3f}, 80% 검정력 필요 표본 {n80:,}명 ({n80/N2:.2f}배)")
