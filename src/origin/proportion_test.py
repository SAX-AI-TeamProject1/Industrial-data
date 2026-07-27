"""스마트 안전장비 도입현장 vs 전국 평균 재해율 — 비율검정 재현.

docu/비율검정_분석문서.md 의 분석을 실행 가능한 코드로 재현한다.
  1) 2표본 비율 Z-검정 (단측)
  2) Fisher 정확검정 (단측)
  3) 두 비율 차이의 95% 신뢰구간
  4) 독립성 보정: 전국 통계에서 도입현장을 제외한 '순수 미도입군'으로 재검정

가설: H0 두 재해율이 같다(p1 = p2) / H1 도입현장이 더 낮다(p1 > p2), 단측, α = 0.05

출처: 류정·박인선(2025), 「건설현장의 스마트 안전장비 성능과 도입 효과 분석」,
      Crisisonomy 21(6) / News1(2024)
"""

from dataclasses import dataclass

import numpy as np
from scipy import stats

# --- 원자료 (분석 문서 1장) ---
# (사고자 수 x, 근로자 수 n)
# 전국 근로자 수는 원문 "약 570만 명"이 재해율 0.461%와 정합하지 않아,
# 재해율 역산을 근거로 576,000명(약 57.6만)으로 정정하여 사용.
NATIONWIDE = (2656, 576000)  # 전국 중소규모 건설현장: 사망 171 + 부상 2,485
ADOPTER = (16, 4481)         # 스마트 안전장비 지원현장 123개소: 사망 1 + 부상 15

ALPHA = 0.05


@dataclass
class ProportionTestResult:
    """한 쌍(전국 vs 도입현장)에 대한 비율검정 결과 묶음."""

    p1: float          # 전국(미도입군) 재해율
    p2: float          # 도입현장 재해율
    z: float           # 2표본 비율 Z-통계량
    p_z: float         # Z-검정 단측 p-value
    odds_ratio: float  # Fisher 정확검정 오즈비
    p_fisher: float    # Fisher 정확검정 단측 p-value
    ci_low: float      # 비율 차이(p1-p2) 95% 신뢰구간 하한
    ci_high: float     # 비율 차이 95% 신뢰구간 상한

    @property
    def significant(self) -> bool:
        """단측 유의수준 0.05에서 통계적으로 유의한가 (더 보수적인 Fisher 기준)."""
        return self.p_fisher < ALPHA


def two_proportion_ztest(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float]:
    """2표본 비율 Z-검정. H1: p1 > p2 (단측). 합동비율 기반 표준오차 사용.

    반환: (z 통계량, 단측 p-value = P(Z > z))
    """
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se_pool
    p_value = 1 - stats.norm.cdf(z)
    return z, p_value


def fisher_test(x1: int, n1: int, x2: int, n2: int) -> tuple[float, float]:
    """Fisher 정확검정. 도입현장의 사고 오즈가 더 낮은지(단측) 검정.

    2x2 분할표는 [[도입현장 사고, 미사고], [전국 사고, 미사고]] 순서.
    반환: (오즈비, 단측 p-value)
    """
    table = [[x2, n2 - x2], [x1, n1 - x1]]
    odds_ratio, p_value = stats.fisher_exact(table, alternative="less")
    return odds_ratio, p_value


def diff_confidence_interval(
    x1: int, n1: int, x2: int, n2: int, conf: float = 0.95
) -> tuple[float, float]:
    """두 비율 차이(p1 - p2)의 신뢰구간. 독립 표본 가정의 unpooled 표준오차 사용."""
    p1, p2 = x1 / n1, x2 / n2
    se_diff = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    z_crit = stats.norm.ppf(1 - (1 - conf) / 2)
    diff = p1 - p2
    return diff - z_crit * se_diff, diff + z_crit * se_diff


def run_proportion_test(
    nationwide: tuple[int, int], adopter: tuple[int, int]
) -> ProportionTestResult:
    """전국(또는 순수 미도입군) vs 도입현장에 대해 세 검정을 모두 수행."""
    x1, n1 = nationwide
    x2, n2 = adopter
    z, p_z = two_proportion_ztest(x1, n1, x2, n2)
    odds_ratio, p_fisher = fisher_test(x1, n1, x2, n2)
    ci_low, ci_high = diff_confidence_interval(x1, n1, x2, n2)
    return ProportionTestResult(
        p1=x1 / n1,
        p2=x2 / n2,
        z=z,
        p_z=p_z,
        odds_ratio=odds_ratio,
        p_fisher=p_fisher,
        ci_low=ci_low,
        ci_high=ci_high,
    )


def purify_nationwide(
    nationwide: tuple[int, int], adopter: tuple[int, int]
) -> tuple[int, int]:
    """전국 통계에서 도입현장을 제외해 '순수 미도입군'을 만든다 (독립성 보정)."""
    x1, n1 = nationwide
    x2, n2 = adopter
    return x1 - x2, n1 - n2


def _print_result(title: str, r: ProportionTestResult) -> None:
    print(f"[{title}]")
    print(f"  재해율        : 전국 {r.p1 * 100:.4f}% vs 도입현장 {r.p2 * 100:.4f}%"
          f"  (차이 {(r.p1 - r.p2) * 100:.4f}%p)")
    print(f"  Z-검정(단측)  : z={r.z:.3f}, p={r.p_z:.4f}")
    print(f"  Fisher(단측)  : OR={r.odds_ratio:.3f}, p={r.p_fisher:.4f}")
    print(f"  95% 신뢰구간  : [{r.ci_low * 100:.4f}%p, {r.ci_high * 100:.4f}%p]"
          f"  (0 포함: {'예' if r.ci_low <= 0 <= r.ci_high else '아니오'})")
    print(f"  → α={ALPHA}에서 {'유의함' if r.significant else '유의하지 않음'}\n")


def main() -> None:
    raw = run_proportion_test(NATIONWIDE, ADOPTER)
    _print_result("보정 전 — 전국 평균에 도입현장 포함 가능성 무시", raw)

    pure = run_proportion_test(purify_nationwide(NATIONWIDE, ADOPTER), ADOPTER)
    _print_result("보정 후 — 전국에서 도입현장을 제외한 순수 미도입군", pure)

    rel = (1 - ADOPTER[0] / ADOPTER[1] / (NATIONWIDE[0] / NATIONWIDE[1])) * 100
    print(f"참고(검정 아님): 상대적 감소율 = {rel:.2f}%")


if __name__ == "__main__":
    main()
