import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import pandas as pd
from textwrap import wrap
import warnings

warnings.simplefilter(action='ignore', category=UserWarning)

# Désactiver l'option de réduction de la largeur de l'application
st.set_page_config(layout="centered")

# Titre et description de l'application
st.title("Matrice en radar")
st.write("Représenter un tableau à deux entrées en forme de radar, et ce quelque soit le type de données évaluées")

# TELECHARGEMENT DU FICHIER MASTER
# Ajouter un widget de téléchargement de fichier
with st.expander("Téléchargement de fichier"):
    my_file = st.file_uploader("", type=["xlsx"])

if my_file is None:
    st.stop()

# Charger les données du fichier Excel
df = pd.read_excel(my_file, index_col=0)
df_max = pd.DataFrame([df.max()], columns=df.columns)
df_max.index = ['Synthese']

list_ressource = list(df.index.values)
list_ressource.append('Tous')
list_ressource.append('Synthese')

choice_ticker = st.selectbox("Selectionnez une ressource :", list_ressource, index=list_ressource.index('Tous'))

if choice_ticker == 'Tous':
    choice_ticker2 = st.selectbox("Selectionnez une représentation de trait :", ['Traits détaillés', 'Traits simples'], index=0)

# Ajouter une option pour choisir si le texte doit être raccourci (wrap)
wrap_text = st.checkbox("Raccourcir le texte", value=True)

# Ajouter un curseur pour ajuster la taille de la police des étiquettes des axes
label_font_size = st.slider("Taille de la police des étiquettes des axes", min_value=6, max_value=20, value=10)

# Round the values
df = df.round(1)

# Define the colormap
colors = ['#F4AF81', '#FEF2CB', '#A9D08D']  # Orange, Yellow, Green
n_bins = 100  # Discretizes the interpolation into bins
cmap_name = 'orange_yellow_green'
cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

# Style the DataFrame
styled_df = df.style.set_properties(
    **{'text-align': 'center', 'white-space': 'normal'}
).set_table_styles([
    {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center'), ('white-space', 'normal')]},
    {'selector': 'td:first-child', 'props': [('text-align', 'left')]},
    {'selector': 'td, th', 'props': [('border', '1px solid lightgray')]},
    {'selector': 'table', 'props': [('border', 'none'), ('table-layout', 'fixed'), ('width', '100%')]},
    {'selector': 'th, td', 'props': [('width', f'{100 / len(df.columns)}%')]},
]).format(precision=1).background_gradient(cmap=cm, axis=None)

# The attributes we want to use in our radar plot.
labels = list(df.columns[0:])

if wrap_text:
    labels = ["\n".join(wrap(r[:38] + ('...' if len(r) > 38 else ''), 22, break_long_words=False)) for r in labels]

num_vars = len(labels)

# Split the circle into even parts and save the angles so we know where to put each axis.
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

# The plot is a circle, so we need to "complete the loop" and append the start value to the end.
angles += angles[:1]
labels += labels[:1]

# Create the figure and polar subplot
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

# List of colors for the border
border_colors = ['#FF8700', '#4682B4', '#32CD32', '#FFD700', '#8A2BE2']
# List of line styles
line_styles = ['-', '--', ':', (0, (5, 1, 1, 1, 1, 1))]
# List of line widths
line_widths = [1, 1.5]
# Constant fill color
fill_color = '#14aeb0'

# Helper function to plot each car on the radar chart.
def add_to_radar(car_model, line_style, color, line_width):
    values = df.loc[car_model].tolist()
    values += values[:1]
    ax.plot(angles, values, color=color, linewidth=line_width, linestyle=line_style, label=car_model)
    ax.fill(angles, values, color=fill_color, alpha=0.15)

if choice_ticker == "Tous":
    total_styles = len(line_styles) * len(border_colors) * len(line_widths)
    for i, car_model in enumerate(df.index):
        if choice_ticker2 == 'Traits détaillés':
            line_style = line_styles[i % len(line_styles)]
            color = border_colors[(i // len(line_styles)) % len(border_colors)]
            line_width = line_widths[(i // (len(line_styles) * len(border_colors))) % len(line_widths)]
            add_to_radar(car_model, line_style, color, line_width)
        else:
            line_style = line_styles[0]
            color = border_colors[0]
            line_width = line_widths[0]
            add_to_radar(car_model, line_style, color, line_width)
elif choice_ticker == "Synthese":
    values = df_max.loc[choice_ticker].tolist()
    values += values[:1]
    ax.plot(angles, values, color='#FF8700', linewidth=1, linestyle='-', label=choice_ticker)
    ax.fill(angles, values, color=fill_color, alpha=0.15)
else:
    line_style = line_styles[0]
    color = border_colors[0]
    line_width = line_widths[0]
    add_to_radar(choice_ticker, line_style, color, line_width)

# Fix axis to go in the right order and start at 12 o'clock.
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Draw axis lines for each angle and label.
ax.set_thetagrids(np.degrees(angles), labels, fontsize=label_font_size)

# Go through labels and adjust alignment based on where it is in the circle.
for label, angle in zip(ax.get_xticklabels(), angles):
    if angle in (0, np.pi):
        label.set_horizontalalignment('center')
    elif 0 < angle < np.pi:
        label.set_horizontalalignment('left')
    else:
        label.set_horizontalalignment('right')

# Ensure radar goes from 0 to 100.
ax.set_ylim(0, 5)

# Set position of y-labels (0-100) to be in the middle of the first two axes.
ax.set_rlabel_position(180 / num_vars)

# Add some custom styling.
ax.tick_params(colors='#222222')
ax.tick_params(axis='y', labelsize=8)
ax.grid(color='#AAAAAA')
ax.spines['polar'].set_color('#222222')
ax.set_facecolor('#FAFAFA')

# Add a legend as well.
ax.legend(loc='upper right', bbox_to_anchor=(1.9, 1.1))

# Display the plot in Streamlit
st.pyplot(fig)

# Convertir le DataFrame stylisé en HTML et l'afficher
st.write("### Tableau des données")
html = styled_df.to_html()
st.write(html, unsafe_allow_html=True)
