from flask import Flask

app = Flask(__name__)
app.config['DEBUG'] = True  # Enable debug mode

@app.route('/')
def home():
    return "Hello, karim!"

if __name__ == '__main__':
    app.run()
