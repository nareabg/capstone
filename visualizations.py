import matplotlib.pyplot as plt
import seaborn as sns

class Visualizations:
    def __init__(self, database, modeling):
        self.database = database
        self.modeling = modeling

    def plot_histogram(self, column):
        """
        Plots a histogram of the specified column.
        """
        data = pd.DataFrame(self.database.get_data(), columns=['purchase_date', 'customer_id', 'product_price',
                                                                     'product_quantity', 'gender', 'location'])
        sns.histplot(data[column])
        plt.show()

    def plot_scatter(self, x_column, y_column):
        """
        Plots a scatter plot of the specified columns.
        """
        data = pd.DataFrame(self.database.get_data(), columns=['purchase_date', 'customer_id', 'product_price',
                                                                     'product_quantity', 'gender', 'location'])
        sns.scatterplot(data=data, x=x_column, y=y_column)
        plt.show()

    def plot_clv(self, customer_id, time_period):
        """
        Plots the customer lifetime value over time for the specified customer.
        """
        self.modeling.load_data()
        self.modeling.fit_models()

        # Compute the CLV for each month in the time period
        clv = []
        for i in range(time_period):
            clv.append(self.modeling.predict_clv(customer_id, i+1))

        # Plot the CLV over time
        plt.plot(range(1, time_period+1), clv)
        plt.xlabel('Time (months)')
        plt.ylabel('Customer Lifetime Value ($)')
        plt.title('Customer Lifetime Value over Time')
        plt.show()
