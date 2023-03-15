from database import Database
from modeling import Modeling
from visualizations import Visualizations

# Connect to the database
database = Database(dbname='mydatabase', user='myusername', password='mypassword')

# Load data from the database
database.load_data()

# Create a modeling object
modeling = Modeling(database)

# Fit the models to the data
modeling.fit_models()

# Create a visualizations object
visualizations = Visualizations(database, modeling)

# Plot a histogram of product prices
visualizations.plot_histogram('product_price')

# Plot a scatter plot of product prices vs. product quantity
visualizations.plot_scatter('product_price', 'product_quantity')

# Plot the customer lifetime value over time for customer ID ?
# visualizations.plot_clv(?, 12)
