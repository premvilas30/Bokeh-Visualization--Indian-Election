from collections import Counter
from math import pi
from operator import itemgetter

import pandas as pd
from bokeh.io import curdoc, show
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, GMapOptions, HoverTool, WheelZoomTool, Plot, LinearAxis, Grid
from bokeh.models.glyphs import HBar
from bokeh.plotting import gmap
from bokeh.plotting import output_file, show, save, figure
from bokeh.transform import cumsum

df = pd.read_csv(r'2014_election.csv', na_values=" NaN")

map_options = GMapOptions(lat=22.0000, lng=81.7394, map_type="roadmap", zoom=5)
p = gmap("Your-Google-Api-Key", map_options,
         title="2014 Indian General Election Interactive Political map")

TOOLTIPS = [
    ("Constituncy:", "@desc"),
    ("Winner:", "@Winner"),
    ("Party:", "@party"),
    ("Category:", "@category"),
    ("Total Electors", "@electors"),
    ("Total Voters:", "@voters"),
    ("Voting Percentage:", "@percent")
]
p.title.text_color = "olive"
p.title.text_font_style = "bold"
p.title.text_font_size = "20px"
p.title.align = "center"
p.add_tools(HoverTool(tooltips=TOOLTIPS))
p.toolbar.active_scroll = p.select_one(WheelZoomTool)
p.xaxis.axis_label = "Latitude"
p.yaxis.axis_label = "Longitude"
p.plot_height = 860
p.plot_width = 900
p.circle(0, 0, size=0.00000001, color="#ffffff", legend='Political Parties')
p.xaxis.axis_label = "Latitude"
p.xaxis.axis_line_width = 3
p.xaxis.axis_line_color = "black"
p.xaxis.major_label_text_color = "Blue"
p.yaxis.axis_label = "Longitude"
p.yaxis.major_label_text_color = "Blue"
p.yaxis.major_label_orientation = "horizontal"
p.yaxis.axis_line_width = 3
p.yaxis.axis_line_color = "black"
p.xaxis.axis_label_standoff = 20
p.yaxis.axis_label_standoff = 20
p.legend.label_standoff = 5
p.legend.glyph_height = 16
p.legend.label_text_color = "navy"
p.legend.click_policy = "hide"

sources = []
for region, data in df.groupby('Party'):
    source = ColumnDataSource(data=dict(
        lat=list(data.lat),
        long=list(data.long),
        electors=data.Total_Electors,
        voters=data.Total_voters,
        percent=data.POLL_PERCENTAGE,
        desc=list(data.PC_name),
        Winner=list(data.MP_Name),
        Gender=list(data.Sex),
        party=data.Party,
        color=data.color,
        category=data.Category
    ))
    p.circle_cross('long', 'lat', size=13, source=source, color='color', legend='party')
new_legend = p.legend[0]
p.legend[0].plot = None
p.add_layout(new_legend, 'right')

# bars
party_color = zip(df.Party.unique(), df.color.unique())
party_color = [s for s in party_color]
seats = Counter(df.Party)
par = []
for party in party_color:
    p1 = list(party)
    p1.append(seats[p1[0]])
    par.append(p1)
par = sorted(par, key=itemgetter(2))
others_count = 0
for s in par:
    if not s[2] > 3:
        others_count += s[2]

party = [s[0] for s in par if s[2] > 3]
color = [s[1] for s in par if s[2] > 3]
count = [str(s[2]) for s in par if s[2] > 3]
count_int = [s[2] for s in par if s[2] > 3]
party.insert(-2, 'Others')
count.insert(-2, str(others_count))
count_int.insert(-2, others_count)
color.insert(-2, 'red')
angle = [s / 493 * pi for s in count_int]
sou = ColumnDataSource(data=dict(
    count=count_int,
    angle=angle,
    color=color,
    party=party
))
dot = figure(title="Partywise Parliament Strength", tools="hover", toolbar_location=None,
             tooltips=[("Party:", "@party"), ("SeatShare:", "@count")],
             y_range=party, x_axis_type="log", x_range=[1, 800])

dot.segment(0, 'party', 'count', 'party', line_width=10, line_color='color', source=sou)
dot.circle('count', 'party', size=10, fill_color='color', line_color='color', line_width=10, source=sou)
dot.toolbar.active_scroll = p.select_one(WheelZoomTool)
dot.title.text_color = "olive"
dot.title.text_font_style = "bold"
dot.title.text_font_size = "20px"
dot.title.align = "center"
dot.xaxis.axis_label = "Number of Seats ( logarithmic Scale)"
dot.yaxis.axis_label = "Parties"
dot.plot_height = 700
dot.plot_width = 600
dot.xaxis.axis_line_width = 3
dot.xaxis.axis_line_color = "black"
dot.xaxis.major_label_text_color = "Blue"
dot.yaxis.major_label_text_color = "Blue"
dot.yaxis.major_label_orientation = "horizontal"
dot.yaxis.axis_line_width = 3
dot.yaxis.axis_line_color = "black"

x = {(key, value) for (key, value) in zip(party, count)}
data = pd.DataFrame()

# Annular Wedge
t = figure(plot_height=700, title="Aggregated Seat Share", plot_width=900,
           tools="hover", tooltips=[("Party:", "@party"), ("SeatShare:", "@count")], x_range=(-0.8, 1.0))
t.wedge(x=0, y=1, radius=0.6,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend='party', source=sou)
t.axis.axis_label = None
t.axis.visible = False
t.grid.grid_line_color = None
t.toolbar.active_scroll = p.select_one(WheelZoomTool)
t.title.text_color = "olive"
t.title.text_font_style = "bold"
t.title.text_font_size = "20px"
t.title.align = "center"

# outPut
show(column(row(p, dot), t))
output_file("Prem_Keshari_18303567.html")
