from flask import Flask,render_template,session,request,redirect,url_for,jsonify
import requests
from pymongo import MongoClient
import os
app = Flask(__name__)
app.secret_key = "4c15ecd572abf8862666257ae104126084a1202187b925bd4dd99e1990ec6254"
app.config['MONGO_URI'] = 'mongodb+srv://maheshduggi456:Mahesh123@murali.ztmq9oy.mongodb.net/?retryWrites=true&w=majority&appName=AtlasApp'
mongo_uri = app.config['MONGO_URI']
mongo = MongoClient(mongo_uri)
db = mongo.get_database('Codechef')
leetcode_url = "https://leetcode.com/graphql"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"  # Customize with an appropriate user agent
}

admin_collection = db['Admin']
employee_collection = db['Employees']
students_collection = db['students']
role=""
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
    },
    {
        "Name":"Baker",
        "Date":"23-Feb-2023",
        "Place": "Me-3 Lab",
        "Content" : "A event about the Cooking problems"
    }
]

@app.route("/")
def home():
    return render_template('index.html',events=events)
@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'POST':
        uname = request.form['emailid']
        upass = request.form['password']
        admin = admin_collection.find_one({'emailid': uname, 'password': upass})
        if admin:
            session['username'] = admin['name']
            session['user_logged_in'] = True
            session['is_admin'] = True
            a={
                "emailid" :"mahesh@gmail.com",
                "password" :"mahesh",
                "name" :"Mahesh Duggi",
                "role" :"admin",
                "Balance" :"5000"
            }
            session['data']=a
            print(str(session['data'])+" hello")
            return render_template('admin.html')
        else:
            emp = employee_collection.find_one({'emailid':uname, 'Password':upass})
            if emp:
                session['username'] = emp['Name']
                session['user_logged_in'] = True
                session['is_admin'] = False
                return redirect(url_for('myaccount'))
            else:
                std = students_collection.find_one({'Email':uname, 'Password':upass})
                if std:
                    session['username'] = std['Name']
                    session['user_logged_in'] = True
                    session['is_admin'] = False
                    return redirect(url_for('myaccount'))
                else:
                    return render_template('login.html', msg="Invalid credentials")
            
    return render_template('login.html')
@app.route("/logout",methods=['POST','GET'])
def logout():
    session.pop('user_logged_in', None)
    return redirect(url_for('home'))
@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        uid = request.form['leetcode']
        ema = request.form['email']
        pas = request.form['pass']
        students_collection.insert_one({'Name':name,"Leetcodeid":uid,"Email":ema,"Password":pas})
        return redirect(url_for('login'))
    else:    
        return  render_template('signup.html')


def get_user_statistics(username):
    # Define the query and variables
    query = """
    query userProblemsSolved($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        matchedUser(username: $username) {
            problemsSolvedBeatsStats {
                difficulty
                percentage
            }
            submitStatsGlobal {
                acSubmissionNum {
                    difficulty
                    count
                }
            }
        }
    }
    """
    
    variables = {
        "username": username
    }

    data = {"query": query, "variables": variables}

    # Make the POST request to the LeetCode API
    response = requests.post(leetcode_url, json=data, headers=headers)

    if response.status_code == 200:
        response_data = response.json()

        total_solved = next(item['count'] for item in response_data['data']['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if item['difficulty'] == 'All')
        easy_solved = next(item['count'] for item in response_data['data']['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if item['difficulty'] == 'Easy')
        medium_solved = next(item['count'] for item in response_data['data']['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if item['difficulty'] == 'Medium')
        hard_solved = next(item['count'] for item in response_data['data']['matchedUser']['submitStatsGlobal']['acSubmissionNum'] if item['difficulty'] == 'Hard')

        return {
            "username": username,
            "total_solved": total_solved,
            "easy_solved": easy_solved,
            "medium_solved": medium_solved,
            "hard_solved": hard_solved
        }

    return None
@app.route('/myaccount')
def myaccount():
    if 'user_logged_in' in session and session['user_logged_in'] is True:
        if session['is_admin']==False:
            username = []
            user_ids = students_collection.distinct('Leetcodeid')
            for user in user_ids:
                username.append(user)
            search_key = "Name"
            search_value = session['username']
            result = students_collection.find({search_key: search_value})
            user_stats = []
            for username in username:
                stats = get_user_statistics(username)
                if stats!= None:
                    user_stats.append(stats)
            sd = sorted(user_stats, key=lambda x: x['total_solved'])
            sd=sd[::-1]
            d=[]
            for i in result:
                d.append(i)
            return render_template('profile.html',msg = sd,event=get_user_statistics(d[0]['Leetcodeid']))            
        else:
            return render_template('admin.html')
    else:
        return redirect(url_for('home'))
@app.route('/addvolun',methods=['GET','POST'])
def addvolun():
    if request.method=='POST':
        name= request.form.get('name')
        selected_role = request.form.get('selected_role')
        username = request.form.get('username')
        employee_collection.insert_one(
        {
            "Name" : name,
            "Username" : username,
            "Role": selected_role,
            "Password" : request.form.get('password'),
            "emailid" : request.form.get('email')
        })
        return render_template('admin.html',msg="Success")
    else:
        return render_template('admin.html')
@app.route('/solve')
def solve():
    if 'user_logged_in' in session and session['user_logged_in'] is True:
        return render_template('solve.html')
    else:
        return redirect(url_for('login'))

@app.route('/removevolun',methods=['GET','POST'])
def removevolun():
    if request.method=='POST':
        username = request.form.get('username')
        result = employee_collection.delete_one(
        {
            "Username" : username
        })
        if result.deleted_count > 0:
            return render_template('admin.html',msg2="Sucess")
        else:
            return render_template('admin.html')
    else:
        return render_template('admin.html',msg2="")
@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

if __name__ == '__main__':
    app.run(debug=True)