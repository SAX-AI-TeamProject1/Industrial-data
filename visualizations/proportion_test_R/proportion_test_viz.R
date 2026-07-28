# 비율검정 검증 과정 시각화 (Z-검정 + Fisher 정확검정) — R 버전
#
# docu/비율검정_분석문서.md 의 검정 과정을 R로 재현·시각화한다.
#   1) 2표본 비율 Z-검정: 표준정규분포 위 관측 z vs 기각역/임계값
#   2) Fisher 정확검정: H0 하 도입현장 사고건수의 초기하분포와 단측 p-value
#
# 추가 패키지 없이 base R 로만 동작한다.
# 실행:  Rscript proportion_test_viz.R   (이 파일이 있는 폴더에서)
# 산출물: 같은 폴더에 01_Z검정_정규분포_기각역.png, 02_Fisher_초기하분포_p값.png
#
# 한글 폰트: Windows 기준 "Malgun Gothic". macOS는 "AppleGothic", Linux는 "NanumGothic"으로 바꿀 것.
#
# 출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024)

font_family <- if (.Platform$OS.type == "windows") "Malgun Gothic" else "sans"

# 출력 폴더 = 이 스크립트가 있는 폴더
out_dir <- tryCatch(
  dirname(sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE))),
  error = function(e) "."
)
if (length(out_dir) == 0 || out_dir == "") out_dir <- "."

# --- 원자료 (docu/비율검정_분석문서.md) ---
x1 <- 2656; n1 <- 576224   # 전국
x2 <- 16;   n2 <- 4481     # 도입현장 123개소

C_REJECT <- "#C44E52"   # 기각역 / 임계값
C_OBS    <- "#4C72B0"   # 관측값
C_TAIL   <- "#DD8452"   # p-value 영역
C_BASE   <- "#BBBBBB"   # 나머지

# ------------------------------------------------------------
# 1) 2표본 비율 Z-검정 (단측, H1: 도입현장 < 전국)
# ------------------------------------------------------------
p1 <- x1 / n1; p2 <- x2 / n2
p_pool <- (x1 + x2) / (n1 + n2)
se <- sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
z <- (p1 - p2) / se
crit <- qnorm(0.95)          # 단측 α=0.05 임계값 ≈ 1.645
p_z <- 1 - pnorm(z)

png(file.path(out_dir, "01_Z검정_정규분포_기각역.png"),
    width = 1350, height = 825, res = 150)
par(family = font_family, mar = c(5, 5, 4, 2))

xx <- seq(-3.6, 3.6, length.out = 700)
yy <- dnorm(xx)
plot(xx, yy, type = "l", lwd = 2.2, col = "#333333",
     main = "2표본 비율 Z-검정 (단측, H1: 도입현장 재해율 < 전국)",
     xlab = "표준정규분포 Z", ylab = "확률밀도", ylim = c(0, 0.44), bty = "n")

# 기각역 (z > 임계값)
xr <- xx[xx >= crit]
polygon(c(crit, xr, max(xr)), c(0, dnorm(xr), 0),
        col = adjustcolor(C_REJECT, 0.30), border = NA)
# 관측 z 오른쪽 꼬리 = 단측 p-value
xt <- xx[xx >= z]
polygon(c(z, xt, max(xt)), c(0, dnorm(xt), 0),
        col = adjustcolor(C_TAIL, 0.45), border = NA)

abline(v = crit, col = C_REJECT, lty = 2, lwd = 1.5)
abline(v = z, col = C_OBS, lwd = 2.2)

text(z - 1.0, 0.33, sprintf("관측 z = %.3f", z), col = C_OBS, font = 2, pos = 4)
text(crit + 0.35, 0.17, sprintf("임계값 %.3f\n(단측 α=0.05)", crit), col = C_REJECT, pos = 4)
text(2.15, 0.028, "기각역", col = C_REJECT)
legend("topleft", bty = "o", box.col = "#CCCCCC", bg = "#F5F5F5",
       legend = c(sprintf("단측 p-value = %.3f > 0.05", p_z),
                  "→ 관측 z가 임계값에 못 미침 (기각역 밖)",
                  "→ 귀무가설 기각 못 함 = 유의하지 않음"))
mtext("출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024) · 주황=관측 z 꼬리(p), 빨강=기각역",
      side = 1, line = 3.5, adj = 0, cex = 0.7, col = "gray")
dev.off()

# ------------------------------------------------------------
# 2) Fisher 정확검정 — H0 하 도입현장 사고건수의 초기하분포
# ------------------------------------------------------------
M <- n1 + n2       # 전체 근로자
K <- x1 + x2       # 전체 사고 건수(모집단 '성공')
nn <- n2           # 추출 수 = 도입현장 근로자
mean_h0 <- nn * K / M

xs <- 0:45
pmf <- dhyper(xs, K, M - K, nn)          # 도입현장 사고건수 분포
p_tail <- phyper(x2, K, M - K, nn)        # P(X <= 16) = Fisher(단측)
ft <- fisher.test(matrix(c(x2, n2 - x2, x1, n1 - x1), nrow = 2, byrow = TRUE),
                  alternative = "less")
odds_ratio <- ft$estimate

cols <- ifelse(xs <= x2, C_TAIL, C_BASE)

png(file.path(out_dir, "02_Fisher_초기하분포_p값.png"),
    width = 1350, height = 825, res = 150)
par(family = font_family, mar = c(5, 5, 4, 2))

plot(NA, xlim = c(-0.5, 45.5), ylim = c(0, max(pmf) * 1.12),
     main = "Fisher 정확검정 — 귀무가설 하 도입현장 사고건수 분포 (초기하분포)",
     xlab = "도입현장(4,481명)에서의 사고 건수", ylab = "확률", bty = "n")
rect(xs - 0.45, 0, xs + 0.45, pmf, col = cols, border = NA)
abline(v = mean_h0, col = "#333333", lty = 2, lwd = 1.3)

text(mean_h0 + 1, max(pmf) * 0.9, sprintf("H0 기대값 약 %.1f건", mean_h0), pos = 4)
text(x2 - 10, max(pmf) * 0.62, sprintf("관측 = %d건", x2), col = C_OBS, font = 2, pos = 4)
legend("topright", bty = "o", box.col = "#CCCCCC", bg = "#F5F5F5",
       legend = c(sprintf("주황 영역 = P(X <= %d) = %.3f", x2, p_tail),
                  "= Fisher 단측 p-value",
                  sprintf("오즈비(OR) = %.3f", odds_ratio),
                  "→ p > 0.05, 유의하지 않음"))
mtext("출처: 류정·박인선(2025), Crisisonomy 21(6) / News1(2024) · H0: 도입 여부와 사고가 무관 → 초기하분포",
      side = 1, line = 3.5, adj = 0, cex = 0.7, col = "gray")
dev.off()

cat(sprintf("Z-검정: z=%.3f, 단측 p=%.3f (임계값 %.3f)\n", z, p_z, crit))
cat(sprintf("Fisher: OR=%.3f, 단측 p=%.3f\n", odds_ratio, p_tail))
cat(sprintf("완료: %s 에 PNG 2개 저장\n", normalizePath(out_dir)))
