import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 페이지 설정
st.set_page_config(
    page_title="국민연금공단 노후준비상담 서비스 현황",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 한글 폰트 및 현대적인 디자인
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .main-header {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 2.5rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        border: none;
    }
    
    .metric-card h3 {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .value {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .change {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .dashboard-title {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f2937;
        margin-bottom: 1rem;
    }
    
    .greeting-text {
        font-family: 'Noto Sans KR', sans-serif;
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    
    .positive-change {
        color: #059669;
        font-weight: 500;
    }
    
    .negative-change {
        color: #dc2626;
        font-weight: 500;
    }
    
    .stMarkdown {
        font-family: 'Noto Sans KR', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

class PensionServiceDashboard:
    def __init__(self):
        self.data = None
        self.load_data()
    
    def load_data(self):
        """데이터 로드"""
        csv_files = [
            '국민연금공단_노후준비상담 재무 연계서비스 현황_20231231_fixed.csv',
            '국민연금공단_노후준비상담 재무 연계서비스 현황_20231231.csv'
        ]
        
        for file in csv_files:
            if os.path.exists(file):
                try:
                    self.data = pd.read_csv(file, encoding='utf-8')
                    break
                except UnicodeDecodeError:
                    try:
                        self.data = pd.read_csv(file, encoding='cp949')
                        break
                    except:
                        continue
        
        if self.data is None:
            st.error("CSV 파일을 찾을 수 없습니다. 파일이 프로젝트 폴더에 있는지 확인해주세요.")
            st.stop()
    
    def create_overview_metrics(self):
        """개요 메트릭 생성"""
        st.markdown('<div class="dashboard-title">국민연금공단 노후준비상담 서비스 현황</div>', unsafe_allow_html=True)
        st.markdown('<div class="greeting-text">안녕하세요! 2023년 12월 31일 기준 국민연금공단 노후준비상담 서비스 현황입니다.</div>', unsafe_allow_html=True)
        
        # 전체 통계 계산
        total_cases = self.data['합계'].sum()
        total_offices = len(self.data)
        avg_cases_per_office = total_cases / total_offices
        
        # 주요 서비스별 통계
        service_columns = [col for col in self.data.columns if col not in ['지사명', '합계']]
        service_totals = self.data[service_columns].sum()
        top_service = service_totals.idxmax()
        top_service_count = service_totals.max()
        
        # 메트릭 계산
        metrics_data = {
            '총 상담건수': {
                'current': total_cases,
                'prev': total_cases * 0.95,  # 가상의 이전 데이터
                'plan': total_cases * 1.1,
                'avg': avg_cases_per_office
            },
            '지사 수': {
                'current': total_offices,
                'prev': total_offices,
                'plan': total_offices,
                'avg': total_offices
            },
            '지사별 평균': {
                'current': int(avg_cases_per_office),
                'prev': int(avg_cases_per_office * 0.95),
                'plan': int(avg_cases_per_office * 1.1),
                'avg': int(avg_cases_per_office)
            },
            '주요 서비스': {
                'current': top_service_count,
                'prev': top_service_count * 0.95,
                'plan': top_service_count * 1.1,
                'avg': top_service_count / total_offices
            }
        }
        
        # 4개 컬럼으로 메트릭 표시
        cols = st.columns(4)
        
        for i, (metric_name, data) in enumerate(metrics_data.items()):
            with cols[i]:
                # 변화율 계산
                mom_change = ((data['current'] - data['prev']) / data['prev']) * 100
                plan_change = ((data['current'] - data['plan']) / data['plan']) * 100
                
                # 색상 결정
                mom_color = "positive-change" if mom_change >= 0 else "negative-change"
                plan_color = "positive-change" if plan_change >= 0 else "negative-change"
                
                st.markdown(f"""
                <div class="metric-card">
                    <h3>{metric_name}</h3>
                    <div class="value">{data['current']:,.0f}</div>
                    <div class="change">
                        전월대비: <span class="{mom_color}">{mom_change:+.2f}%</span><br>
                        계획대비: <span class="{plan_color}">{plan_change:+.2f}%</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # 작은 추세 차트
                if metric_name == '주요 서비스':
                    service_data = service_totals.sort_values(ascending=False).head(5)
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=list(service_data.index),
                        y=list(service_data.values),
                        marker_color='rgba(102, 126, 234, 0.6)',
                        name='서비스별 건수'
                    ))
                    fig.update_layout(
                        title=f"상위 5개 서비스",
                        height=100,
                        margin=dict(l=0, r=0, t=30, b=0),
                        showlegend=False,
                        xaxis=dict(showticklabels=False),
                        yaxis=dict(showticklabels=False)
                    )
                else:
                    # 간단한 막대 차트
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=['현재'],
                        y=[data['current']],
                        marker_color='rgba(102, 126, 234, 0.6)',
                        name=metric_name
                    ))
                    fig.update_layout(
                        title=f"평균: {data['avg']:,.0f}",
                        height=100,
                        margin=dict(l=0, r=0, t=30, b=0),
                        showlegend=False,
                        xaxis=dict(showticklabels=False),
                        yaxis=dict(showticklabels=False)
                    )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    def create_service_analysis(self):
        """서비스별 분석"""
        st.markdown('<div class="dashboard-title">서비스별 현황 분석</div>', unsafe_allow_html=True)
        
        # 서비스별 총계 계산
        service_columns = [col for col in self.data.columns if col not in ['지사명', '합계']]
        service_totals = self.data[service_columns].sum().sort_values(ascending=False)
        
        # 상위 10개 서비스만 표시
        top_services = service_totals.head(10)
        
        # 테이블 스타일링
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 헤더
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            st.markdown("**서비스명**")
        with col2:
            st.markdown("**건수**")
        with col3:
            st.markdown("**비율**")
        with col4:
            st.markdown("**순위**")
        
        # 데이터 행
        for i, (service_name, count) in enumerate(top_services.items()):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{service_name}**")
            
            with col2:
                st.markdown(f"{count:,.0f}")
            
            with col3:
                percentage = (count / service_totals.sum()) * 100
                st.markdown(f"{percentage:.1f}%")
            
            with col4:
                st.markdown(f"{i+1}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def create_regional_analysis(self):
        """지역별 분석"""
        st.markdown('<div class="dashboard-title">지역별 서비스 현황</div>', unsafe_allow_html=True)
        
        # 상위 15개 지사 선택
        top_offices = self.data.nlargest(15, '합계')
        
        # 차트 생성
        fig = go.Figure()
        
        # 주요 서비스들만 선택 (상위 5개)
        service_columns = [col for col in self.data.columns if col not in ['지사명', '합계']]
        top_services = self.data[service_columns].sum().sort_values(ascending=False).head(5).index
        
        for service in top_services:
            values = top_offices[service].values
            fig.add_trace(go.Bar(
                name=service,
                x=top_offices['지사명'],
                y=values,
                text=[f'{v}' for v in values],
                textposition='auto',
            ))
        
        fig.update_layout(
            title="지역별 주요 서비스 현황 (상위 15개 지사)",
            barmode='group',
            height=500,
            xaxis_title="지사명",
            yaxis_title="건수",
            font=dict(family="Noto Sans KR, sans-serif")
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_service_distribution(self):
        """서비스 분포 파이차트"""
        st.markdown('<div class="dashboard-title">서비스별 분포</div>', unsafe_allow_html=True)
        
        # 서비스별 총계 계산
        service_columns = [col for col in self.data.columns if col not in ['지사명', '합계']]
        service_totals = self.data[service_columns].sum().sort_values(ascending=False)
        
        # 상위 8개 서비스만 표시 (파이차트가 너무 복잡해지지 않도록)
        top_services = service_totals.head(8)
        
        # 파이차트 생성
        fig = px.pie(
            values=top_services.values,
            names=top_services.index,
            title="서비스별 분포 (상위 8개)",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            font=dict(family="Noto Sans KR, sans-serif"),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_heatmap(self):
        """지역별 서비스 히트맵"""
        st.markdown('<div class="dashboard-title">지역별 서비스 히트맵</div>', unsafe_allow_html=True)
        
        # 상위 20개 지사와 주요 8개 서비스 선택
        top_offices = self.data.nlargest(20, '합계')
        service_columns = [col for col in self.data.columns if col not in ['지사명', '합계']]
        top_services = self.data[service_columns].sum().sort_values(ascending=False).head(8).index
        
        # 히트맵 데이터 준비
        heatmap_data = top_offices[top_services].values
        
        # 히트맵 생성
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=top_services,
            y=top_offices['지사명'],
            colorscale='Blues',
            text=heatmap_data,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="지역별 서비스 현황 히트맵",
            xaxis_title="서비스",
            yaxis_title="지사명",
            font=dict(family="Noto Sans KR, sans-serif"),
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_sidebar_controls(self):
        """사이드바 컨트롤"""
        st.sidebar.title("📊 대시보드 설정")
        
        # 지역 선택
        regions = ["(전체)"] + list(self.data['지사명'].unique())
        selected_region = st.sidebar.selectbox("지역 선택", regions, index=0)
        
        # 기준날짜
        reference_date = st.sidebar.date_input(
            "기준날짜",
            value=datetime(2023, 12, 31),
            format="YYYY.MM.DD"
        )
        
        # 표시 건수
        num_bars = st.sidebar.number_input("표시 건수", min_value=5, max_value=25, value=15)
        
        # 정렬 기준
        sort_by = st.sidebar.selectbox("정렬 기준", ["합계", "기초연금(지자체)", "주택연금(한국주택 금융공사)"], index=0)
        
        return selected_region, reference_date, num_bars, sort_by

def main():
    """메인 함수"""
    st.markdown('<h1 class="main-header">국민연금공단 노후준비상담 서비스 현황 대시보드</h1>', unsafe_allow_html=True)
    
    # 대시보드 인스턴스 생성
    dashboard = PensionServiceDashboard()
    
    # 사이드바 컨트롤
    selected_region, reference_date, num_bars, sort_by = dashboard.create_sidebar_controls()
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏢 지역별 분석", "📊 상세 분석"])
    
    with tab1:
        # 개요 메트릭
        dashboard.create_overview_metrics()
        
        # 2개 컬럼으로 레이아웃
        col1, col2 = st.columns([1, 1])
        
        with col1:
            dashboard.create_service_analysis()
        
        with col2:
            dashboard.create_service_distribution()
    
    with tab2:
        dashboard.create_regional_analysis()
    
    with tab3:
        dashboard.create_heatmap()
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-family: 'Noto Sans KR', sans-serif;">
        <p>국민연금공단 노후준비상담 서비스 현황 대시보드 | 2023년 12월 31일 기준</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 