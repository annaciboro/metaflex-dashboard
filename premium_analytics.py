import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Premium Enterprise Color Palette
COLORS = {
    'primary_teal': '#5f8c8c',
    'accent_lime': '#b9c97d',
    'coral': '#e08585',
    'sage': '#8ca68c',
    'neutral_50': '#fafbfc',
    'neutral_100': '#f5f7f9',
    'neutral_200': '#ebeef2',
    'neutral_300': '#dfe3e8',
    'neutral_600': '#6b778c',
    'neutral_800': '#323f52',
    'neutral_900': '#1f2937',
    'white': '#ffffff',
}

def inject_premium_css():
    """Inject premium enterprise CSS styling"""
    st.markdown("""
        <style>
        /* Premium Enterprise Dashboard Styling */

        /* Main container */
        .main .block-container {
            padding: 3rem 4rem !important;
            max-width: 1600px !important;
            background: #fafbfc !important;
        }

        /* Premium metric cards */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%) !important;
            border: 1px solid #ebeef2 !important;
            border-radius: 16px !important;
            padding: 2rem !important;
            box-shadow: 0 4px 12px rgba(31, 41, 55, 0.04),
                        0 1px 3px rgba(31, 41, 55, 0.02) !important;
            transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        [data-testid="metric-container"]:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 12px 24px rgba(31, 41, 55, 0.08),
                        0 4px 8px rgba(31, 41, 55, 0.04) !important;
            border-color: #5f8c8c !important;
        }

        /* Metric labels */
        [data-testid="stMetricLabel"] {
            color: #6b778c !important;
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 1.2px !important;
            margin-bottom: 0.5rem !important;
        }

        /* Metric values */
        [data-testid="stMetricValue"] {
            color: #1f2937 !important;
            font-size: 48px !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            font-family: 'Inter Tight', 'Inter', sans-serif !important;
        }

        /* Add accent line to metric cards */
        [data-testid="metric-container"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #5f8c8c 0%, #b9c97d 100%);
            border-radius: 16px 16px 0 0;
            opacity: 0;
            transition: opacity 300ms ease;
        }

        [data-testid="metric-container"]:hover::before {
            opacity: 1;
        }

        /* Chart containers */
        .chart-container {
            background: white;
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 4px 12px rgba(31, 41, 55, 0.04),
                        0 1px 3px rgba(31, 41, 55, 0.02);
            border: 1px solid #ebeef2;
            margin-bottom: 2rem;
            transition: all 300ms ease;
        }

        .chart-container:hover {
            box-shadow: 0 8px 20px rgba(31, 41, 55, 0.06),
                        0 2px 6px rgba(31, 41, 55, 0.03);
            border-color: #dfe3e8;
        }

        /* Section headers */
        .section-header {
            font-size: 28px;
            font-weight: 800;
            color: #1f2937;
            margin-bottom: 0.5rem;
            letter-spacing: -0.02em;
            font-family: 'Inter Tight', 'Inter', sans-serif;
        }

        .section-subtitle {
            font-size: 15px;
            color: #6b778c;
            margin-bottom: 2.5rem;
            font-weight: 500;
        }

        /* Divider */
        .premium-divider {
            height: 1px;
            background: linear-gradient(90deg,
                transparent 0%,
                #ebeef2 20%,
                #ebeef2 80%,
                transparent 100%);
            margin: 3rem 0;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        </style>
    """, unsafe_allow_html=True)

def create_premium_donut_chart(done_pct, in_progress_pct, open_pct):
    """
    Create a sophisticated donut chart with premium styling
    """
    labels = ['Completed', 'In Progress', 'Not Started']
    values = [done_pct, in_progress_pct, open_pct]
    colors = [COLORS['sage'], COLORS['accent_lime'], COLORS['coral']]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.7,
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=5)
        ),
        textinfo='none',  # Hide text on slices for cleaner look
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<br><extra></extra>',
        direction='clockwise',
        sort=False
    )])

    # Add center annotation with total completion
    total_completion = done_pct + in_progress_pct
    fig.add_annotation(
        text=f'<b style="font-size: 54px; color: {COLORS["neutral_900"]};">{total_completion:.0f}%</b><br><span style="font-size: 16px; color: {COLORS["neutral_600"]}; font-weight: 600;">OVERALL PROGRESS</span>',
        x=0.5, y=0.5,
        font=dict(size=20, family='Inter'),
        showarrow=False,
        align='center'
    )

    # Premium layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color=COLORS['neutral_600'], family='Inter', weight=600),
            itemsizing='constant'
        ),
        height=450,
        margin=dict(t=40, b=60, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, -apple-system, sans-serif')
    )

    return fig

def create_premium_bar_chart(projects, counts):
    """
    Create a sophisticated horizontal bar chart with rounded corners
    """
    # Create gradient colors for bars
    max_count = max(counts)
    bar_colors = []
    for count in counts:
        intensity = count / max_count
        # Interpolate between light teal and primary teal
        bar_colors.append(f'rgba(95, 140, 140, {0.3 + intensity * 0.5})')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color=COLORS['primary_teal'], width=2),
            cornerradius=8  # Rounded corners
        ),
        text=[f'<b>{count}</b>' for count in counts],
        textposition='outside',
        textfont=dict(
            size=16,
            color=COLORS['neutral_900'],
            family='Inter',
            weight=700
        ),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<br><extra></extra>',
        width=0.6  # Slimmer bars for modern look
    ))

    # Premium layout
    fig.update_layout(
        height=400,
        margin=dict(t=20, b=20, l=20, r=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(235, 238, 242, 0.6)',
            gridwidth=1,
            zeroline=False,
            title='',
            tickfont=dict(size=13, color=COLORS['neutral_600'], family='Inter'),
            range=[0, max(counts) * 1.15]  # Add space for text
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=15, color=COLORS['neutral_900'], family='Inter', weight=600),
            showgrid=False
        ),
        font=dict(family='Inter, -apple-system, sans-serif'),
        bargap=0.3
    )

    return fig

def render_metric_card(label, value, icon="📊"):
    """Render a premium metric card"""
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown(f"<div style='font-size: 36px; opacity: 0.6;'>{icon}</div>", unsafe_allow_html=True)
    with col2:
        st.metric(label=label, value=value)

def main():
    st.set_page_config(
        page_title="Analytics Dashboard - MetaFlex",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Inject premium CSS
    inject_premium_css()

    # Header
    st.markdown('<h1 class="section-header">Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Real-time insights into team performance and project progress</p>', unsafe_allow_html=True)

    # Metrics Row
    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
        st.metric(
            label="My Open Tasks",
            value="27"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
        st.metric(
            label="Team Open Tasks",
            value="45"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div style="position: relative;">', unsafe_allow_html=True)
        st.metric(
            label="Active Projects",
            value="3"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Divider
    st.markdown('<div class="premium-divider"></div>', unsafe_allow_html=True)

    # Charts Section
    st.markdown('<h2 class="section-header">Performance Overview</h2>', unsafe_allow_html=True)
    st.markdown('<p class="section-subtitle">Track completion rates and project distribution</p>', unsafe_allow_html=True)

    # Charts in 2 columns with generous spacing
    chart_col1, chart_spacer, chart_col2 = st.columns([10, 1, 10])

    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 20px; font-weight: 700; color: #1f2937; margin-bottom: 1.5rem;">Task Completion Status</h3>', unsafe_allow_html=True)

        # Donut chart data
        donut_fig = create_premium_donut_chart(
            done_pct=77.6,
            in_progress_pct=17.24,
            open_pct=5.17
        )
        st.plotly_chart(donut_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-size: 20px; font-weight: 700; color: #1f2937; margin-bottom: 1.5rem;">Tasks by Project</h3>', unsafe_allow_html=True)

        # Bar chart data
        projects = ['General', 'Products', 'Marketing']
        counts = [14, 20, 24]

        bar_fig = create_premium_bar_chart(projects, counts)
        st.plotly_chart(bar_fig, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # Bottom spacing
    st.markdown('<div style="height: 3rem;"></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
