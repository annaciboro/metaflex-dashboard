import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# MetaFlex Dark Theme Palette
MF_DARK = {
    'bg_dark': '#0a2f2f',        # Deep dark teal canvas
    'bg_surface': '#0d3a3a',     # Dark teal surface
    'border': '#2d5016',         # Dark forest green border
    'accent_lime': '#d4ff00',    # Neon lime accent
    'text_light': '#e8f5e9',     # Light text for readability
    'text_dark': '#2d5016',      # Dark green text
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


def create_team_performance_metrics(exec_metrics):
    """
    Team Performance Metrics with dark theme
    Shows completion rate per team member
    """
    person_data = []
    for person, metrics in exec_metrics["tasks_by_person"].items():
        total = metrics["total"]
        complete = metrics["complete"]
        completion_rate = int((complete / total * 100)) if total > 0 else 0
        person_data.append({
            "Team Member": person,
            "Completion Rate": completion_rate
        })

    if not person_data:
        st.info("No team performance data available.")
        return None

    person_df = pd.DataFrame(person_data).sort_values("Completion Rate", ascending=True)

    fig = go.Figure(data=[go.Bar(
        y=person_df["Team Member"],
        x=person_df["Completion Rate"],
        orientation='h',
        marker=dict(
            color=MF_DARK['accent_lime'],
            line=dict(color=MF_DARK['border'], width=2)
        ),
        text=[f"{rate}%" for rate in person_df["Completion Rate"]],
        textposition='outside',
        textfont=dict(size=14, color=MF_DARK['text_light'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Completion: %{x}%<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='<b>Team Performance Metrics</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_DARK['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=120, r=60),
        paper_bgcolor=MF_DARK['bg_dark'],
        plot_bgcolor=MF_DARK['bg_surface'],
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(212, 255, 0, 0.1)',
            title='Completion Rate (%)',
            titlefont=dict(size=12, color=MF_DARK['text_light']),
            tickfont=dict(size=11, color=MF_DARK['text_light']),
            range=[0, 110]
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_DARK['text_light'])
        )
    )

    return fig


def create_task_age_analysis(df):
    """
    Task Age Analysis with dark theme
    Shows how long tasks have been open
    """
    if df.empty:
        st.info("No task age data available.")
        return None

    # Calculate task ages (mock data for now - would need Created Date column)
    age_ranges = {
        '0-7 days': 0,
        '8-14 days': 0,
        '15-30 days': 0,
        '30+ days': 0
    }

    # Mock calculation - in real implementation would parse Created Date
    import random
    total_tasks = len(df)
    age_ranges['0-7 days'] = int(total_tasks * 0.4)
    age_ranges['8-14 days'] = int(total_tasks * 0.3)
    age_ranges['15-30 days'] = int(total_tasks * 0.2)
    age_ranges['30+ days'] = total_tasks - sum([age_ranges['0-7 days'], age_ranges['8-14 days'], age_ranges['15-30 days']])

    labels = list(age_ranges.keys())
    values = list(age_ranges.values())

    colors = ['#d4ff00', '#a8cc00', '#7a9900', '#4d6600']

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color=MF_DARK['border'], width=2)
        ),
        text=values,
        textposition='outside',
        textfont=dict(size=14, color=MF_DARK['text_light'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{x}</b><br>Tasks: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='<b>Task Age Analysis</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_DARK['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        paper_bgcolor=MF_DARK['bg_dark'],
        plot_bgcolor=MF_DARK['bg_surface'],
        xaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_DARK['text_light'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(212, 255, 0, 0.1)',
            title='Number of Tasks',
            titlefont=dict(size=12, color=MF_DARK['text_light']),
            tickfont=dict(size=11, color=MF_DARK['text_light'])
        )
    )

    return fig


def create_task_completion_velocity(exec_metrics):
    """
    Task Completion Velocity with dark theme
    Shows tasks completed over time (last 7 days)
    """
    # Mock data - in real implementation would use actual completion dates
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    completed_counts = [3, 5, 2, 7, 4, 1, 6]  # Mock data

    fig = go.Figure(data=[go.Scatter(
        x=days,
        y=completed_counts,
        mode='lines+markers',
        line=dict(color=MF_DARK['accent_lime'], width=3),
        marker=dict(
            size=10,
            color=MF_DARK['accent_lime'],
            line=dict(color=MF_DARK['border'], width=2)
        ),
        fill='tozeroy',
        fillcolor='rgba(212, 255, 0, 0.2)',
        hovertemplate='<b>%{x}</b><br>Completed: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='<b>Task Completion Velocity</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_DARK['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        paper_bgcolor=MF_DARK['bg_dark'],
        plot_bgcolor=MF_DARK['bg_surface'],
        xaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_DARK['text_light']),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(212, 255, 0, 0.1)',
            title='Tasks Completed',
            titlefont=dict(size=12, color=MF_DARK['text_light']),
            tickfont=dict(size=11, color=MF_DARK['text_light'])
        )
    )

    return fig


def create_project_health_dashboard(exec_metrics):
    """
    Project Health Dashboard with dark theme
    Shows project completion rates
    """
    project_data = []
    for project, metrics in exec_metrics["tasks_by_project"].items():
        total = metrics["total"]
        complete = metrics["complete"]
        in_progress = metrics["in_progress"]
        open_tasks = metrics["open"]
        health_score = int((complete + (in_progress * 0.5)) / total * 100) if total > 0 else 0

        project_data.append({
            "Project": project,
            "Health Score": health_score,
            "Total": total
        })

    if not project_data:
        st.info("No project health data available.")
        return None

    project_df = pd.DataFrame(project_data).sort_values("Health Score", ascending=True)

    # Color code by health score
    colors = []
    for score in project_df["Health Score"]:
        if score >= 75:
            colors.append('#d4ff00')  # Healthy - lime
        elif score >= 50:
            colors.append('#7a9900')  # Warning - darker lime
        else:
            colors.append('#4d6600')  # At risk - dark green

    fig = go.Figure(data=[go.Bar(
        y=project_df["Project"],
        x=project_df["Health Score"],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=MF_DARK['border'], width=2)
        ),
        text=[f"{score}%" for score in project_df["Health Score"]],
        textposition='outside',
        textfont=dict(size=14, color=MF_DARK['text_light'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Health: %{x}%<br>Total Tasks: %{customdata}<extra></extra>',
        customdata=project_df["Total"]
    )])

    fig.update_layout(
        title=dict(
            text='<b>Project Health Dashboard</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_DARK['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=140, r=60),
        paper_bgcolor=MF_DARK['bg_dark'],
        plot_bgcolor=MF_DARK['bg_surface'],
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(212, 255, 0, 0.1)',
            title='Health Score (%)',
            titlefont=dict(size=12, color=MF_DARK['text_light']),
            tickfont=dict(size=11, color=MF_DARK['text_light']),
            range=[0, 110]
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_DARK['text_light'])
        )
    )

    return fig


def create_team_completion_donut(open_tasks, working_tasks, done_tasks):
    """
    Premium donut chart with sophisticated styling and percentages on each slice
    """
    total_tasks = open_tasks + working_tasks + done_tasks

    if total_tasks == 0:
        st.info("No tasks to display in chart.")
        return None

    # Muted coral, amber, forest colors
    colors = ['#d17a6f', '#e8b968', '#4d7a40']  # Coral (not started), Amber (in progress), Forest (completed)

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
        textfont=dict(size=13, color='#ffffff', family='-apple-system, sans-serif', weight=700),
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
        text=f'<b style="font-size: 40px; color: #2d5016; font-weight: 900;">{overall_progress}%</b><br><span style="font-size: 12px; color: #2d5016; font-weight: 600;">OVERALL PROGRESS</span>',
        x=0.5, y=0.5,
        font=dict(size=16, color='#2d5016', family='-apple-system, sans-serif'),
        showarrow=False,
        align='center'
    )

    # Compact layout with smaller height
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color='#2d5016', family='-apple-system, sans-serif', weight=700),
            itemsizing='constant'
        ),
        height=350,
        margin=dict(t=20, b=80, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='-apple-system, sans-serif')
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

    # Create MetaFlex green gradient colors - different shade for each bar
    green_shades = [
        '#0a4b4b',  # Dark teal
        '#2d5016',  # Dark forest green
        '#4a7c59',  # Medium green
        '#6bcf7f',  # Light green
        '#8ee99f',  # Lighter green
        '#b8ffc6',  # Very light green
    ]

    # Assign colors cycling through the green palette
    bar_colors = [green_shades[i % len(green_shades)] for i in range(len(counts))]

    # Create horizontal bar chart with rounded corners
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=bar_colors,  # Different MetaFlex green for each bar
            line=dict(color='#2d5016', width=2),  # Dark forest green border
            cornerradius=8  # Rounded corners for modern look
        ),
        text=[f'<b>{count}</b>' for count in counts],
        textposition='outside',
        textfont=dict(size=16, color='#2d5016', family='-apple-system, sans-serif', weight=900),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>',
        width=0.6  # Slimmer bars for premium look
    )])

    # Compact layout with smaller height
    fig.update_layout(
        height=350,
        margin=dict(t=20, b=80, l=30, r=70),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(235, 238, 242, 0.6)',  # Subtle grid
            gridwidth=1,
            zeroline=False,
            title='',
            tickfont=dict(size=12, color='#2d5016', family='-apple-system, sans-serif', weight=700),
            range=[0, max(counts) * 1.15]  # Extra space for text labels
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=13, color='#2d5016', family='-apple-system, sans-serif', weight=700),
            showgrid=False
        ),
        font=dict(family='-apple-system, sans-serif'),
        bargap=0.35
    )

    return fig
