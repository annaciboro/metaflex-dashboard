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
    Premium donut chart with sophisticated styling and percentages on each slice
    """
    total_tasks = open_tasks + working_tasks + done_tasks

    if total_tasks == 0:
        st.info("No tasks to display in chart.")
        return None

    # Premium sophisticated colors
    colors = ['#e08585', '#b9c97d', '#8ca68c']  # Coral (open), Lime (in progress), Sage (done)

    # Create donut chart with percentages on slices
    fig = go.Figure(data=[go.Pie(
        labels=['Not Started', 'In Progress', 'Completed'],
        values=[open_tasks, working_tasks, done_tasks],
        hole=0.7,  # Larger hole for modern look
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=5)  # Thicker white lines for separation
        ),
        textinfo='percent',  # Show percentages on each slice
        textfont=dict(size=15, color='#1f2937', family='Inter', weight=600),
        textposition='inside',
        insidetextorientation='horizontal',
        hovertemplate='<b>%{label}</b><br>Tasks: %{value}<br>Percentage: %{percent}<extra></extra>',
        direction='clockwise',
        sort=False
    )])

    # Calculate overall progress
    overall_progress = int((working_tasks + done_tasks) / total_tasks * 100) if total_tasks > 0 else 0

    # Add center text showing overall progress
    fig.add_annotation(
        text=f'<b style="font-size: 54px; color: #1f2937;">{overall_progress}%</b><br><span style="font-size: 16px; color: #6b778c; font-weight: 600;">OVERALL PROGRESS</span>',
        x=0.5, y=0.5,
        font=dict(size=20, color='#1f2937', family='Inter'),
        showarrow=False,
        align='center'
    )

    # Premium white background layout
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=14, color='#6b778c', family='Inter', weight=600),
            itemsizing='constant'
        ),
        height=450,
        margin=dict(t=40, b=60, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, -apple-system, sans-serif')
    )

    return fig


def create_project_breakdown_chart(df):
    """
    Premium horizontal bar chart with rounded corners and sophisticated styling
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

    # Create gradient colors based on value intensity
    max_count = max(counts)
    bar_colors = []
    for count in counts:
        intensity = count / max_count
        # Interpolate opacity for sophisticated gradient effect
        bar_colors.append(f'rgba(95, 140, 140, {0.3 + intensity * 0.5})')

    # Create horizontal bar chart with rounded corners
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=bar_colors,  # Gradient based on value
            line=dict(color='#5f8c8c', width=2),  # Primary teal border
            cornerradius=8  # Rounded corners for modern look
        ),
        text=[f'<b>{count}</b>' for count in counts],
        textposition='outside',
        textfont=dict(size=16, color='#1f2937', family='Inter', weight=700),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>',
        width=0.6  # Slimmer bars for premium look
    )])

    # Premium white background layout
    fig.update_layout(
        height=400,
        margin=dict(t=20, b=20, l=20, r=80),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(235, 238, 242, 0.6)',  # Subtle grid
            gridwidth=1,
            zeroline=False,
            title='',
            tickfont=dict(size=13, color='#6b778c', family='Inter'),
            range=[0, max(counts) * 1.15]  # Extra space for text labels
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=15, color='#1f2937', family='Inter', weight=600),
            showgrid=False
        ),
        font=dict(family='Inter, -apple-system, sans-serif'),
        bargap=0.3
    )

    return fig