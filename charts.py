import plotly.graph_objects as go
import streamlit as st

# MetaFlex Luxury Chart Palette - Phase 1
# Dark theme with restrained accents for premium SaaS experience
MF_COLORS = {
    'primary-dark': '#0a0e27',      # Dark charcoal canvas
    'primary-surface': '#1a1f3a',   # Refined graphite surfaces
    'accent-cyan': '#0a9aaa',       # Primary interactive - premium tech feel
    'accent-lime': '#d4ff00',       # Reserved for critical metrics only (power moments)
    'accent-gold': '#b8935f',       # Premium tier features
    'text-primary': '#f6f7fb',      # Soft platinum - readable on dark
    'status-success': '#2d7d70',    # Muted emerald
    'status-warning': '#a87e3f',    # Warm amber
    'status-error': '#8b4444',      # Subtle red
    'muted': 'rgba(10, 154, 170, 0.1)'  # Soft cyan for grid
}

def create_team_completion_donut(open_tasks, working_tasks, done_tasks):
    """
    Create a donut chart showing team task completion breakdown
    Uses luxury color palette: cyan for open, lime for in progress, emerald for done
    """
    total_tasks = open_tasks + working_tasks + done_tasks
    
    if total_tasks == 0:
        st.info("No tasks to display in chart.")
        return None
    
    # Create donut chart with luxury colors
    fig = go.Figure(data=[go.Pie(
        labels=['Open', 'In Progress', 'Done'],
        values=[open_tasks, working_tasks, done_tasks],
        hole=0.6,
        marker=dict(
            colors=[
                MF_COLORS['accent-cyan'],   # Open → cyan
                MF_COLORS['accent-lime'],   # In Progress → lime (power moment)
                MF_COLORS['status-success']  # Done → emerald
            ],
            line=dict(color=MF_COLORS['text-primary'], width=2)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color=MF_COLORS['text-primary'], family='Inter'),
        hovertemplate='<b>%{label}</b><br>Tasks: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Add center text showing total tasks
    fig.add_annotation(
        text=f'<b>{total_tasks}</b><br>Total Tasks',
        x=0.5, y=0.5,
        font=dict(size=24, color=MF_COLORS['text-primary'], family='Inter'),
        showarrow=False
    )
    
    # Update layout with dark theme
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=MF_COLORS['text-primary'])
        ),
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor=MF_COLORS['primary-dark'],  # Dark background
        plot_bgcolor=MF_COLORS['primary-surface'],  # Slightly lighter surface
        title=dict(
            text='<b>Team Task Completion</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_COLORS['text-primary'], family='Inter')
        )
    )
    
    return fig


def create_project_breakdown_chart(df):
    """
    Create a horizontal bar chart showing task breakdown by project
    Uses luxury accent colors with dark theme
    """
    if df.empty or "Project" not in df.columns:
        st.info("No project data available.")
        return None
    
    # Count tasks by project
    project_counts = df["Project"].str.lower().str.strip().value_counts()
    
    if project_counts.empty:
        st.info("No project data to display.")
        return None
    
    # Title case for display
    projects = [p.title() for p in project_counts.index]
    counts = project_counts.values
    
    # Create horizontal bar chart with luxury colors
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=MF_COLORS['accent-cyan'],  # Primary bars in cyan
            line=dict(color=MF_COLORS['accent-gold'], width=2)  # Gold accent border
        ),
        text=counts,
        textposition='outside',
        textfont=dict(size=14, color=MF_COLORS['text-primary'], family='Inter'),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>'
    )])
    
    # Update layout with dark theme
    fig.update_layout(
        height=400,
        margin=dict(t=40, b=40, l=120, r=40),
        paper_bgcolor=MF_COLORS['primary-dark'],  # Dark background
        plot_bgcolor=MF_COLORS['primary-surface'],  # Slightly lighter surface
        xaxis=dict(
            showgrid=True,
            gridcolor=MF_COLORS['muted'],
            title='Number of Tasks',
            titlefont=dict(size=12, color=MF_COLORS['text-primary']),
            tickfont=dict(size=11, color=MF_COLORS['text-primary'])
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_COLORS['text-primary'])
        ),
        title=dict(
            text='<b>Tasks by Project</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_COLORS['text-primary'], family='Inter')
        )
    )
    
    return fig