import plotly.graph_objects as go
import streamlit as st
import re

# MetaFlex chart palette and typography
MF_COLORS = {
    'chart1': '#137a67',  # deep green
    'chart2': '#2aa76a',
    'chart3': '#c8ee33',  # accent lime
    'text': '#0f5b52',
    'muted': 'rgba(15,91,82,0.12)'
}

def get_column(df, col_name):
    """
    Helper function to get a column by its original name, even if it has a unique suffix.
    Returns the column name with the suffix that exists in the DataFrame.
    """
    # First try exact match
    if col_name in df.columns:
        return col_name

    # Try to find column with ___ suffix
    matching_cols = [col for col in df.columns if col.startswith(f"{col_name}___")]
    if matching_cols:
        return matching_cols[0]  # Return the first match

    # Fallback: return the original name (will cause KeyError if doesn't exist)
    return col_name

def has_column(df, col_name):
    """Check if a column exists by original name"""
    if col_name in df.columns:
        return True
    return any(col.startswith(f"{col_name}___") for col in df.columns)

def create_team_completion_donut(open_tasks, working_tasks, done_tasks):
    """
    Create a donut chart showing team task completion breakdown
    Uses red, yellow, green color scheme to match progress dots
    """
    total_tasks = open_tasks + working_tasks + done_tasks

    if total_tasks == 0:
        st.info("No tasks to display in chart.")
        return None

    # Red, Yellow, Green color scheme to match progress dots
    colors = ['#ef4444', '#fbbf24', '#22c55e']  # Red, Yellow/Orange, Green

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=['Open', 'In Progress', 'Done'],
        values=[open_tasks, working_tasks, done_tasks],
        hole=0.6,
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=15, color='#1f2937', family='Inter', weight='bold'),
        hovertemplate='<b>%{label}</b><br>Tasks: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])

    # Add center text showing total tasks with better contrast
    fig.add_annotation(
        text=f'<b style="font-size: 32px;">{total_tasks}</b><br><span style="font-size: 14px;">Total Tasks</span>',
        x=0.5, y=0.5,
        font=dict(size=18, color='#1f2937', family='Inter'),
        showarrow=False
    )

    # Update layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.18,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color='#1f2937', weight='bold')
        ),
        height=400,
        margin=dict(t=40, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text='<b>Team Task Completion</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color='#1f2937', family='Inter')
        )
    )

    return fig


def create_project_breakdown_chart(df):
    """
    Create a horizontal bar chart showing task breakdown by project
    """
    if df.empty or not has_column(df, "Project"):
        st.info("No project data available.")
        return None

    # Get the actual column name (with suffix if it exists)
    project_col = get_column(df, "Project")

    # Count tasks by project
    project_counts = df[project_col].str.lower().str.strip().value_counts()
    
    if project_counts.empty:
        st.info("No project data to display.")
        return None
    
    # Title case for display
    projects = [p.title() for p in project_counts.index]
    counts = project_counts.values
    
    # Create horizontal bar chart
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=MF_COLORS['chart1'],
            line=dict(color=MF_COLORS['chart3'], width=2)
        ),
        text=counts,
        textposition='outside',
        textfont=dict(size=14, color=MF_COLORS['text'], family='Inter'),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>'
    )])
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(t=40, b=40, l=120, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor=MF_COLORS['muted'],
            title=dict(
                text='Number of Tasks',
                font=dict(size=12, color=MF_COLORS['text'])
            ),
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
            font=dict(size=18, color=MF_COLORS['text'], family='Inter')
        )
    )
    
    return fig