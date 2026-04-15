import numpy as np
import plotly.graph_objects as go


def plot_engelamiento_interactive(
    data_by_time, times, output_path, title="Riesgo de Engelamiento"
):

    lats_2d = data_by_time[0]["lats"].values
    lons_2d = data_by_time[0]["lons"].values
    lats = lats_2d[:, 0]
    lons = lons_2d[0, :]

    all_p = []
    for d in data_by_time:
        v = d["engelamiento"].values[~np.isnan(d["engelamiento"].values)]
        if len(v) > 0:
            all_p.extend([v.min(), v.max()])
    vmin = min(all_p) if all_p else 800
    vmax = max(all_p) if all_p else 1000

    first_en = data_by_time[0]["engelamiento"].values

    fig = go.Figure()

    # Fondo gris claro
    fig.add_trace(
        go.Scatter(
            x=[lons.min(), lons.max(), lons.max(), lons.min(), lons.min()],
            y=[lats.min(), lats.min(), lats.max(), lats.max(), lats.min()],
            mode="lines",
            fill="toself",
            fillcolor="#e8e8e8",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=lons_2d[0, :],
            y=lats_2d[0, :],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=lons_2d[-1, :],
            y=lats_2d[-1, :],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=lons_2d[:, 0],
            y=lats_2d[:, 0],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=lons_2d[:, -1],
            y=lats_2d[:, -1],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Contour(
            x=lons,
            y=lats,
            z=first_en,
            colorscale="RdYlBu_r",
            zmin=vmin,
            zmax=vmax,
            colorbar=dict(title="Presion (hPa)", len=0.7),
            contours=dict(showlabels=True, coloring="heatmap"),
        )
    )

    frames = []
    for i in range(len(data_by_time)):
        eng = data_by_time[i]["engelamiento"].values
        trace0 = go.Scatter(
            x=[lons.min(), lons.max(), lons.max(), lons.min(), lons.min()],
            y=[lats.min(), lats.min(), lats.max(), lats.max(), lats.min()],
            mode="lines",
            fill="toself",
            fillcolor="#e8e8e8",
            line=dict(width=0),
            hoverinfo="skip",
            showlegend=False,
        )
        trace1 = go.Scatter(
            x=lons_2d[0, :],
            y=lats_2d[0, :],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
        trace2 = go.Scatter(
            x=lons_2d[-1, :],
            y=lats_2d[-1, :],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
        trace3 = go.Scatter(
            x=lons_2d[:, 0],
            y=lats_2d[:, 0],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
        trace4 = go.Scatter(
            x=lons_2d[:, -1],
            y=lats_2d[:, -1],
            mode="lines",
            line=dict(color="#555555", width=1),
            hoverinfo="skip",
            showlegend=False,
        )
        trace5 = go.Contour(
            x=lons,
            y=lats,
            z=eng,
            colorscale="RdYlBu_r",
            zmin=vmin,
            zmax=vmax,
            contours=dict(showlabels=True, coloring="heatmap"),
        )
        frame_data = [trace0, trace1, trace2, trace3, trace4, trace5]
        frames.append(go.Frame(data=frame_data, name=str(i), traces=[0, 1, 2, 3, 4, 5]))
    fig.frames = frames

    slider_steps = []
    for i in range(len(times)):
        label = str(times[i])[:16]
        step_dict = {"args": [[str(i)]], "label": label, "method": "animate"}
        slider_steps.append(step_dict)

    btn_play = {"label": "Play", "method": "animate", "args": [None]}
    btn_pause = {"label": "Pause", "method": "animate", "args": [[None]]}
    buttons_list = [btn_play, btn_pause]
    buttons_dict = {
        "type": "buttons",
        "showactive": False,
        "y": -0.12,
        "x": 0.1,
        "buttons": buttons_list,
    }
    updatemenus_list = [buttons_dict]

    slider_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {"prefix": "Hora: ", "visible": True},
        "transition": {"duration": 300},
        "pad": {"b": 10, "t": 50},
        "len": 0.85,
        "x": 0.08,
        "y": -0.02,
        "steps": slider_steps,
    }
    sliders_list = [slider_dict]

    fig.update_layout(
        title={"text": title, "x": 0.5},
        paper_bgcolor="white",
        plot_bgcolor="#f5f5f5",
        xaxis={
            "title": "Longitud",
            "range": [lons.min() - 0.05, lons.max() + 0.05],
            "showgrid": True,
            "gridcolor": "#ddd",
        },
        yaxis={
            "title": "Latitud",
            "range": [lats.min() - 0.05, lats.max() + 0.05],
            "scaleanchor": "x",
            "scaleratio": 1,
            "showgrid": True,
            "gridcolor": "#ddd",
        },
        updatemenus=updatemenus_list,
        sliders=sliders_list,
        height=720,
        width=1000,
        margin={"l": 60, "r": 60, "t": 80, "b": 100},
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
