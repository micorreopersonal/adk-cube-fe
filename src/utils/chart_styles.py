import streamlit as st

# --- BRAND COLORS (RIMAC) ---
class ChartColors:
    # Primary Palette (Fallback Defaults)
    PRIMARY_RED = '#EF3340'
    PRIMARY_BLUE = '#3949AB'
    PRIMARY_TEAL = '#00897B'
    PRIMARY_ORANGE = '#FB8C00'
    PRIMARY_GREY = '#757575'
    PRIMARY_PURPLE = '#8E24AA'
    
    # Semantic Colors
    SUCCESS = '#00C851'
    WARNING = '#ffbb33'
    DANGER = '#ff4444'
    INFO = '#33b5e5'

    # Default Sequence
    DEFAULTS = [PRIMARY_RED, PRIMARY_BLUE, PRIMARY_TEAL, PRIMARY_ORANGE, PRIMARY_GREY, PRIMARY_PURPLE]

    @staticmethod
    def get_colors():
        """Retrieve the active color sequence from Session State or return defaults."""
        if "custom_colors" in st.session_state:
            return st.session_state.custom_colors
        return ChartColors.DEFAULTS

    # Property for backward compatibility (dynamic access)
    @property
    def SEQUENCE(self):
        return self.get_colors()

# Instantiate for property access if needed, but static method is preferred.
# For now, we will expose a helper or just use the static method.

# --- STANDARD LAYOUTS ---
class ChartLayouts:
    
    @staticmethod
    def _base_layout(title: str, height: int = 500) -> dict:
        return dict(
            title=dict(
                text=title,
                font=dict(size=18, family="Arial, sans-serif"),
                x=0, # Left aligned title
                xanchor='left'
            ),
            template="plotly_white",
            height=height,
            margin=dict(l=40, r=40, t=60, b=80), # Increased bottom margin for standard legends
            font=dict(family="Arial, sans-serif"),
        )

    @staticmethod
    def get_pie_layout(title: str, show_legend: bool = True) -> dict:
        """
        Standard layout for Pie Charts.
        Legend is positioned to the right to avoid overlap with labels.
        """
        layout = ChartLayouts._base_layout(title)
        
        if show_legend:
            layout.update(dict(
                showlegend=True,
                legend=dict(
                    orientation="v",      # Vertical legend on the side
                    yanchor="top",
                    y=1,
                    xanchor="left",
                    x=1.05,               # Move legend outside the chart area to the right
                    bgcolor="rgba(0,0,0,0)",
                    font=dict(size=12)
                )
            ))
        else:
            layout.update(dict(showlegend=False))
            
        return layout

    @staticmethod
    def get_cartesian_layout(title: str, x_label: str = "", y_label: str = "", show_legend: bool = True) -> dict:
        """
        Standard layout for Bar and Line charts.
        Legend is positioned at the top right, above the grid.
        """
        layout = ChartLayouts._base_layout(title)
        
        layout.update(dict(
            xaxis=dict(
                title=x_label,
                showgrid=False,
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title=y_label,
                showgrid=True,
                gridcolor="#f0f0f0",
                tickfont=dict(size=12)
            ),
            hovermode="x unified"
        ))
        
        if show_legend:
            layout.update(dict(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,              # Slightly above the plot area
                    xanchor="right",
                    x=1,
                    bgcolor="rgba(255,255,255,0.8)"
                )
            ))
        else:
            layout.update(dict(showlegend=False))
            
        return layout
