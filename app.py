from flask import Flask, render_template, request, redirect, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payments.db'
db = SQLAlchemy(app)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    tax_rate = db.Column(db.Float, nullable=False)


def format_date_mmddyyyy(date):
    if date:
        return date.strftime('%m/%d/%Y')
    return 'NA'

@app.route('/summary')
def summary():
    due_date = request.args.get('dueDate')
    print("ss",due_date)
    parsed_time = datetime.datetime.strptime(due_date, '%m/%d/%Y')
    due_date = parsed_time.strftime('%Y-%m-%d')
    payments = Payment.query.all()
    total_amount = sum(payment.amount for payment in payments)
    tax_rate = payments[0].tax_rate if payments else 0
    tax_due = total_amount * tax_rate
    print("ksnsk",jsonify(payments));

    html = '<table border="1"><tr><th>ID</th><th>Company</th><th>Amount</th><th>Payment Dates</th><th>Status</th><th>Due Date</th></tr>'
    for payment in payments:
        payment_date = payment.payment_date if payment.payment_date else None
        formatted_date = format_date_mmddyyyy(payment_date)
        html += f'<tr><td>{payment.id}</td><td>{payment.company}</td><td>{payment.amount}</td><td>{formatted_date}</td><td>{payment.status}</td><td>{payment.due_date}</td>'
        # Uncomment the following lines if you need buttons
        # html += f'<button onclick="openEditPopup({payment.id}, \'{payment.company}\', {payment.amount}, \'{payment.payment_date}\', \'{payment.status}\', \'{payment.due_date}\', {payment.tax_rate})">Edit</button>'
        # html += f'<button onclick="deleteRecord({payment.id})">Delete</button>'
        html += '</td></tr>'
    html += f'<tr><td colspan="5"><strong>Total Amount:</strong></td><td>&dollar;{total_amount}</td></tr><tr><td colspan="5"><strong>Tax Rate:</strong></td><td>{tax_rate}%</td></tr><tr><td colspan="5"><strong>Tax Due:</strong></td><td>&dollar;{tax_due}</td></tr>'
    html += '</table>'

    return jsonify({'html': html})


# Create all database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    current_year = datetime.datetime.now().year
    next_year = current_year + 1
    due_dates = [
        f"04/15/{current_year}",
        f"06/15/{current_year}",
        f"09/15/{current_year}",
        f"01/15/{next_year}"
    ]
    payments = Payment.query.all()
    print("due_dates",due_dates)
    return render_template('home.html',due_dates=due_dates, payments=payments)

@app.route('/add_payment', methods=['POST'])
def add_payment():
    if request.method == 'POST':
        company_name = request.form['company_name']
        amount = float(request.form['amount'])
        payment_date = datetime.datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
        status = request.form['status']
        due_date = datetime.datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        tax_rate = float(request.form['tax_rate'])
        print("sks",due_date)
        new_payment = Payment(company_name=company_name, amount=amount, 
                              payment_date=payment_date, status=status, 
                              due_date=due_date, tax_rate=tax_rate)
        db.session.add(new_payment)
        db.session.commit()

    return redirect(url_for('home'))

@app.route('/update_payment/<int:id>', methods=['GET', 'POST'])
def update_payment(id):
    payment = Payment.query.get_or_404(id)
    if request.method == 'POST':
        payment.company_name = request.form['company_name']
        payment.amount = float(request.form['amount'])
        payment.payment_date = datetime.datetime.strptime(request.form['payment_date'], '%Y-%m-%d').date()
        payment.status = request.form['status']
        payment.due_date = datetime.datetime.strptime(request.form['due_date'], '%Y-%m-%d').date()
        payment.tax_rate = float(request.form['tax_rate'])
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('update_payment.html', payment=payment)

@app.route('/delete_payment/<int:id>', methods=['POST'])
def delete_payment(id):
    payment = Payment.query.get_or_404(id)
    db.session.delete(payment)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
