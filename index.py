import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import page_2, page_3


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/page_2':
        return page_2.layout
    elif pathname == '/apps/page_3':
        return page_3.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)