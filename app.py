from flask import Flask,render_template,request,redirect,url_for,g
import sqlite3
from datetime import datetime

app=Flask(__name__)
DATABASE = 'D:/food tracker/database/food.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()		

@app.route("/",methods=['GET','POST'])
def home():
	db=get_db()
	if request.method=='POST':
		date = request.form['date']

		dt=datetime.strptime(date,'%Y-%m-%d')
		database_date=datetime.strftime(dt,'%Y%m%d')

		db.execute('insert into log_date (entry_date) values(?)',[database_date])
		db.commit()
		
	cur=db.execute('select log_date.entry_date,  sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id=log_date.id left join food on food.id=food_date.food_id group by log_date.id order by log_date.entry_date DESC')
	results=cur.fetchall()	

	date_results=[]

	for i in results:
		single_date={}
		single_date['entry_date']=i[0]
		single_date['protein']=i[1]
		single_date['carbohydrates']=i[2]
		single_date['fat']=i[3]
		single_date['calories']=i[4]

		d=datetime.strptime(str(i[0]), '%Y%m%d')
		single_date['pretty_date']=datetime.strftime(d,'%B %d %Y')
		
		date_results.append(single_date)

	return render_template("home.html",results=date_results)


@app.route("/addfood", methods=['GET','POST'])
def addfood():
	db=get_db()
	if request.method=='POST':
		name=request.form['food-name']
		protein=int(request.form['protein'])
		carbohydrates=int(request.form['carbohydrates'])
		fat=int(request.form['fat'])
		calories=protein*4 + carbohydrates*4 + fat*9
        
		db.execute('insert into food(name,protein,carbohydrates,fat,calories) values(?,?,?,?,?)', \
		[name,protein,carbohydrates,fat,calories])
		db.commit()
	cur=db.execute('select name,protein,carbohydrates,fat,calories from food')
	results=cur.fetchall()
	return render_template('addfood.html',results=results)

@app.route('/view/<date>',methods=['GET','POST'])
def view(date):
	db=get_db()
	cur=db.execute('select id,entry_date from log_date where entry_date = ? ',[date])
	date_result=cur.fetchone()

	if request.method=='POST':
		db.execute('insert into food_date (food_id, log_date_id) values (?,?)',[request.form['food-select'], date_result[0]])
		db.commit()

	
	
	d=datetime.strptime(str(date_result[1]), '%Y%m%d')

	pretty_date=datetime.strftime(d,' %B %d %Y')

	food_cur=db.execute('select id, name from food')
	food_result=food_cur.fetchall()

	log_cur=db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories from log_date join food_date on food_date.log_date_id=log_date.id join food on food.id=food_date.food_id where log_date.entry_date=?',[date])
	log_results=log_cur.fetchall()

	totals={'protein':0, 'carbohydrates':0,'fat':0,'calories':0}
	

	for food in log_results:
		totals['protein']+=int(food[1])
		totals['carbohydrates']+=int(food[2])
		totals['fat']+=int(food[3])
		totals['calories']+=int(food[4])



	return render_template('view.html',entry_date=date_result[1],pretty_date=pretty_date,food_result=food_result,log_results=log_results,totals=totals)


app.run(debug=True)	
