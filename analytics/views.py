
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from .mongo import get_mongo_client

class TotalSalesOverTime(APIView):
    def get(self, request, interval='daily'):
        db = get_mongo_client()
        response_data = {}
        # Fetch data from MongoDB
        orders = list(db.shopifyOrders.find({}, {'_id': 0, 'created_at': 1, 'total_price_set.shop_money.amount': 1}))

        # Convert to DataFrame
        df = pd.DataFrame(orders)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Flatten nested fields
        df['total_price'] = df['total_price_set'].apply(lambda x: float(x['shop_money']['amount']) if x else 0)

        # Define resampling rule based on the interval
        resample_rule = {
            'daily': 'D',
            'monthly': 'M',
            'quarterly': 'Q',
            'yearly': 'Y'
        }.get(interval, 'D')

        # Group and aggregate data
        sales_over_time = df.resample(resample_rule, on='created_at')['total_price'].sum().reset_index()

        # Prepare the response
        response_data['data'] = sales_over_time.to_dict(orient='records')
        return Response(response_data)
    

class SalesGrowthRateOverTime(APIView):
    def get(self, request, interval='monthly'):
        # Fetch data from MongoDB
        #import pdb;pdb.set_trace()
        db = get_mongo_client()
        response_data = {}
        # Fetch data from MongoDB
        orders = list(db.shopifyOrders.find({}, {'_id': 0, 'created_at': 1, 'total_price_set.shop_money.amount': 1}))

        # Convert to DataFrame
        df = pd.DataFrame(orders)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Flatten nested fields
        df['total_price'] = df['total_price_set'].apply(lambda x: float(x['shop_money']['amount']) if x else 0)

        # Define resampling rule based on the interval
        resample_rule = {
            'daily': 'D',
            'monthly': 'M',
            'quarterly': 'Q',
            'yearly': 'Y'
        }.get(interval, 'M')

        # Group and calculate total sales
        total_sales = df.resample(resample_rule, on='created_at')['total_price'].sum()

        # Calculate growth rate
        growth_rate = total_sales.pct_change().fillna(0).reset_index()
        growth_rate.rename(columns={'total_price': 'growth_rate'}, inplace=True)

        # Prepare the response
        response_data['data'] = growth_rate.to_dict(orient='records')
        return Response(response_data)
    
class NewCustomersAddedOverTime(APIView):
    def get(self, request, interval='monthly'):
        db = get_mongo_client()
        response_data = {}
        # Fetch data from MongoDB
        customers = list(db.shopifyCustomers.find({}, {'_id': 0, 'created_at': 1}))

        # Convert to DataFrame
        df = pd.DataFrame(customers)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Define resampling rule based on the interval
        resample_rule = {
            'daily': 'D',
            'monthly': 'M',
            'quarterly': 'Q',
            'yearly': 'Y'
        }.get(interval, 'M')

        # Group and count new customers
        new_customers = df.resample(resample_rule, on='created_at').size().reset_index(name='new_customers')

        # Prepare the response
        response_data['data'] = new_customers.to_dict(orient='records')
        return Response(response_data)
    
class RepeatCustomersCount(APIView):
    def get(self, request, interval='monthly'):
        db = get_mongo_client()
        response_data = {}
        # Fetch data from MongoDB
        orders = list(db.shopifyOrders.find({}, {
            '_id': 0,
            'created_at': 1,
            'customer': 1
        }))

        # Convert to DataFrame
        df = pd.DataFrame(orders)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Extract customer ID from nested dictionary
        df['customer_id'] = df['customer'].apply(lambda x: x['id'] if isinstance(x, dict) and 'id' in x else None)

        # Drop rows where customer_id is missing
        df = df[df['customer_id'].notna()]

        # Count orders per customer
        repeat_customers = df.groupby('customer_id').size().reset_index(name='order_count')
        repeat_customers = repeat_customers[repeat_customers['order_count'] > 1]

        # Merge repeat customers with original orders
        df = df.merge(repeat_customers[['customer_id']], on='customer_id', how='inner')

        # Define resampling rule based on the interval
        resample_rule = {
            'daily': 'D',
            'monthly': 'M',
            'quarterly': 'Q',
            'yearly': 'Y'
        }.get(interval, 'M')

        # Group by resampling period and count repeat customers
        repeat_customers_resampled = df.resample(resample_rule, on='created_at').size().reset_index(name='repeat_customers')

        # Prepare the response
        response_data['data'] = repeat_customers_resampled.to_dict(orient='records')
        return Response(response_data)
    
class GeographicalDistribution(APIView):
    def get(self, request):
        db = get_mongo_client()
        response_data = {}
        customers = list(db.shopifyCustomers.find({}, {
            '_id': 0,
            'default_address.city': 1
        }))

        # Convert to DataFrame
        df = pd.DataFrame(customers)

        # Extract city information
        df['city'] = df['default_address'].apply(lambda x: x['city'] if isinstance(x, dict) and 'city' in x else None)

        # Group by city and count customers
        geo_distribution = df.groupby('city').size().reset_index(name='customer_count')

        # Prepare the response
        response_data['data'] = geo_distribution.to_dict(orient='records')
        return Response(response_data)
    
class CustomerLifetimeValueByCohorts(APIView):
    def get(self, request):
        db = get_mongo_client()
        response_data = {}
        orders = list(db.shopifyOrders.find({}, {
            '_id': 0,
            'created_at': 1,
            'total_price_set.shop_money.amount': 1,
            'customer': 1
        }))

        # Convert to DataFrame
        df = pd.DataFrame(orders)
        df['created_at'] = pd.to_datetime(df['created_at'])

        # Extract total_price and customer_id
        df['total_price'] = df['total_price_set'].apply(lambda x: float(x['shop_money']['amount']) if isinstance(x, dict) and 'shop_money' in x else 0)
        df['customer_id'] = df['customer'].apply(lambda x: x['id'] if isinstance(x, dict) and 'id' in x else None)

        # Determine cohort month and convert to string
        df['cohort_month'] = df['created_at'].dt.to_period('M').astype(str)

        # Group by cohort month and calculate total sales
        cohort_value = df.groupby('cohort_month')['total_price'].sum().reset_index()

        # Prepare the response
        response_data['data'] = cohort_value.to_dict(orient='records')
        return Response(response_data)
#http://127.0.0.1:8000/analytics/sales_growth_rate_over_time/daily/