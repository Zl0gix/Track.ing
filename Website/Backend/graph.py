import plotly.graph_objects as go
import plotly.io as pltIO

def RoundAndScale(metric):
    metricScaled = metric * 100
    metricScaled = int(round(metricScaled, 0))
    return metricScaled

def Radar(consistency, hardWorking, original, inspirational, GOAT):
    consistencyScaled = RoundAndScale(consistency)
    hardWorkingScaled = RoundAndScale(hardWorking)
    originalityScaled = RoundAndScale(original)
    inspirationScaled = RoundAndScale(inspirational)
    GOATScaled = RoundAndScale(GOAT)

    fig = go.Figure(data=go.Scatterpolar(
    r = [consistencyScaled, hardWorkingScaled, originalityScaled, inspirationScaled, GOATScaled],
    theta=[f'Consistency {consistencyScaled}',f'Hard Working {hardWorkingScaled}',f'Original {originalityScaled}', f'Inspirational {inspirationScaled}',
            f'G.O.A.T {GOATScaled}'],
    fill='toself',
    fillcolor='#7efffb',
    opacity=1
    ))

    fig.update_traces(mode = "lines+markers",
        line_color = "#ff7ed0",
        line_width = 4,
        marker = dict(
            symbol = "circle",
            size = 2)
        )

    fig.update_layout(
    polar=dict(
        bgcolor='black',
        angularaxis = dict(
            linewidth = 10),
        radialaxis=dict(
        visible=False
        ),
    ),
    showlegend=False
    )

    #fig.show()

    return pltIO.to_html(fig)



