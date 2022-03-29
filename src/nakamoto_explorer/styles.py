
import plotly.io as pio
from plotly.graph_objects import Layout

# Currently (2022-02) this dash_table styles can not be changed using CSS
BACKGROUND_COLOR = '#1c1c1f'
MENU_BACKGROUND = '#282828'
TABLE_HEADER_BACKGROUND = '#1e2122'
TABLE_CELL_BACKGROUND = '#282828'
TABLE_CELL_BACKGROUND_2 = '#303030'
TABLE_CELL_HIGHLIGHTED = '#484545'
TEXT_COLOR = '#cccccc'
BORDER_COLOR = '#454a4d'

MAIN_TABLE_HEIGHT = '350px'

# Other configuration parameters used in `renders` module
GREEN = 'green'
DARK_GREEN = '#2A4A21'
RED = 'indianred'
BRIGHT_RED = '#ef553b'
DARK_RED = '#4E1A1A'
DARK_VIOLET = '#636efa'


plotly_template = {
    'layout': Layout(
        font={'color': '#cccccc'},
        paper_bgcolor='#1c1c1f',
        plot_bgcolor='#1c1c1f',
        title={'x': 0.5}
    )
}

pio.templates['nakamoto'] = plotly_template


table_style = {
    'height': MAIN_TABLE_HEIGHT,
    'width': '1450px',
    'overflowY': 'auto'
}

table_data_style = {
    'backgroundColor': TABLE_CELL_BACKGROUND,
    'color': TEXT_COLOR,
    'border': f'1px solid {BORDER_COLOR}',
}

table_cell_style = {
    'overflow': 'hidden',
    'textOverflow': 'ellipsis',
    'maxWidth': '110px',
    'width': '90px'
}

table_header_style = {
    'backgroundColor': TABLE_HEADER_BACKGROUND,
    'color': TEXT_COLOR,
    'textAlign': 'center',
    'border': f'1px solid {BORDER_COLOR}',
    'fontWeight': 'bold'
}

table_odd_rows_style = {
    'backgroundColor': TABLE_CELL_BACKGROUND_2,
}

table_select_style = {
    'backgroundColor': TABLE_HEADER_BACKGROUND,
    'border': f'2px solid {BORDER_COLOR}',
}


def tab_style(selected: bool = False, nested: int = 0) -> dict:
    style = {
        'border': 'None',
        'backgroundColor': MENU_BACKGROUND if selected else BACKGROUND_COLOR,
        'color': TEXT_COLOR
    }
    if nested:
        if nested == 1:
            style['padding'] = '12px'
        elif nested == 2:
            style['padding'] = '6px'
        else:
            raise NotImplementedError
    return style


def tabs_style(nested: bool = False) -> dict:
    style = {
        'border': f'1px solid {BORDER_COLOR}',
    }
    if nested:
        style['borderTop'] = 'None'
    return style
