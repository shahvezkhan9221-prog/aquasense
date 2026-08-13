import plotly.graph_objects as go
import pandas as pd

def create_parameter_chart(df, param_key, display_name, unit, safe_min=None, safe_max=None, line_color="#06b6d4", fill_color="rgba(6, 182, 212, 0.08)"):
    """
    Creates an interactive Plotly area/line chart for a specific water parameter.
    Includes custom safety zones, spline curves, and transparent layout.
    """
    if df.empty:
        # Return empty placeholder figure
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis={"visible": False},
            yaxis={"visible": False},
            annotations=[{
                "text": "No historical telemetry available",
                "xref": "paper", "yref": "paper",
                "showarrow": False,
                "font": {"color": "#94a3b8", "size": 14}
            }]
        )
        return fig

    # Ensure sorting by timestamp
    df_sorted = df.sort_values("timestamp")
    
    x = df_sorted["timestamp"]
    y = df_sorted[param_key]
    
    fig = go.Figure()
    
    # Add safety zones if specified
    # Add custom rectangle for Safe Range
    min_y, max_y = y.min(), y.max()
    pad_min = min(min_y, safe_min if safe_min is not None else min_y) * 0.9
    pad_max = max(max_y, safe_max if safe_max is not None else max_y) * 1.1
    
    if safe_min is not None or safe_max is not None:
        s_min = safe_min if safe_min is not None else pad_min
        s_max = safe_max if safe_max is not None else pad_max
        fig.add_hrect(
            y0=s_min, y1=s_max,
            fillcolor="rgba(16, 185, 129, 0.05)",  # faint emerald tint
            line_width=0,
            annotation_text="Optimal Range",
            annotation_position="top left",
            annotation_font=dict(size=9, color="rgba(16, 185, 129, 0.5)")
        )
        
        # Safe limit lines
        if safe_min is not None:
            fig.add_hline(y=safe_min, line_dash="dash", line_color="rgba(16, 185, 129, 0.2)", line_width=1)
        if safe_max is not None:
            fig.add_hline(y=safe_max, line_dash="dash", line_color="rgba(16, 185, 129, 0.2)", line_width=1)

    # Primary time series curve
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        line=dict(color=line_color, width=3, shape="spline"),
        marker=dict(size=6, color=line_color, opacity=0.8, line=dict(color="#1e293b", width=1)),
        fill="tozeroy",
        fillcolor=fill_color,
        hovertemplate=(
            "<b>%{x|%b %d, %H:%M}</b><br>"
            f"{display_name}: <b>%{{y}}</b> {unit}<extra></extra>"
        ),
        name=display_name
    ))
    
    # Set axis properties and overall look
    fig.update_layout(
        margin=dict(l=30, r=20, t=25, b=25),
        height=260,
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#94a3b8"),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_color="#f8fafc",
            bordercolor="rgba(255,255,255,0.1)"
        ),
        xaxis=dict(
            showline=True,
            showgrid=False,
            linecolor="rgba(255, 255, 255, 0.1)",
            linewidth=1,
            tickfont=dict(color="#94a3b8"),
            type="date"
        ),
        yaxis=dict(
            showline=False,
            showgrid=True,
            gridcolor="rgba(255, 255, 255, 0.05)",
            tickfont=dict(color="#94a3b8"),
            range=[pad_min, pad_max]
        )
    )
    
    return fig
