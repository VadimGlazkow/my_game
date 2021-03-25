from flask import Flask

app = Flask(__name__)


@app.route('/')
def title():
    return 'Миссия Колонизация Марса'


@app.route('/choice/<planet_name>')
def choice_planet(planet_name):
    return f'''<!doctype html>
                <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
                    <link rel="stylesheet" 
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                    crossorigin="anonymous">
                   <title>Варианты выбора</title>
                </head>
                <body>
                    <h1>Мое предложение: {planet_name}</h1>
                    <h3 class="alert alert-light" role="alert">
                        Эта планета близка к Земле;
                    </h3>
                    <h3 class="alert alert-success" role="alert">
                        На ней много необходимых ресурсов;
                    </h3>
                    <h3 class="alert alert-secondary" role="alert">
                        На ней есть вода и атмосфера;
                    </h3>
                    <h3 class="alert alert-warning" role="alert">
                        На ней есть небольшое магнитное поле;
                    </h3>
                    <h3 class="alert alert-danger" role="alert">
                        Наконец, она просто красива!
                    </h3>
                </body>
                </html>'''


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
