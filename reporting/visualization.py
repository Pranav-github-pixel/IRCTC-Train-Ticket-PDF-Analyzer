"""Journey timeline visualization using Plotly.

Generates a professional, chronological timeline showing all boarding
journeys with passenger names, routes, and dates.
"""

import logging
import re
from pathlib import Path
from typing import Optional
from datetime import timedelta
from models.ticket import Ticket
from utils.constants import (
    COLORS,
    TIMELINE_DPI,
    TIMELINE_HEIGHT_PER_ENTRY,
    TIMELINE_MIN_HEIGHT,
    TIMELINE_WIDTH,
)

logger = logging.getLogger("irctc_analyzer")


def generate_timeline(
    tickets: list[Ticket],
    output_path: Path,
) -> None:
    """Generate a professional timeline visualization of all journeys.

    Args:
        tickets: Chronologically sorted list of Ticket objects.
        output_path: Full path for the output PNG file.
    """
    import plotly.graph_objects as go

    if not tickets:
        logger.warning("No tickets to visualize — skipping timeline.")
        return

    entries = _build_entries(tickets)
    if not entries:
        logger.warning("No valid entries for timeline — skipping.")
        return

    height = max(
        TIMELINE_MIN_HEIGHT,
        len(entries) * TIMELINE_HEIGHT_PER_ENTRY + 150,
    )

    fig = go.Figure()

    for i, entry in enumerate(entries):
        color = COLORS[i % len(COLORS)]
        fig.add_trace(
            go.Scatter(
                x=[entry["date"]],
                y=[i],
                mode="markers+text",
                cliponaxis = False,
                marker=dict(
                    size=18, color=color, symbol="diamond",
                    line=dict(width=2, color="#FFFFFF"),
                ),
                text=[entry["label"]],
                textposition="middle right",
                textfont=dict(size=11, color="#333333"),
                hovertemplate=(
                    f"<b>{entry['route']}</b><br>"
                    f"Date: {entry['date_str']}<br>"
                    f"Passengers: {entry['passengers']}<br>"
                    f"Train: {entry['train']}<br>"
                    f"PNR: {entry['pnr']}"
                    "<extra></extra>"
                ),
                name=entry["date_str"],
                showlegend=False,
            )
        )

    fig.update_layout(
        title=dict(
            text="🚂 Journey Timeline",
            font=dict(size=24, color="#1F4E79", family="Arial Black"),
            x=0.5, xanchor="center",
        ),
        xaxis=dict(
            title="Departure Date",
            title_font=dict(size=14, color="#555555"),
            tickfont=dict(size=11),
            gridcolor="#F0F0F0",
            showgrid=True,
            type="date",
            dtick="M1",
            tickformat="%d %b %Y",

     # add space on right for labels
            range=[
            min(entry["date"] for entry in entries) - timedelta(days =5),
            max(entry["date"] for entry in entries) + timedelta(days=10),
            ],
        ),
        yaxis=dict(
            showticklabels=False, showgrid=False, zeroline=False,
        ),
        plot_bgcolor="#FAFBFC",
        paper_bgcolor="#FFFFFF",
        height=height, width=TIMELINE_WIDTH,
        margin=dict(l=120, r=500, t=80, b=60),
        font=dict(family="Arial, sans-serif"),
    )

    for i, entry in enumerate(entries):
        fig.add_annotation(
            x=entry["date"], y=i,
            text=f"<b>{entry['date_str']}</b>",
            showarrow=True, arrowhead=0,
            arrowwidth=1, arrowcolor="#CCCCCC",
            ax=-80, ay=0,
            font=dict(size=10, color="#666666"),
            bgcolor="#F5F5F5",
            bordercolor="#DDDDDD", borderwidth=1, borderpad=4,
        )

    try:
        fig.write_image(str(output_path), scale=TIMELINE_DPI / 72)
        logger.info("[OK] Timeline saved: %s", output_path)
    except Exception as exc:
        html_path = output_path.with_suffix(".html")
        fig.write_html(str(html_path))
        logger.warning(
            "PNG export failed (%s). Saved as HTML: %s", exc, html_path,
        )


def _build_entries(tickets: list[Ticket]) -> list[dict]:
    """Build timeline entries from ticket data."""
    entries: list[dict] = []
    for ticket in tickets:
        if ticket.departure_datetime is None:
            continue
        passengers = ticket.passenger_names or "Unknown"
        from_st = _short_station(ticket.from_station)
        to_st = _short_station(ticket.to_station)
        route = f"{from_st} → {to_st}"
        date_str = ticket.departure_datetime.strftime("%d-%b-%Y")
        train_info = (
            f"{ticket.train_number or '?'} "
            f"{ticket.train_name or ''}"
        ).strip()
        label = f"  {passengers}  |  {route}"
        entries.append({
            "date": ticket.departure_datetime,
            "date_str": date_str,
            "passengers": passengers,
            "route": route,
            "train": train_info,
            "pnr": ticket.pnr or "N/A",
            "label": label,
        })
    return entries


def _short_station(station: Optional[str]) -> str:
    """Shorten station name for display."""
    if not station:
        return "?"
    name = re.sub(r"\s*\([^)]*\)\s*", "", station).strip()
    return name.title() if name else station.title()
