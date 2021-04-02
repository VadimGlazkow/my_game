from flask import Flask
import os

app = Flask(__name__)


@app.route('/')
def choice_planet():
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
                    <h1>Мое предложение: Марс</h1>
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)