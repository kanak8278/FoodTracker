from flask import Flask, render_template, redirect, g, url_for, request
import sqlite3
from datetime import datetime
app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect('/Users/kanakraj/PycharmProjects/FoodTracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite3_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')
        # pretty_date = datetime.strftime(database_date, '%B %d, %Y')
        db.execute('insert into log_date (entry_date) values (?)',\
                   [database_date])
        db.commit()
        # return str(pretty_date)
    cur = db.execute('select log_date.entry_date as entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories from log_date left join food_date on food_date.log_date_id = log_date.id left join food on food.id = food_date.food_id group by log_date.entry_date order by log_date.entry_date desc ')
    results = cur.fetchall()

    date_cur = db.execute('select entry_date from log_date order by entry_date desc')
    day = date_cur.fetchall()

    # date_results = []
    #
    # for date in day:
    #     single_date = {}
    #     single_date['date'] = date['entry_date']
    #     d = datetime.strptime(str(date['entry_date']), '%Y%m%d')
    #     single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
    #     date_results.append(single_date)

    date_results = []
    for date in results:
        single_date = {}

        single_date['date'] = date['entry_date']
        single_date['protein'] = date['protein']
        single_date['carbohydrates'] = date['carbohydrates']
        single_date['fat'] = date['fat']
        single_date['calories'] = date['calories']

        d = datetime.strptime(str(date['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
        date_results.append(single_date)

    return render_template('home.html', results=date_results)


@app.route('/view/<date>', methods=['POST', 'GET'])
def view(date):
    db = get_db()

    cur = db.execute('select id, entry_date from log_date where entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        # date_id = date_result['id']
        # return date_id
        food_id = request.form['food-select']
        date_id = date_result['id']
        db.execute('insert into food_date (food_id, log_date_id) values (?, ?)', [food_id, date_id])
        db.commit()
        # return '<h1>The food item selected is #{}, Date:{}</h1>'.format(request.form['food-select'],date_result['id'])

    d = datetime.strptime(str(date_result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')
     # return pretty_date

    food_cur = db.execute('Select id, name from food')
    food_result = food_cur.fetchall()

    log_cur = db.execute('select food.name, food.protein, food.carbohydrates, food.fat, food.calories\
                        from log_date join food_date on food_date.log_date_id = log_date.id\
                        join food on food.id = food_date.food_id where log_date.entry_date = ?', [date])
    log_results = log_cur.fetchall()
    # return log_results

    totals = {}
    totals['protein']=0
    totals['carbohydrates']=0
    totals['calories']=0
    totals['fat']=0

    for food in log_results:
        totals['protein'] += food['protein']
        totals['carbohydrates'] += food['carbohydrates']
        totals['calories'] += food['calories']
        totals['fat'] += food['fat']


    return render_template('day.html',entry_date= date_result['entry_date'], pretty_date=pretty_date, food_result=food_result, log_results=log_results, totals=totals)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        calories = protein*4 + carbohydrates*4 + fat*9

        db.execute('insert into food (name, protein, carbohydrates, fat, calories) values (?,?,?,?,?)', \
                   [name, protein, carbohydrates, fat, calories])
        db.commit()
        # return '<h1>Name: {} Protein: {} Carbo: {} Fat:{}</h1>'.format(name, protein, carbohydrates, fat)

    cur = db.execute('select name, protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
