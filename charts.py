import plotly.graph_objects as go
import streamlit as st

# MetaFlex Luxury chart palette - Premium dark theme
MF_COLORS = {
    'primary': '#0a9aaa',      # Deep cyan - primary interactive
    'secondary': '#b8935f',    # Refined gold - premium accents
    'accent': '#d4ff00',       # Lime - power moments (use sparingly)
    'emerald': '#2d7d70',      # Muted emerald - success states
    'warning': '#a87e3f',      # Warm warning
    'error': '#8b4444',        # Subtle error
    'text': '#f6f7fb',         # Platinum text
    'text_secondary': '#b8bfd4', # Muted secondary text
    'background': '#1a1f3a',   # Graphite background
    'muted': 'rgba(255,255,255,0.05)'  # Subtle borders/dividers
}

def create_team_completion_donut(open_tasks, working_tasks, done_tasks):
    """
    Create a donut chart showing team task completion breakdown
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
            colors=[MF_COLORS['error'], MF_COLORS['warning'], MF_COLORS['emerald']],
            line=dict(color=MF_COLORS['text'], width=1)
        ),
        textinfo='label+percent',
        textfont=dict(size=14, color=MF_COLORS['text'], family='Inter'),
        hovertemplate='<b>%{label}</b><br>Tasks: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    # Add center text showing total tasks
    fig.add_annotation(
        text=f'<b>{total_tasks}</b><br>Total Tasks',
        x=0.5, y=0.5,
        font=dict(size=24, color=MF_COLORS['text'], family='Outfit'),
        showarrow=False
    )

    # Update layout with luxury dark theme
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=MF_COLORS['text'])
        ),
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='<b>Team Task Completion</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_COLORS['text'], family='Outfit')
        )
    )
    
    return fig


def create_project_breakdown_chart(df):
    """
    Create a horizontal bar chart showing task breakdown by project
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
    
    # Create horizontal bar chart with luxury styling
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=MF_COLORS['primary'],
            line=dict(color=MF_COLORS['secondary'], width=1)
        ),
        text=counts,
        textposition='outside',
        textfont=dict(size=14, color=MF_COLORS['text'], family='IBM Plex Mono'),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>'
    )])
    
    # Update layout with luxury dark theme
    fig.update_layout(
        height=400,
        margin=dict(t=40, b=40, l=120, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor=MF_COLORS['muted'],
            title='Number of Tasks',
            titlefont=dict(size=12, color=MF_COLORS['text_secondary']),
            tickfont=dict(size=11, color=MF_COLORS['text'])
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_COLORS['text'])
        ),
        title=dict(
            text='<b>Tasks by Project</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_COLORS['text'], family='Outfit')
        )
    )
    
    return fig
