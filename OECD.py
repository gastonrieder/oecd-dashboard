from os.path import dirname, join
import math
import pandas as pd
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Select, Slider
# , TextInput
from bokeh.plotting import figure, show

oecd = pd.read_csv('OECD - English.csv')
desc = Div(text=open(join(dirname(__file__),
           'description.html')).read(), sizing_mode='stretch_width')

axis_map = oecd.columns[5:]

source = ColumnDataSource(data=dict())

fig = figure(height=300,
             width=600,
             title="",
             toolbar_location=None,
             sizing_mode="scale_both")

fig.image_url(url='url',
              x="x", y="y",
              source=source,
              global_alpha=0.75)

x_axis = Select(title='X Axis',
                options=sorted(axis_map),
                value='GDP per capita (USD current PPPs)')
y_axis = Select(title="Y Axis",
                options=sorted(axis_map),
                value='Inflation rate: all items (Annual growth %)')

slider_x = Slider(title=x_axis.value,
                  start=oecd[x_axis.value].min(),
                  end=oecd[x_axis.value].max(),
                  value=oecd[x_axis.value].median())
slider_y = Slider(title=y_axis.value,
                  start=oecd[y_axis.value].min(),
                  end=oecd[y_axis.value].max(),
                  value=oecd[y_axis.value].median())


def on_y_change(attr, old, new):
    selected = oecd[oecd[new].notna()]

    fig.yaxis.axis_label = new
    fig.title.text = """Infomation for %d countries available.\n
                     %d countries currently in display""" % (len(selected), len(selected))

    start = selected[new].min()
    end = selected[new].max()

    range = selected[new].max() - selected[new].min()
    step = range / 1000
    mag10 = math.ceil(math.log(step) / math.log(10))
    step = math.pow(10, mag10)

    slider_y.update(title=new,
                    start=start,
                    end=end,
                    value=end,
                    step=step)

    source.data = dict(x=selected[x_axis.value],
                       y=selected[new],
                       url=selected['url'],
                       country=selected['country'])


def on_slider_y_change(attr, old, new):
    selected = oecd
    selected_filtered = selected[selected[y_axis.value] <= new]
    fig.title.text = """Infomation for %d countries available.\n
                     %d countries currently in display""" % (len(selected), len(selected_filtered))
    source.data = dict(x=selected_filtered[x_axis.value],
                       y=selected_filtered[y_axis.value],
                       url=selected_filtered['url'],
                       country=selected_filtered['country'])


def display():
    controls = [slider_x, slider_y, x_axis, y_axis]

    inputs = column(*controls, width=320)

    # x_axis.on_change('value', on_x_change)
    y_axis.on_change('value', on_y_change)
    # slider_x.on_change('value', on_slider_x_change)
    slider_y.on_change('value', on_slider_y_change)

    html_base = column(desc, row(inputs, fig),
                       sizing_mode="scale_both")

    # on_x_change('value', None, x_axis)
    on_y_change('value', None, y_axis.value)
    curdoc().add_root(html_base)
    curdoc().title = "OECD"

    show(fig)


display()
# bokeh serve --show /Users/gastonrieder/Documents/Personal/OECD.py
