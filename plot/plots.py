from json import loads
from os import PathLike
from typing import Union

import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
from os.path import join

from additional_tools import working_directory
from data import data_object
from abc import ABC, abstractmethod


class Plots:
    def __init__(self, redis_token='', payments='', category=False, weekday_to_time=False, area_plot=None):
        self._payments = payments or loads(data_object.get_from_redis(redis_token))
        self._payments_df = self._produce_detailed_statistic()
        self._images = {'category': None, 'weekday_to_time': None, 'area_plot': None}
        if category:
            self._images['category'] = CategoryPlot(payments_df=self._payments_df).create_plot()
        if weekday_to_time:
            self._images['weekday_to_time'] = WeekdayToTimePlot(payments_df=self._payments_df).create_plot()
        if area_plot:
            self._choose_area_plot(dateunit=area_plot)

    def _produce_detailed_statistic(self):
        payments_df = pd.DataFrame(self._payments)
        columns = ['time', 'amount', 'currencyCode', 'cashbackAmount', 'wider_category', 'account_id', 'description']
        payments_df = payments_df[columns]
        payments_df.loc[:, 'amount'] = payments_df['amount'] / 100

        payments_df['timestamp_utc'] = payments_df['time']
        payments_df['datetime'] = pd.to_datetime(payments_df['timestamp_utc'], unit='s', utc=True).dt.tz_convert('Europe/Kiev')
        payments_df['date'] = payments_df['datetime'].dt.date
        payments_df['time'] = payments_df['datetime'].dt.time
        payments_df['day_of_week'] = payments_df['datetime'].dt.strftime('%A')
        payments_df['hour'] = payments_df['datetime'].dt.hour
        # self.payments_df = payments_df
        return payments_df

    def _choose_area_plot(self, dateunit='day'):
        dateunit_functions = {'today': DailyAreaPlot, 'week': WeeklyAreaPlot, 'month': MonthlyAreaPlot}
        right_class = dateunit_functions[dateunit]
        self._images['area_plot'] = right_class(payments_df=self._payments_df).create_plot()

    def get_plots_paths(self):
        return list(filter(lambda x: x, self._images.values()))

    def get_produced_dateframe(self):
        return self._payments_df


class Plot(ABC):
    def __init__(self, payments_df):
        self.payments_df = payments_df

    @abstractmethod
    def create_plot(self) -> Union[str, bytes, PathLike]:
        pass


class CategoryPlot(Plot):
    def create_plot(self):
        # payments_df.sort_values(by='timestamp_utc', inplace=True)
        # __________________________________________________________________________
        # GROUPING
        grouped_by_category_df = self.payments_df.groupby(by='wider_category') \
            .agg({'wider_category': 'count', 'amount': 'sum'})
        grouped_by_category_df.rename(columns={'wider_category': 'count_pays', 'amount': 'sum_spent'}, inplace=True)

        grouped_by_category_df['sum_spent'] = grouped_by_category_df['sum_spent'] * -1
        grouped_by_category_df = grouped_by_category_df[grouped_by_category_df['sum_spent'] > 0]

        grouped_by_category_df['percentage_from_total'] = round(grouped_by_category_df.sum_spent /
                                                                grouped_by_category_df.sum_spent.sum() * 100, 2)
        grouped_by_category_df = grouped_by_category_df[grouped_by_category_df['percentage_from_total'] + 0.5 > 0]
        grouped_by_category_df.sort_values(by='sum_spent', ascending=True, inplace=True)
        grouped_by_category_df['category_labels'] = grouped_by_category_df.index + ' (' + \
                                                    (grouped_by_category_df['percentage_from_total'] + 0.5).astype(
                                                        'int').astype('str') + '%)'
        # __________________________________________________________________________
        # PLOTTING
        data_normalizer = mp.colors.Normalize()
        color_map = mp.colors.LinearSegmentedColormap(
            "my_map",
            {
                "red": [(0, 0.5, 0.5),
                        (1.0, 0, 0)],
                "green": [(0, 1.0, 1.0),
                          (1.0, 0, 0)],
                "blue": [(0, 0.50, 0.5),
                         (1.0, 0.8, 0.5)]
            }
        )

        # STYLES
        rect1 = plt.barh(grouped_by_category_df.index, grouped_by_category_df['sum_spent'],
                         color=color_map(data_normalizer(grouped_by_category_df['sum_spent'].tolist())))

        plt.title('Категорії', fontsize=13, fontweight='black', color='#333F4B')
        plt.xlabel('Витрачено (грн)', fontsize=11, fontweight='black', color='#333F4B')
        # plt.ylabel('')
        plt.tight_layout()
        plt.gca().spines['right'].set_color('none')
        plt.gca().spines['top'].set_color('none')

        for i, rect in enumerate(rect1):
            width = rect.get_width()
            height = rect.get_height()
            percentage = grouped_by_category_df.iloc[i]['percentage_from_total']

            plt.annotate(str(int(percentage)) + '%', xy=(width + 1, rect.get_y() + height / 2),
                         color='black', ha='left', va='center')

        path_to_save_category = join(working_directory, 'plot/category_week_final.png')
        plt.savefig(path_to_save_category)
        # plt.show()
        plt.close()
        return path_to_save_category


class DayTimePlot(Plot, ABC):
    plt.style.use('fivethirtyeight')
    fontweight = 'black'
    color = '#333F4B'


class DailyAreaPlot(DayTimePlot):
    def create_plot(self):
        grouped_payment_df = self.payments_df.groupby(by='hour').agg({'amount': 'sum'})
        grouped_payment_df.plot(kind='area', stacked=False, color="orange", alpha=.5, legend=None)

        plt.tight_layout()
        plt.title('Статистика витрат за сьогодні', fontsize=14, fontweight=self.fontweight, color=self.color)
        plt.xlabel('Година', fontsize=11, fontweight=self.fontweight, color=self.color)
        plt.ylabel('Витрачено', fontsize=11, fontweight=self.fontweight, color=self.color)

        path_to_save_area_days = join(working_directory, 'plot/area_day.png')
        plt.savefig(path_to_save_area_days)
        # plt.show()
        plt.close()
        return path_to_save_area_days


class WeeklyAreaPlot(DayTimePlot):
    def create_plot(self):
        grouped_payment_df = self.payments_df.groupby(by='date').agg({'amount': 'sum'})
        grouped_payment_df.reset_index(inplace=True)
        grouped_payment_df['day_of_week'] = grouped_payment_df.date.astype('datetime64').dt.strftime('%A')
        grouped_payment_df.drop(columns='date', inplace=True)
        grouped_payment_df.plot(kind='area', x='day_of_week', y='amount', stacked=False, color="green", alpha=.5,
                                legend=None)
        plt.tight_layout()
        plt.title('Статистика витрат за днями цього тижня', fontsize=14, fontweight=self.fontweight, color=self.color)
        plt.xlabel('День тижня', fontsize=11, fontweight=self.fontweight, color=self.color)
        plt.xticks(rotation=25)
        plt.ylabel('Витрачено', fontsize=11, fontweight=self.fontweight, color=self.color)

        path_to_save_area_days = join(working_directory, 'plot/area_week.png')
        plt.savefig(path_to_save_area_days)
        # plt.show()
        plt.close()
        return path_to_save_area_days


class MonthlyAreaPlot(DayTimePlot):
    def create_plot(self):
        grouped_payment_df = self.payments_df.groupby(by='date').agg({'amount': 'sum'})
        grouped_payment_df.reset_index(inplace=True)
        month = grouped_payment_df.date.astype('datetime64').dt.strftime('%B')[0]
        grouped_payment_df['day_number'] = grouped_payment_df['date'].astype('datetime64').dt.strftime('%-d')
        grouped_payment_df.drop(columns='date', inplace=True)
        grouped_payment_df.plot(kind='area', x='day_number', y='amount', stacked=False, color="dodgerblue", alpha=.5,
                                legend=None)
        plt.tight_layout()
        plt.title('Статистика витрат за днями місяця', fontsize=14, fontweight=self.fontweight, color=self.color)
        plt.xlabel(f'Дні місяця "{month}"', fontsize=11, fontweight=self.fontweight, color=self.color)
        plt.ylabel('Витрачено', fontsize=11, fontweight=self.fontweight, color=self.color)

        path_to_save_area_days = join(working_directory, 'plot/area_month.png')
        plt.savefig(path_to_save_area_days)
        # plt.show()
        plt.close()
        return path_to_save_area_days


# not used plot
class WeekdayToTimePlot(Plot):
    def create_plot(self):
        payment_df = self.payments_df.sort_values(by='timestamp_utc')
        payment_df['amount'] = payment_df['amount'].abs()
        sc = plt.scatter(x=payment_df.day_of_week, y=payment_df.hour,
                         c='green', alpha=0.5)
        # plt.legend(*sc.legend_elements("sizes", num=3), loc='lower left')

        plt.title('По днях та годинах')
        plt.xlabel('Дні тижня', fontsize=15, fontweight='black', color='#333F4B')
        plt.ylabel('Години', fontsize=15, fontweight='black', color='#333F4B')
        plt.xticks(rotation=20)

        path_to_save_weekday_to_time = join(working_directory, 'plot/weekday_time_scatter.png')
        plt.savefig(path_to_save_weekday_to_time)
        # plt.show()
        plt.close()
        return path_to_save_weekday_to_time
