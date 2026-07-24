### 로봇밀도가 높아짐에 따라 사고 감소시 적극 도입추진 해야한다로 시작했지만
### 로봇밀도가 산업재해를 크게 예방하지 못하고 있고 데이터 비교시 뚜렷하지 않습니다
### 로봇에 작업자 수신호 인식과 예측기능을 넣고 사고감소 기대효과를 보면 좋을 것 같습니다 
### 고로 실제로 사고감소 효과를 보거나 기대하려면 이런 프로젝트가 꼭 필요해 보입니다 ** 수기작성입니다 ㅎㅎ **


import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) # 환경설정 
CANDIDATE_DIRS = [SCRIPT_DIR, os.path.join(SCRIPT_DIR, "..", "..", "asset")] # asset 폴더 데이터만 이용

DATA_DIR = SCRIPT_DIR   # 아래 find_data_dir()에서 실제 값으로 갱신됨

FORCE_DATA_DIR = None

OUT_DIR = os.path.join(SCRIPT_DIR, '..', '..', "visualizations")  # 결과 이미지 저장 폴더

FILE_NAMES = {
    "y23": "기획_2023사고재해자.csv",
    "y24": "기획_2024사고재해자.csv",
    "y25": "기획_2025사고재해자.csv",
    "sev22": "기획_22_사고재해정도.csv",
    "sev23": "기획_23_사고재해정도.csv",
    "sev24": "기획_24_사고재해정도.csv",
    "sev25": "기획_25_사고재해정도.csv",
    "robot": "기획_로봇밀도.csv",
}

SRC_INJURY = "출처: 고용노동부 산업재해현황(대업종별 발생형태) 2023~2025"
SRC_SEV = "출처: 고용노동부 산업재해현황(재해정도별) 2022~2025"
SRC_ROBOT = "출처: IFR(International Federation of Robotics) World Robotics 2023~2025 요약본 및 보도자료"

# 로봇밀도는 IFR 공개 요약자료 기준 4개 연도만 확인됨 (그 외 연도 결측)
DENSITY_BY_YEAR = {2018: 774, 2021: 1000, 2023: 1012, 2024: 1220}


def setup_font():
    """Windows 한글 폰트 설정 (맑은 고딕). 없으면 기본 폰트로 폴백."""
    candidates = ["Malgun Gothic", "NanumGothic", "AppleGothic"]
    available = {f.name for f in plt.matplotlib.font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            plt.rcParams['font.family'] = name
            break
    else:
        print("경고: 한글 폰트를 찾지 못했습니다. 그래프의 한글이 깨질 수 있습니다.")
    plt.rcParams['axes.unicode_minus'] = False # 가끔 한글쓸때 - 가 깨지는 경우를 방지해줍니다
    plt.rcParams['figure.dpi'] = 140


def load_industry_csv(path):
    """대업종 x 발생형태(또는 재해정도) 형태의 CSV 공통 로더."""
    df = pd.read_csv(path, skiprows=1, thousands=',')
    df = df.rename(columns={df.columns[0]: '대업종'})
    df = df.dropna(axis=1, how='all')
    df['대업종'] = df['대업종'].astype(str).str.replace(r'\s+', '', regex=True)
    return df


def find_data_dir():
    """FORCE_DATA_DIR이 지정되어 있으면 그것을 쓰고, 아니면 CANDIDATE_DIRS를 순서대로
    확인해 11개 CSV 파일이 모두 존재하는 첫 번째 폴더를 찾는다."""
    global DATA_DIR

    if FORCE_DATA_DIR:
        DATA_DIR = FORCE_DATA_DIR
        return

    tried = []
    for d in CANDIDATE_DIRS:
        d = os.path.abspath(d)
        if d in tried:
            continue
        tried.append(d)
        if all(os.path.exists(os.path.join(d, fname)) for fname in FILE_NAMES.values()):
            DATA_DIR = d
            print(f"CSV 폴더 찾음: {DATA_DIR}")
            return

    # 못 찾았으면 에러 메시지로 시도한 폴더 목록과 각 폴더별 누락 파일을 알려준다
    msg = "CSV 파일 11개를 모두 가진 폴더를 찾지 못했습니다.\n다음 폴더들을 확인해봤습니다:\n"
    for d in tried:
        missing = [f for f in FILE_NAMES.values() if not os.path.exists(os.path.join(d, f))]
        status = "OK" if not missing else f"누락 {len(missing)}개 (예: {missing[0]})"
        msg += f"  - {d}  [{status}]\n"
    msg += ("\n해결 방법: 스크립트 상단의 FORCE_DATA_DIR 에 CSV가 실제로 들어있는 폴더의 "
            "절대경로를 직접 넣어주세요. 예:\n"
            r'  FORCE_DATA_DIR = r"C:\RobotJuly\Industrial-data\data"' + "\n")
    raise FileNotFoundError(msg)


def load_all_data():
    """모든 CSV를 읽어서 dict로 반환."""
    find_data_dir()
    p = lambda key: os.path.join(DATA_DIR, FILE_NAMES[key])

    data = {}
    data['y23'] = load_industry_csv(p('y23'))
    data['y24'] = load_industry_csv(p('y24'))
    data['y25'] = load_industry_csv(p('y25'))
    data['sev22'] = load_industry_csv(p('sev22'))
    data['sev23'] = load_industry_csv(p('sev23'))
    data['sev24'] = load_industry_csv(p('sev24'))
    data['sev25'] = load_industry_csv(p('sev25'))

    def total_and_dead(sev_df):
        row = sev_df[sev_df['대업종'] == '합계'].iloc[0]
        return row['요양재해자'] + row['사망자'], row['사망자']

    tot22, dead22 = total_and_dead(data['sev22'])
    tot23, dead23 = total_and_dead(data['sev23'])
    tot24, dead24 = total_and_dead(data['sev24'])
    tot25, dead25 = total_and_dead(data['sev25'])

    data['total_by_year'] = {2022: tot22, 2023: tot23, 2024: tot24, 2025: tot25}
    data['dead_by_year'] = {2022: dead22, 2023: dead23, 2024: dead24, 2025: dead25}
    data['density_by_year'] = DENSITY_BY_YEAR
    return data


# ------------------------------------------------------------
# 차트 1: 로봇밀도 vs 총사고재해자수 양방향 비교 막대그래프
# ------------------------------------------------------------
def make_chart1_robot_density_vs_accidents(data):
    total_by_year = data['total_by_year']
    density_by_year = data['density_by_year']

    years = [2018, 2021, 2022, 2023, 2024, 2025]
    x = np.arange(len(years))
    w = 0.38

    acc_vals = [total_by_year.get(y, np.nan) for y in years]
    den_vals = [density_by_year.get(y, np.nan) for y in years]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    ax1.bar(x - w/2, acc_vals, width=w, color='#4C72B0', label='총 사고재해자수 (요양재해자+사망자)')
    ax2.bar(x + w/2, den_vals, width=w, color='#DD8452', label='로봇밀도 (종업원 1만명당 가동대수)')

    ax1.set_xticks(x)
    ax1.set_xticklabels([str(y) for y in years])
    ax1.set_ylabel('총 사고재해자수 (명)', color='#4C72B0', fontsize=11)
    ax2.set_ylabel('로봇밀도 (대/종업원 1만명)', color='#DD8452', fontsize=11)
    ax1.set_ylim(0, max(v for v in acc_vals if not np.isnan(v)) * 1.25)
    ax2.set_ylim(0, max(v for v in den_vals if not np.isnan(v)) * 1.4)

    for i, v in enumerate(acc_vals):
        if not np.isnan(v):
            ax1.text(x[i]-w/2, v+1500, f'{int(v):,}', ha='center', fontsize=8, color='#4C72B0')
    for i, v in enumerate(den_vals):
        if not np.isnan(v):
            ax2.text(x[i]+w/2, v+15, f'{int(v):,}', ha='center', fontsize=8, color='#DD8452')

    ax1.set_title('로봇 투입(밀도) 증가 vs 산업재해자수 추이 (전산업 합계, 2018~2025)', fontsize=13, pad=15)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1+lines2, labels1+labels2, loc='upper left', fontsize=9, framealpha=0.9)

    fig.text(0.01, -0.03,
              f"출처: 고용노동부 산업재해현황(재해정도별) 2022~2025 / IFR World Robotics 2023~2025\n"
              f"※ 로봇밀도는 2018·2021·2023·2024년만 공개 수치가 존재(그 외 연도는 결측)",
              fontsize=8, color='gray', ha='left')

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, '06_로봇_투입증가vs산업재해자수_추이.png')
    plt.savefig(out_path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"저장됨: {out_path}")


# ------------------------------------------------------------
# 차트 2: 로봇밀도 vs 산업재해 지표 "약한 상관관계" 히트맵
# ------------------------------------------------------------
def make_chart2_heatmap(data):
    density_by_year = data['density_by_year']
    total_by_year = data['total_by_year']
    dead_by_year = data['dead_by_year']

    years = [2018, 2021, 2022, 2023, 2024, 2025]
    metrics = ['로봇밀도\n(대/종업원1만명)', '총 사고재해자수\n(명)', '사고 사망자수\n(명)']

    raw = np.full((3, len(years)), np.nan)
    for j, y in enumerate(years):
        raw[0, j] = density_by_year.get(y, np.nan)
        raw[1, j] = total_by_year.get(y, np.nan)
        raw[2, j] = dead_by_year.get(y, np.nan)

    norm = np.full_like(raw, np.nan)
    for i in range(3):
        row = raw[i]
        valid = row[~np.isnan(row)]
        lo, hi = valid.min(), valid.max()
        norm[i] = (row - lo) / (hi - lo) if hi > lo else 0.5

    fig, ax = plt.subplots(figsize=(10, 4.2))
    masked = np.ma.masked_invalid(norm)
    cmap = plt.cm.RdYlGn_r
    cmap.set_bad(color='#eeeeee')
    ax.imshow(masked, cmap=cmap, aspect='auto', vmin=0, vmax=1)

    ax.set_xticks(range(len(years)))
    ax.set_xticklabels([str(y) for y in years], fontsize=10)
    ax.set_yticks(range(3))
    ax.set_yticklabels(metrics, fontsize=10)

    for i in range(3):
        for j in range(len(years)):
            v = raw[i, j]
            if not np.isnan(v):
                txt_color = 'white' if (norm[i, j] > 0.65 or norm[i, j] < 0.2) else 'black'
                ax.text(j, i, f'{int(v):,}', ha='center', va='center', fontsize=9.5,
                        color=txt_color, fontweight='bold')
            else:
                ax.text(j, i, '결측', ha='center', va='center', fontsize=8, color='#999999')

    ax.set_title(
        '로봇밀도 증가 vs 산업재해 지표 — "약한 상관관계" 히트맵\n'
        '(행별 정규화: 진한 빨강=해당 지표의 그 시기 최고 수준, 진한 초록=최저 수준)',
        fontsize=11.5, pad=14)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks(np.arange(-.5, len(years), 1), minor=True)
    ax.set_yticks(np.arange(-.5, 3, 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=2)
    ax.tick_params(which='minor', bottom=False, left=False)

    fig.text(0.01, -0.08,
              "출처: 고용노동부 산업재해현황(재해정도별) 2022~2025 / IFR World Robotics 2023~2025\n"
              "※ 로봇밀도는 2018→2021→2023→2024년 계속 상승했지만, 총 재해자수·사망자수는 뚜렷한 하락 없이 등락을 반복\n"
              "  → 국가 단위 집계로는 로봇밀도 증가가 산업재해 감소로 뚜렷하게 이어진다고 보기 어려움",
              fontsize=8.3, color='dimgray', ha='left')

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, '07_로봇밀도_증가vs산업재해_약한_상관관계.png')
    plt.savefig(out_path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"저장됨: {out_path}")


# ------------------------------------------------------------
# 차트 3: 대업종별 사고재해자 발생형태 (부딪힘/끼임/깔림뒤집힘/교통사고)
# ------------------------------------------------------------
def make_chart3_industry_hazard_types(data):
    types = ['부딪힘', '끼임', '깔림.뒤집힘', '사업장내교통사고']
    type_labels = ['부딪힘', '끼임', '깔림·뒤집힘', '사업장내교통사고']

    # 표시할 업종만 지정
    target_industries = [
        '제조업',
        '건설업',
        '운수·창고·통신업'
    ]

    dfs = [data['y23'], data['y24'], data['y25']]

    agg = dfs[0][['대업종'] + types].set_index('대업종').copy()

    for d in dfs[1:]:
        agg = agg.add(
            d[['대업종'] + types].set_index('대업종'),
            fill_value=0
        )

    # 제조업, 건설업, 운수·창고·통신업만 남김
    agg = agg.loc[
        agg.index.intersection(target_industries)
    ]

    agg['total'] = agg.sum(axis=1)
    agg = agg.sort_values('total', ascending=True)

    colors = ['#4C72B0', '#DD8452', '#55A868', '#C44E52']

    fig, ax = plt.subplots(figsize=(10, 5))

    left = np.zeros(len(agg))

    for t, lbl, c in zip(types, type_labels, colors):
        ax.barh(
            agg.index,
            agg[t],
            left=left,
            color=c,
            label=lbl
        )
        left += agg[t].values

    for i, (idx, row) in enumerate(agg.iterrows()):
        ax.text(
            row['total'] + 200,
            i,
            f"{int(row['total']):,}명",
            va='center',
            fontsize=9
        )

    ax.set_xlabel(
        '사고재해자수 (명, 2023~2025년 합산)',
        fontsize=11
    )

    ax.set_title(
        '제조업·건설업·운수·창고·통신업의 사고재해 발생형태\n'
        '(2023~2025년 합산, K-NAVI 대응 대상 유형)',
        fontsize=12.5,
        pad=14
    )

    ax.legend(
        loc='lower right',
        fontsize=10,
        framealpha=0.9
    )

    ax.set_xlim(
        0,
        agg['total'].max() * 1.18
    )

    fig.text(
        0.01,
        -0.03,
        "출처: 고용노동부 산업재해현황(대업종별 발생형태) 2023~2025년 합산\n"
        "※ 제조업·건설업·운수·창고·통신업만 표시",
        fontsize=8,
        color='gray',
        ha='left'
    )

    plt.tight_layout()

    out_path = os.path.join(
        OUT_DIR,
        '05_제조업_건설업_운수창고통신업_사고재해자_발생형태.png'
    )

    plt.savefig(
        out_path,
        bbox_inches='tight',
        facecolor='white'
    )

    plt.close(fig)

    print(f"저장됨: {out_path}")

# ------------------------------------------------------------
# 차트 4 (보너스): 전산업 재해정도 구성비 추이
# ------------------------------------------------------------
def make_chart4_severity_trend(data):
    years = [2022, 2023, 2024, 2025]
    sevs = [data['sev22'], data['sev23'], data['sev24'], data['sev25']]
    cols = ['4~7일', '8~14일', '15~28일', '29~90일', '91~180일', '6개월 이상', '사망자']
    labels = ['4~7일', '8~14일', '15~28일', '29~90일', '91~180일', '6개월 이상 요양', '사망']
    colors = ['#c7e9c0', '#a1d99b', '#74c476', '#fdae6b', '#fd8d3c', '#e6550d', '#a50f15']

    values = np.zeros((len(years), len(cols)))
    for i, s in enumerate(sevs):
        row = s[s['대업종'] == '합계'].iloc[0]
        for j, c in enumerate(cols):
            values[i, j] = row[c]

    shares = values / values.sum(axis=1, keepdims=True) * 100

    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = np.zeros(len(years))
    x = np.arange(len(years))
    for j, (lbl, c) in enumerate(zip(labels, colors)):
        ax.bar(x, shares[:, j], bottom=bottom, color=c, label=lbl, width=0.55)
        bottom += shares[:, j]

    ax.set_xticks(x)
    ax.set_xticklabels([f'{y}년' for y in years])
    ax.set_ylabel('구성비 (%)')
    ax.set_ylim(0, 100)
    ax.set_title('전산업 재해정도(치료기간·사망) 구성비 추이 (2022~2025)', fontsize=13, pad=14)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=4, fontsize=9)

    for i in range(len(years)):
        severe = shares[i, -2] + shares[i, -1]
        ax.text(x[i], 101, f"중대(6개월↑+사망) {severe:.1f}%", ha='center', fontsize=8.5, color='#a50f15')

    fig.text(0.01, -0.02, "출처: 고용노동부 산업재해현황(재해정도별) 2022~2025, 전산업 합계 기준",
              fontsize=8, color='gray', ha='left')

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, '09_전산업_재해_치료기간_추이.png')
    plt.savefig(out_path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"저장됨: {out_path}")


# ------------------------------------------------------------
# 차트 5 (보너스): 업종별 "대상 유형" 비중 추이
# ------------------------------------------------------------
def make_chart5_target_share_trend(data):
    types = ['부딪힘', '끼임', '깔림.뒤집힘', '사업장내교통사고']
    industries = ['건설업', '제조업', '운수·창고·통신업']
    years = [2023, 2024, 2025]
    dfs = {2023: data['y23'], 2024: data['y24'], 2025: data['y25']}

    colors = {'건설업': "#C26A2F", '제조업': "#885DA5",
              '운수·창고·통신업': '#55A868'}

    fig, ax = plt.subplots(figsize=(9, 6))
    for ind in industries:
        shares = []
        for y in years:
            d = dfs[y]
            row = d[d['대업종'] == ind].iloc[0]
            target = row[types].sum()
            shares.append(target / row['합계'] * 100)
        ax.plot(years, shares, marker='o', linewidth=2.5, markersize=8, label=ind, color=colors[ind])
        for x, v in zip(years, shares):
            ax.text(x, v + 0.8, f'{v:.1f}%', ha='center', fontsize=8.5, color=colors[ind])

    ax.set_xticks(years)
    ax.set_ylabel('전체 재해자 중 대상 유형(부딪힘·끼임·깔림뒤집힘·교통사고) 비중 (%)')
    ax.set_title('업종별 "K-NAVI 대응 대상 유형" 비중 추이 (2023~2025)', fontsize=13, pad=14)
    ax.legend(loc='best', fontsize=10)
    ax.grid(axis='y', alpha=0.3)

    fig.text(0.01, -0.03,
              "출처: 고용노동부 산업재해현황(대업종별 발생형태) 2023~2025\n"
              "※ 비중(%) = (부딪힘+끼임+깔림·뒤집힘+사업장내교통사고) ÷ 해당 업종 전체 사고재해자수 × 100",
              fontsize=8, color='gray', ha='left')

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, '08_업종별_대응유형_비중.png')
    plt.savefig(out_path, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"저장됨: {out_path}")


# ------------------------------------------------------------
# 메인 실행부
# ------------------------------------------------------------
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    setup_font()

    print("데이터 로딩 중...")
    data = load_all_data()

    print("차트 1 생성 중 (로봇밀도 vs 사고재해자수)...")
    make_chart1_robot_density_vs_accidents(data)

    print("차트 2 생성 중 (약한 상관관계 히트맵)...")
    make_chart2_heatmap(data)

    print("차트 3 생성 중 (대업종별 발생형태)...")
    make_chart3_industry_hazard_types(data)

    print("차트 4 생성 중 (재해정도 구성비 추이)...")
    make_chart4_severity_trend(data)

    print("차트 5 생성 중 (업종별 대상유형 비중 추이)...")
    make_chart5_target_share_trend(data)

    print(f"\n완료! 모든 이미지는 '{os.path.abspath(OUT_DIR)}' 폴더에 저장되었습니다.")


if __name__ == "__main__":
    main()
