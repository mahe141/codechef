from flask import Flask,render_template,session
app = Flask(__name__)
u_name="mahesh@gmail.com"
pas = "mahesh"

events=[
    {
        "Name":"Quicker",
        "Date":"22-jan-2023",
        "Place": "CCC Lab",
        "Content" : "A event about the coding"
    },
    {
        "Name":"Hacker",
        "Date":"23-jan-2023",
        "Place": "T&P Lab",
        "Content" : "A event about the coding"
    }
]

@app.route("/")
def home():
    return render_template('index.html',events=events)

if __name__ == '__main__':
    app.run(debug=True)