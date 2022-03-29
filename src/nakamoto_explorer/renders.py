
from json import dumps
from operator import itemgetter
from typing import Dict, List, Set

from dash.dash_table import DataTable
from dash.dcc import Graph, Tabs, Tab
from dash import html
from pandas import DataFrame
import plotly.graph_objects as go

from nakamoto_explorer.nakamoto import Rule

from nakamoto_explorer import styles, utils


def render_dict(dictionary: dict, indent: int = 4, format_zeros: bool = True,
                delete_quotes: bool = True, add_emojis: bool = True) -> html.Pre:
    """ Render a dictionary into an html Pre element. """
    if format_zeros:
        dictionary = utils.format_dict_zeros(dictionary)
    if add_emojis:
        dictionary = utils.add_emojis_to_dict(dictionary)
    content = dumps(dictionary, indent=indent, ensure_ascii=False)
    if delete_quotes:
        # This regular expression removes quotes only in the dict keys:
        # content = re.sub(r'"(.*?)"(?=:)', r'\1', content)
        content = content.replace('"', '')
    return html.Pre(
        className='dict',
        children=[content]
    )


def render_diff_metrics_tabs(diff_metrics: dict) -> Tabs:
    """ Render a line of Tabs of diff metrics data. """
    return \
        Tabs(
            value='main',
            style=styles.tabs_style(nested=True),
            children=[
                Tab(
                    label=label.title(),
                    value=label,
                    style=styles.tab_style(nested=2),
                    selected_style=styles.tab_style(selected=True, nested=2),
                    children=[render_dict(diff_metrics[label])]
                ) for label in ['main', 'stats']
            ]
        )


def render_sub_metrics_tabs(metrics: dict) -> Tabs:
    """ Render a line of Tabs of metrics data. """
    return \
        Tabs(
            value='main',
            style=styles.tabs_style(nested=True),
            children=[
                Tab(
                    label=label.title(),
                    value=label,
                    style=styles.tab_style(nested=1),
                    selected_style=styles.tab_style(selected=True, nested=1),
                    children=[render_dict(metrics[label],
                                          format_zeros=label != 'strategy')]
                ) for label in ['main', 'stats', 'strategy', 'rules']
            ]
        )


def render_metrics(metrics: dict) -> html.Div:
    """ Render Nakamoto metrics into a Tabs section. """
    no_rules, simulation, improvement = itemgetter(
        'no_rules_metrics', 'simulation_metrics', 'improvement_metrics')(metrics)
    return \
        html.Div(
            className='metrics',
            children=[
                html.Label('Metrics'),
                Tabs(
                    value='improvement',
                    style=styles.tabs_style(),
                    children=[
                        Tab(
                            label='No rules',
                            value='no_rules',
                            style=styles.tab_style(),
                            selected_style=styles.tab_style(selected=True),
                            children=[render_sub_metrics_tabs(no_rules)]
                        ),
                        Tab(
                            label='Simulation',
                            value='simulation',
                            style=styles.tab_style(),
                            selected_style=styles.tab_style(selected=True),
                            children=[render_sub_metrics_tabs(simulation)]
                        ),
                        Tab(
                            label='Improvement',
                            value='improvement',
                            style=styles.tab_style(),
                            selected_style=styles.tab_style(selected=True),
                            children=[
                                Tabs(
                                    value='percent',
                                    style=styles.tabs_style(nested=True),
                                    children=[
                                        Tab(
                                            label='Percent',
                                            value='percent',
                                            style=styles.tab_style(nested=1),
                                            selected_style=styles.tab_style(selected=True, nested=1),
                                            children=[
                                                render_diff_metrics_tabs(improvement['percent_diffs'])
                                            ]
                                        ),
                                        Tab(
                                            label='Absolute',
                                            value='absolute',
                                            style=styles.tab_style(nested=1),
                                            selected_style=styles.tab_style(selected=True, nested=1),
                                            children=[
                                                render_diff_metrics_tabs(improvement['absolute_diffs'])
                                            ]
                                        ),
                                        Tab(
                                            label='Strategy',
                                            value='strategy',
                                            style=styles.tab_style(nested=1),
                                            selected_style=styles.tab_style(selected=True, nested=1),
                                            children=[
                                                render_dict(improvement['strategy_diffs'], format_zeros=False)
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                    ]
                ),
            ]
        )


def render_simulation_line_graphs(df: DataFrame) -> html.Div:
    """ Render a Nakamoto line-plot of price-list + performance data. """

    df = df.copy()
    df['datetime'] = df.index
    # Reduce columns to the ones needed
    df = df[['datetime', 'base-quote', 'quote_value', 'action']]
    improve = df.iloc[-1]['quote_value'] > df.iloc[-1]['base-quote']

    actions = df['action'].value_counts().index
    discarded_actions = ['init', 'end', 'sale', 'purchase']
    actions = [a for a in actions if a not in discarded_actions]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=df['base-quote'], mode='lines+markers', name='price',
        line={'color': styles.DARK_VIOLET}
    ))
    fig.add_trace(go.Scatter(
        x=df['datetime'], y=df['quote_value'], mode='lines+markers', name='performance',
        line={'color': styles.GREEN if improve else styles.BRIGHT_RED}
    ))

    for action in actions:

        if 'failed' in action:
            action_color = styles.BORDER_COLOR
        elif 'Sale' in action:
            action_color = styles.RED
        else:  # if 'Purchase' in action
            action_color = styles.GREEN

        df_action = df.loc[df['action'] == action, :]
        fig.add_trace(go.Scatter(
            x=df_action['datetime'], y=[0]*df_action.shape[0], mode='none', name='',
            hovertext=action, hoverinfo='text'
        ))
        for _, action_row in df_action.iterrows():
            fig.add_vline(x=action_row['datetime'], line_width=1, line_dash='dash',
                          line_color=action_color)

    fig.update_layout(template='plotly_dark+nakamoto',
                      title=df.columns.name.split('|')[0],
                      hovermode='x unified')

    return \
        html.Div(
            className='price-list',
            children=[Graph(figure=fig)]
        )


def render_rule(rule: Rule) -> html.Div:
    """ Render a Nakamoto Rule indicating its parameters. """
    rule_dict = rule.data.as_dict(nested=True)
    name, parameters = rule_dict['name'], rule_dict['parameters']
    color = styles.GREEN if rule.action == 'purchase' else styles.RED
    # TODO 2022.02.04 Better with horizontal plot bars.
    html_parameters = [(html.Label(f'{k}:'),
                        html.Div(className='rule-parameter-value', children=[v]))
                       for k, v in parameters.items()]
    return \
        html.Div(
            className='rule',
            children=[
                html.P(f'- {name}', style={'color': color}),
                html.Div(
                    className='rule-parameters',
                    children=[element for pair in html_parameters for element in pair]
                )
            ]
        )


def render_rule_set(rule_set: Dict[str, Set[Rule]], title: str = 'Rule Set') -> html.Div:
    """ Render a Nakamoto rule set. """
    rules, stop_rules = rule_set['rule_set'], rule_set['stop_rules']
    rules, stop_rules = list(rules), list(stop_rules)
    rules = rules + stop_rules
    return \
        html.Div(
            className='rule-set',
            children=[html.P(title), html.Div()] + [render_rule(rule) for rule in rules]
        )


def render_simulation_df(df: DataFrame) -> DataTable:
    """ Render a Nakamoto simulation DataFrame as a Dash DataTable. """
    simulation_df = df.copy()
    simulation_df['datetime'] = simulation_df.index
    simulation_df = simulation_df[['datetime'] + [col for col in simulation_df.columns
                                                  if col not in ['datetime']]]
    simulation_df['datetime'] = simulation_df['datetime'].apply(utils.format_datetime_element)
    conditional_styles = [
        {'if': {'filter_query': '{action} = "sale"'},
         'backgroundColor': styles.DARK_RED},
        {'if': {'filter_query': '{action} = "purchase"'},
         'backgroundColor': styles.DARK_GREEN},
        {'if': {'filter_query': '{action} contains "failed"',
                'column_id': 'action'},
         'backgroundColor': styles.TABLE_CELL_HIGHLIGHTED}
    ]
    return render_table(simulation_df, conditional_styles=conditional_styles)


def render_table(df: DataFrame, n_decimals: int = 8, use_tooltip: bool = True,
                 conditional_styles: List[dict] = None) -> DataTable:
    """ Render a Dash DataTable using a DataFrame. Watch out: index is ignored. """
    data_table_kwargs = {
        'columns': [{'name': i, 'id': i} for i in df.columns],
        'data': df.round(n_decimals).to_dict('records'),
        'fixed_rows': {'headers': True},
        'style_table': styles.table_style,
        'style_header': styles.table_header_style,
        'style_data': styles.table_data_style,
        'style_data_conditional': [
            {'if': {'row_index': 'odd'}, **styles.table_odd_rows_style},
            {'if': {'state': 'selected'}, **styles.table_select_style},
        ],
        'style_cell': styles.table_cell_style,
    }
    if conditional_styles:
        data_table_kwargs['style_data_conditional'].extend(conditional_styles)
    if use_tooltip:
        data_table_kwargs.update({
            'tooltip_header': {i: i for i in df.columns},
            'tooltip_data': [{column: {'value': str(value), 'type': 'markdown'}
                              for column, value in row.items()}
                             for row in df.to_dict('records')],
            'tooltip_duration': None,
            # TODO 2022.02.09 These styles are ugly there. But watch out: they are difficult to check.
            'css': [
                {'selector': '.dash-table-tooltip',
                 'rule': f'background-color: {styles.MENU_BACKGROUND}; '
                         f'font-family: monospace; '
                         f'min-width: 160px; '
                         f'max-width: 160px; '
                         f'border-bottom-color: {styles.MENU_BACKGROUND}; '
                         f'color: {styles.TEXT_COLOR}; '
                         f'text-align: center; '},
                {'selector': '.dash-tooltip',
                 'rule': f'border-color: {styles.BORDER_COLOR};'},
                {'selector': '.dash-tooltip:before',
                 'rule': f'border-bottom-color: {styles.BORDER_COLOR};'},
                {'selector': '.dash-tooltip:after',
                 'rule': f'border-bottom-color: {styles.MENU_BACKGROUND};'}
            ]}
        )
    return DataTable(**data_table_kwargs)
