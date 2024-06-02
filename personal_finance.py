"""
PersonalFinance class, define with person's name
attrib .data: a pandas DataFrame with entries, columns: ['date', 'category', 'title', 'amount', 'notes']
attrib .barchart: barchart in the form of a DataFrame, with the category, category sum ('amount'), and height (log scale of amount)

 ／l、
（ﾟ､ ｡ ７
  l  ~ヽ
  じしf_,)ノ
"""

import pandas as pd
from pandas import Period
from datetime import datetime as dt
import numpy as np
import os

class PersonalFinance:
    def __init__(self, name: str):
        self.name = name
        # initialize dataframe with these columns
        self.data = pd.DataFrame(columns=['date', 'category', 'title', 'amount', 'notes'])

        # dataframe for totals is stored here. also includes month
        self._cat_totals = pd.DataFrame(columns=['category', 'amount'])

        # daily totals
        self._daily_totals = pd.DataFrame(columns=['date', 'amount'])

    def new_entry(self, date: dt.date, category: str, title: str, amount: float, notes: str = ' ') -> None:
        new_row = pd.DataFrame([{
            'date': date,
            'category': category,
            'title': title,
            'amount': amount,
            'notes': notes
        }])
        self.data = pd.concat([self.data, new_row], ignore_index=True)

    @property
    def _temp_data(self) -> pd.DataFrame:
        # data with month, internally stored because redundant w date
        df = self.data.copy()
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')
        return df

    @property
    def cat_totals(self) -> pd.DataFrame | None:
        # totals by category irrespective of month
        if not self._temp_data.empty:
            # df = self._temp_data['amount'].apply(lambda amt: float(amt)) # make sure all in float
            return self._temp_data[['category', 'amount']].groupby('category').sum().reset_index()
        else:
            return None

    @property
    def daily_totals(self) -> pd.DataFrame:
        if self._daily_totals.empty:
            self._daily_totals = self.data[['date', 'amount']].groupby('date').sum().reset_index()
        else:
            1==1
        return self._daily_totals

    def monthly_cat_totals(self, month: Period) -> pd.DataFrame | None:
        if month in list(set(self._temp_data['month'])):
            return self._temp_data[self._temp_data['month'] == month][['category', 'amount']].groupby('category').sum().reset_index()
        else:
            return self.cat_totals

    def delete_index(self, index: int) -> None:
        if index in self.data.index:
            self.data = self.data.drop(index=index)
            self.data = self.data.reset_index(drop=True)[['date', 'category', 'title', 'amount', 'notes']]
        else:
            raise IndexError('Index not found')

    def dump(self) -> None:
        self.data.to_csv(f'personal_finance_{self.name}.csv', index=False)

    def load(self) -> None:
        assert os.path.exists(f'personal_finance_{self.name}.csv')
        self.data = pd.read_csv(f'personal_finance_{self.name}.csv')[['date', 'category', 'title', 'amount', 'notes']]
        self.data['date'] = self.data['date'].apply(lambda date: date[:10])
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data['amount'] = self.data['amount'].apply(lambda amt: np.round(amt, 2))
        self._cat_totals = pd.DataFrame(columns=['category', 'amount'])


