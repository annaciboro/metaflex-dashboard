import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# MetaFlex Premium Light Theme Palette - Subtle Version
MF_LIGHT = {
    'bg_white': '#ffffff',           # Pure white background
    'bg_light': '#f9fafb',           # Very light gray surface
    'border': '#e5e7eb',             # Subtle gray border
    'accent_teal': '#0a4b4b',        # Teal for strategic accents (dark)
    'accent_teal_light': '#4d8787',  # Lighter teal for subtle charts
    'accent_teal_very_light': '#90b4b4',  # Very light teal for backgrounds
    'accent_lime': '#7a9900',        # Olive lime for CTAs
    'accent_lime_muted': '#a8c957',  # Muted lime for subtle highlights
    'text_dark': '#2d3748',          # Dark gray text (primary)
    'text_medium': '#374151',        # Medium gray text
    'text_light': '#6b7280',         # Light gray text (secondary)
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


def create_project_tasks_overview_chart(exec_metrics):
    """
    Combined Project Tasks Overview with premium light theme
    Shows both total tasks and open tasks per project in grouped bars
    """
    project_data = []
    for project, metrics in exec_metrics["tasks_by_project"].items():
        project_data.append({
            "Project": project,
            "Total Tasks": metrics["total"],
            "Open Tasks": metrics["open"]
        })

    if not project_data:
        st.info("No project data available.")
        return None

    project_df = pd.DataFrame(project_data).sort_values("Total Tasks", ascending=True)

    # Create bar colors - subtle light teal for all, muted lime for top performer
    total_colors = [MF_LIGHT['accent_teal_very_light'] if i < len(project_df) - 1 else MF_LIGHT['accent_lime_muted'] for i in range(len(project_df))]
    open_colors = [MF_LIGHT['accent_teal_light'] for _ in range(len(project_df))]

    # Create grouped bar chart
    fig = go.Figure()

    # Total Tasks bar (teal with lime green for top)
    fig.add_trace(go.Bar(
        y=project_df["Project"],
        x=project_df["Total Tasks"],
        name='Total Tasks',
        orientation='h',
        marker=dict(
            color=total_colors,
            line=dict(color=MF_LIGHT['border'], width=1)
        ),
        text=project_df["Total Tasks"],
        textposition='outside',
        textfont=dict(size=13, color=MF_LIGHT['text_dark'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Total Tasks: %{x}<extra></extra>'
    ))

    # Open Tasks bar (darker teal)
    fig.add_trace(go.Bar(
        y=project_df["Project"],
        x=project_df["Open Tasks"],
        name='Open Tasks',
        orientation='h',
        marker=dict(
            color=open_colors,
            line=dict(color=MF_LIGHT['border'], width=1)
        ),
        text=project_df["Open Tasks"],
        textposition='outside',
        textfont=dict(size=13, color=MF_LIGHT['text_dark'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Open Tasks: %{x}<extra></extra>'
    ))

    max_value = project_df["Total Tasks"].max() if len(project_df) > 0 else 10

    fig.update_layout(
        title=dict(
            text='<b>Project Tasks Overview</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_LIGHT['text_dark'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=140, r=80),
        paper_bgcolor=MF_LIGHT['bg_white'],
        plot_bgcolor=MF_LIGHT['bg_light'],
        barmode='group',  # Group bars side by side
        bargap=0.15,
        bargroupgap=0.1,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(229, 231, 235, 0.6)',
            title=dict(text='Number of Tasks', font=dict(size=12, color=MF_LIGHT['text_medium'])),
            tickfont=dict(size=11, color=MF_LIGHT['text_medium']),
            range=[0, max_value * 1.2]
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_LIGHT['text_dark'])
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=MF_LIGHT['text_medium'], family='-apple-system, sans-serif'),
            bgcolor='rgba(0,0,0,0)'
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

    # Subtle teal gradient - from very light to medium light
    colors = ['#c8d9d9', '#90b4b4', '#6d9f9f', '#4d8787']

    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker=dict(
            color=colors,
            line=dict(color=MF_LIGHT['border'], width=2)
        ),
        text=values,
        textposition='outside',
        textfont=dict(size=14, color=MF_LIGHT['text_light'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{x}</b><br>Tasks: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='<b>Task Age Analysis</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_LIGHT['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        paper_bgcolor=MF_LIGHT['bg_white'],
        plot_bgcolor=MF_LIGHT['bg_light'],
        xaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_LIGHT['text_light'])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(229, 231, 235, 0.6)',
            title=dict(text='Number of Tasks', font=dict(size=12, color=MF_LIGHT['text_light'])),
            tickfont=dict(size=11, color=MF_LIGHT['text_light'])
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
        line=dict(color=MF_LIGHT['accent_lime'], width=3),
        marker=dict(
            size=10,
            color=MF_LIGHT['accent_lime'],
            line=dict(color=MF_LIGHT['border'], width=2)
        ),
        fill='tozeroy',
        fillcolor='rgba(10, 75, 75, 0.1)',
        hovertemplate='<b>%{x}</b><br>Completed: %{y}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(
            text='<b>Task Completion Velocity</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_LIGHT['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=60, r=60),
        paper_bgcolor=MF_LIGHT['bg_white'],
        plot_bgcolor=MF_LIGHT['bg_light'],
        xaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_LIGHT['text_light']),
            showgrid=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(229, 231, 235, 0.6)',
            title=dict(text='Tasks Completed', font=dict(size=12, color=MF_LIGHT['text_light'])),
            tickfont=dict(size=11, color=MF_LIGHT['text_light'])
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

    # Color code by health score - subtle teal shades
    colors = []
    for score in project_df["Health Score"]:
        if score >= 75:
            colors.append('#90b4b4')  # Healthy - light teal
        elif score >= 50:
            colors.append('#6d9f9f')  # Warning - medium teal
        else:
            colors.append('#4d8787')  # At risk - darker teal

    fig = go.Figure(data=[go.Bar(
        y=project_df["Project"],
        x=project_df["Health Score"],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color=MF_LIGHT['border'], width=2)
        ),
        text=[f"{score}%" for score in project_df["Health Score"]],
        textposition='outside',
        textfont=dict(size=14, color=MF_LIGHT['text_light'], family='-apple-system, sans-serif'),
        hovertemplate='<b>%{y}</b><br>Health: %{x}%<br>Total Tasks: %{customdata}<extra></extra>',
        customdata=project_df["Total"]
    )])

    fig.update_layout(
        title=dict(
            text='<b>Project Health Dashboard</b>',
            x=0.5,
            xanchor='center',
            font=dict(size=18, color=MF_LIGHT['text_light'], family='-apple-system, sans-serif')
        ),
        height=400,
        margin=dict(t=60, b=40, l=140, r=60),
        paper_bgcolor=MF_LIGHT['bg_white'],
        plot_bgcolor=MF_LIGHT['bg_light'],
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(229, 231, 235, 0.6)',
            title=dict(text='Health Score (%)', font=dict(size=12, color=MF_LIGHT['text_light'])),
            tickfont=dict(size=11, color=MF_LIGHT['text_light']),
            range=[0, 110]
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12, color=MF_LIGHT['text_light'])
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

    # MetaFlex color palette - teal, forest green, lime shades
    metaflex_colors = [
        '#0a4b4b',  # Dark teal
        '#0d6868',  # Medium teal
        '#2d5a3d',  # Dark forest green
        '#4d7a40',  # Medium forest green
        '#7a9900',  # Lime green
        '#a8d900',  # Light lime
    ]

    # Assign colors cycling through the MetaFlex palette
    bar_colors = [metaflex_colors[i % len(metaflex_colors)] for i in range(len(counts))]

    # Create horizontal bar chart with rounded corners
    fig = go.Figure(data=[go.Bar(
        y=projects,
        x=counts,
        orientation='h',
        marker=dict(
            color=bar_colors,  # Different subtle teal for each bar
            line=dict(color=MF_LIGHT['border'], width=1),  # Subtle border
            cornerradius=8  # Rounded corners for modern look
        ),
        text=[f'<b>{count}</b>' for count in counts],
        textposition='outside',
        textfont=dict(size=14, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', weight='bold'),
        hovertemplate='<b>%{y}</b><br>Tasks: %{x}<extra></extra>',
        width=0.6  # Slimmer bars for premium look
    )])

    # Compact layout with matching height and margins to align bottoms
    fig.update_layout(
        height=380,
        margin=dict(t=50, b=60, l=30, r=70),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(235, 238, 242, 0.6)',  # Subtle grid
            gridwidth=1,
            zeroline=False,
            title='',
            tickfont=dict(size=12, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', weight=600),
            range=[0, max(counts) * 1.15]  # Extra space for text labels
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=13, color='#0a4b4b', family='-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif', weight=600),
            showgrid=False
        ),
        font=dict(family='-apple-system, sans-serif'),
        bargap=0.35
    )

    return fig
