
from dash import Dash, callback_context, dcc, html
from dash.dependencies import Input, Output

from nakamoto_explorer import input_data
from nakamoto_explorer import renders
from nakamoto_explorer.settings import DEBUG_MODE


app = Dash(__name__)
app.title = 'Trading Bot Dashboard'
server = app.server

data = input_data.load_data()

app.layout = html.Div(
    className='dashboard',
    children=[
        html.Div(
            className='nakamoto-banner',
            children=[
                html.H2('Trading Bot Dashboard'),
                html.A(
                    id='banner-link',
                    children=['View on GitHub'],
                    href='https://github.com/carlospinto93p/NakamotoExplorer'
                ),
                html.Img(src=app.get_asset_url('github_logo.png')),
            ],
        ),
        html.Div(
            className='container',
            children=[
                html.Div(
                    id='content',
                    className='content',
                    children=[
                        html.Div(
                            className='main-table',
                            children=[
                                renders.render_simulation_df(data[0]['simulation_df'])
                            ],
                        ),
                        renders.render_simulation_line_graphs(data[0]['simulation_df']),
                        renders.render_metrics(data[0]['metrics']),
                    ]
                ),
                html.Div(
                    className='left-panel',
                    children=[
                        html.Div(
                            className='page-settings',
                            children=[
                                html.P(['Study Design']),
                                html.Div(
                                    className='settings-row',
                                    children=[
                                        html.Label(['Mock index']),
                                        html.Div(id='mock-index', children=['0 / 75'])
                                    ]
                                ),
                                html.Div(
                                    className='settings-row',
                                    children=[
                                        html.Label(['Price list']),
                                        html.Div([
                                            dcc.Input(
                                                id='price-list',
                                                type='number',
                                                value=1,
                                                min=1,
                                                max=input_data.get_max_price_list_idx(data),
                                            )]
                                        )]
                                ),
                                html.Div(
                                    className='settings-row',
                                    children=[
                                        html.Label(['Rule Set']),
                                        html.Div([
                                            dcc.Input(
                                                id='rule-set',
                                                type='number',
                                                value=1,
                                                min=1,
                                                max=input_data.get_max_rule_set_idx(data),
                                            )]
                                        )]
                                ),
                                html.Div(
                                    className='settings-row',
                                    children=[
                                        html.Div([
                                            html.Button(
                                                id='prev-simulation',
                                                children=['Prev'],
                                            ),
                                            html.Button(
                                                id='next-simulation',
                                                children=['Next'],
                                            )]
                                        )]
                                ),
                            ]
                        ),
                        html.Div(
                            id='rule-sets',
                            children=[
                                html.Div(
                                    className='rule-sets',
                                    children=[
                                        renders.render_rule_set(data[0]['rule_set_kwargs'])
                                    ]
                                )]
                        )

                    ]
                ),
                html.Div(
                    className='clearing-div',
                    children=[]
                )
            ],
        )
    ]
)


@app.callback(
    Output('content', 'children'),
    Output('mock-index', 'children'),
    Output('price-list', 'value'),
    Output('rule-set', 'value'),
    Output('rule-sets', 'children'),
    [Input('next-simulation', 'n_clicks'),
     Input('prev-simulation', 'n_clicks'),
     Input('price-list', 'value'),
     Input('rule-set', 'value')])
def update_interaction(next_n_clicks: int, prev_n_clicks: int,
                       price_list_idx: int, rule_set_idx: int):
    idx, context = 0, callback_context
    if context.triggered:
        idx = input_data.get_data_idx(data, price_list_idx=price_list_idx,
                                      rule_set_idx=rule_set_idx)
        last_trigger = context.triggered[0]['prop_id'].split('.')[0]
        if last_trigger == 'next-simulation':
            idx += 1
        elif last_trigger == 'prev-simulation':
            idx -= 1
    idx = idx % len(data)
    data_element = data[idx]
    return (
        [
            html.Div(
                className='main-table',
                children=[
                    renders.render_simulation_df(data_element['simulation_df'])
                ],
            ),
            renders.render_simulation_line_graphs(data_element['simulation_df']),
            renders.render_metrics(data_element['metrics'])],
        [f'{idx} / {len(data)}'],
        data_element['identifier']['price_list'],
        data_element['identifier']['rule_set'],
        [
            html.Div(
                className='rule-sets',
                children=[
                    renders.render_rule_set(data_element['rule_set_kwargs'])
                ])]
    )


if __name__ == '__main__':
    app.run_server(debug=DEBUG_MODE)
