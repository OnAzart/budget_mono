import pandas as pd
import matplotlib as mp
import matplotlib.pyplot as plt
from os.path import join

from additional_tools import working_directory


class Plot:
    def __init__(self, payments, category=False, weekday_to_time=True):
        self.payments_df = self.produce_detailed_statistic(payments)
        self.images = {'category': None, 'weekday_to_time': None}
        if category:
            self.category_bar_plot()
        if weekday_to_time:
            self.weekday_to_time_scatter_plot()

    def produce_detailed_statistic(self, pays):
        payments_df = pd.DataFrame(pays)
        columns = ['time', 'amount', 'currencyCode', 'cashbackAmount', 'wider_category', 'account_id', 'description']
        payments_df = payments_df[columns]
        payments_df.loc[:, 'amount'] = payments_df['amount'] / 100

        payments_df['timestamp'] = payments_df['time']
        payments_df['datetime'] = pd.to_datetime(payments_df['timestamp'], unit='s')
        payments_df['date'] = payments_df['datetime'].dt.date
        payments_df['time'] = payments_df['datetime'].dt.time
        payments_df['day_of_week'] = payments_df['datetime'].dt.strftime('%A')
        payments_df['hour'] = payments_df['datetime'].dt.hour
        # self.payments_df = payments_df
        return payments_df

    def category_bar_plot(self):
        # payments_df.sort_values(by='timestamp', inplace=True)
        # __________________________________________________________________________
        # GROUPING
        grouped_by_category_df = self.payments_df.groupby(by='wider_category')\
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

        plt.title('Категорії')
        plt.xlabel('Витрачено (грн)', fontsize=15, fontweight='black', color='#333F4B')
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
        self.images['category'] = path_to_save_category

    def weekday_to_time_scatter_plot(self):
        payment_df = self.payments_df.sort_values(by='timestamp')
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
        plt.show()
        plt.close()
        self.images['weekday_to_time'] = path_to_save_weekday_to_time

    def get_plots_paths(self):
        return self.images.values()
