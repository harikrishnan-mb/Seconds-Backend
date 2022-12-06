from createapp import get_app
from database import get_db

app = get_app()
db = get_db()


@app.route('/home')
def home():
    return "Seconds Backend"


if __name__ == '__main__':
    app.run(port=5001)
