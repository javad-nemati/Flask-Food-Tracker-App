from flask import Flask, render_template, g, request, redirect
import mariadb
from datetime import datetime
from database import connect_db,get_db
app = Flask(__name__)



@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'mariadb_db'):
        g.mariadb_db.close()

@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']
        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y-%m-%d')
        cur = db.cursor()
        cur.execute('INSERT INTO log_date (entry_date) VALUES (?)', [database_date])
        return redirect('/')
    cur = db.cursor()
    cur.execute('select log_date.entry_date, sum(food.protein) as protein, sum(food.carbohydrates) as carbohydrates, sum(food.fat) as fat, sum(food.calories) as calories \
                from log_date \
                left join food_date on food_date.log_date_id = log_date.id \
                left join food on food.id = food_date.food_id group by log_date.id order by log_date.entry_date desc')
    results = cur.fetchall()
    #pretty_results = []
    date_results = []
    for i in results:
        single_date = {}
        single_date['entry_date'] = i[0]
        single_date['protein'] = i[1]
        single_date['carbohydrates'] = i[2]
        single_date['fat'] = i[3]
        single_date['calories'] = i[4]
        d = datetime.strptime(str(i[0]), '%Y-%m-%d')
        single_date['pretty_date'] = datetime.strftime(d, '%B %d, %Y')
        date_results.append(single_date)

    return render_template('home.html', results=date_results)


@app.route('/view/<date>', methods=['GET', 'POST'])
def view(date):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT id, entry_date FROM log_date WHERE entry_date = ?', [date])
    date_result = cur.fetchone()

    if request.method == 'POST':
        food_id = request.form['food-select']
        log_date_id = date_result[0]
        cur.execute('INSERT INTO food_date (food_id, log_date_id) VALUES (?, ?)', [food_id, log_date_id])

    d = datetime.strptime(str(date_result[1]), '%Y-%m-%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')
    
    cur.execute('SELECT id, name FROM food')
    food_results = cur.fetchall()

    cur.execute('SELECT food.name, food.protein, food.carbohydrates, food.fat, food.calories ' \
                'FROM food ' \
                'JOIN food_date ON food.id = food_date.food_id ' \
                'JOIN log_date ON log_date.id = food_date.log_date_id ' \
                'WHERE log_date.entry_date = ?', [date])
    log_results = cur.fetchall()
    
    totals = {
        'protein': sum(food[1] for food in log_results),
        'carbohydrates': sum(food[2] for food in log_results),
        'fat': sum(food[3] for food in log_results),
        'calories': sum(food[4] for food in log_results)
    }

    return render_template('day.html', entry_date=date_result[1], date=pretty_date, food_results=food_results, log_results=log_results, totals=totals)



@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()

    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        cur = db.cursor()
        cur.execute('INSERT INTO food (name, protein, carbohydrates, fat, calories) VALUES (?, ?, ?, ?, ?)',
                    [name, protein, carbohydrates, fat, calories])

        return redirect('/food')

    cur = db.cursor()
    cur.execute('SELECT name, protein, carbohydrates, fat, calories FROM food')
    results = cur.fetchall()

    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)