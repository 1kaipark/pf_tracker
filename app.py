import numpy as np
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import pandas as pd
from pandas import Period
import matplotlib.pyplot as plt
import seaborn as sns

import io
import base64


from personal_finance import PersonalFinance

app = Flask(__name__)
app.config['SECRET_KEY'] = 'HELLO999BLUD666'


class ExpenseForm(FlaskForm):
    """form to create new expense"""
    # date entry
    date = DateField('date', format='%Y-%m-%d', validators=[DataRequired()])

    # category entry
    category = SelectField('category',
                           choices=[('living', 'LIVING🏡'), ('food', 'FOOD🍔'), ('transport', 'TRANSPORT🚗'), ('fun', 'FUN😹'),
                                    ('education', 'EDUCATION🤓'), ('savings', 'SAVINGS🤑')], validators=[DataRequired()])

    # title of expense entry
    title = StringField('title', validators=[DataRequired()])

    # amount entry
    amount = FloatField('amount', validators=[DataRequired()])

    # optional notes
    notes = TextAreaField('notes')

    # submit button
    submit = SubmitField('add')

class DeleteForm(FlaskForm):
    """form to delete an index"""
    index = IntegerField('index', validators=[DataRequired()])
    confirm = SubmitField('CONFIRM DELETE')

personal_finance = PersonalFinance('user')

# try to load save
try:
    personal_finance.load()
except AssertionError:
    print('no data found for {}'.format(personal_finance.name))

@app.route('/', methods=['GET', 'POST'])
def index():
    # from the month selector -> url (/?month=XXX)
    month = request.args.get('month')
    if month != 'ALL':
        month = Period(month, 'M')
        # else, month = 'ALL', which will return the sum from monthly_cat_totals
    form = ExpenseForm()
    if form.validate_on_submit():
        date = str(form.date.data)
        category = form.category.data
        title = form.title.data
        amount = form.amount.data
        notes = form.notes.data if form.notes.data else " "
        personal_finance.new_entry(date, category, title, amount, notes)
        personal_finance.dump()
        return redirect(url_for('index'))

    # month selector
    months = ['ALL'] + list(set(personal_finance._temp_data['month']))

    try:
        month_data = personal_finance.monthly_cat_totals(month = month)
        month_data['height'] = month_data['amount'].apply(np.log)
    except Exception:
        month_data = pd.DataFrame(columns=['category', 'amount', 'height'])

    if not month_data.empty:
        plt.figure(figsize=(8, 4))
        sns.set_theme(style='white', color_codes=True)
        sns.set_palette('Paired')
        sns.barplot(data=month_data, x='height', y='category', width=0.5)
        sns.despine(bottom=True)
        plt.xlabel(None)
        plt.xticks(color='w')
        if type(month) == pd._libs.tslibs.nattype.NaTType:
            plt.title('ALL')
        else:
            plt.title(month)

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plot_url = 'data:image/png;base64,{}'.format(plot_url)

    else:
        plot_url = None

    # table for category totals
    cat_totals = month_data.to_dict(orient='records')
    monthly_sum = month_data['amount'].sum()
    for dict_ in cat_totals:
        dict_['amount'] = f"${format(dict_['amount'], '.2f')}"


    return render_template('index.html', form=form, months=months, cat_totals = cat_totals, plot_url=plot_url, month=month, monthly_sum=monthly_sum)

@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    # expenses table
    delete_form = DeleteForm() # to delete an index
    if delete_form.validate_on_submit():
        index = delete_form.index.data
        try:
            personal_finance.delete_index(index)
            personal_finance.dump()
            flash(f'{index} deleted', 'success')
        except IndexError:
            flash(f'UHHH', 'danger')
        return redirect(url_for('expenses'))

    expenses = personal_finance.data.to_dict('records')

    for dict_ in expenses:
        dict_['amount'] = f"${format(dict_['amount'], '.2f')}"
        dict_['date'] = str(dict_['date'])[:10]

    if not personal_finance.daily_totals.empty:
        daily_totals = personal_finance.daily_totals
        daily_totals['date'] = daily_totals['date'].apply(lambda date: str(date)[:10])

        plt.figure(figsize=(10, 3))
        sns.set_theme(style='white', color_codes=True)
        sns.set_palette('BuGn_r')
        sns.barplot(data=daily_totals, x='date', y='amount', width=0.3)
        plt.xticks(rotation=90)

        img = io.BytesIO()
        plt.tight_layout()

        plt.savefig(img, format='png')
        img.seek(0)
        daily_barchart = base64.b64encode(img.getvalue()).decode()
        daily_barchart = 'data:image/png;base64,{}'.format(daily_barchart)

    else:
        daily_barchart = None


    return render_template('expenses.html', delete_form=delete_form, expenses=expenses, daily_barchart = daily_barchart)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.197')
