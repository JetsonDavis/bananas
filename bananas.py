# Bananas - Jeff Davidson 310-395-9300 jeff@very-advanced.com
# Coding challenge 4/8/2019

from flask import Flask, g
from flask_restful import Resource, Api, reqparse
from datetime import datetime
from datetime import timedelta
import markdown, os, shelve, re

print('Entering prog')

SELL = 0.35
BUY = 0.20
DAYS = 10

app = Flask(__name__)
api = Api(app)

def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = shelve.open("bananas.db")
	return db

def validate_transaction_entry(args):
	#if not re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', args['date']):
		#return ["Illegal date format - must be YYYY-MM-DD"]

	try:
		date = datetime.strptime(args['date'], '%Y-%m-%d')
	except:
		return "Invalid date"

	try:
		total = int(args['total'])
	except:
		return "Invalid quantity"

	return 

def add_transaction(date, total):
	shelf = get_db()
	if 'data' not in shelf:
		shelf['data'] = []
	data = shelf['data']

	shelf['data'] = shelf['data'] + [[int(date.replace('-','')), total]]

	return shelf['data']

def search(data, date):
	# Binary search to find date in data.  
	# Returns the index of the first un-needed date

	a, b = 0, len(data)

	while a != b:
		mid = int((b - a) / 2) + a
		if data[mid][0] == date:
			# inch fwd to cover all transactions this day
			while mid < len(data) and data[mid][0] == date:
				mid += 1
			break
		elif data[mid][0] < date:
			a = mid + 1
		else:
			b = mid - 1

	if mid != date:
		return -1
	return mid

def shift_inv(b, shift_val, waste_days):

	waste_total = sum(b[0:waste_days])

	b = b[shift_val:] + [0 for i in range(shift_val)]
	return b, waste_total

def take_from_inv(buffr, index, total):
	taken_from_inv = 0 
	while total < 0 and index >= 0:
		if buffr[index] < -total:
			total += buffr[index]
			buffr[index] = 0
			index -= 1
		else:
			buffr[index] += total
			total = 0

	return buffr, total

@app.teardown_appcontext
def teardown_db(exception):
	db = getattr(g, '_database', None)
	if db is not None:
		db.close()

@app.route("/")
def index():
    # Open the readme.md file
    with open (os.path.dirname(os.path.abspath(__file__)) + '/readme.md', 'r') as markdown_file:

        # Read file contents
        content = markdown_file.read()

        # Return HTML
        return markdown.markdown(content)

@app.route("/print_shelf")
def print_shelf():
	shelf = get_db()
	print("Shelf contents:")
	pr = ''
	for s in shelf:
		print (s, shelf[s])
		pr += '<span>' + s + ": " + str(shelf[s]) + "<br/></span>"

	return pr

@app.route("/clear_data")
# Clears out the data value from the shelf
def clear_data():
	shelf = get_db()
	shelf['data'] = []
	return "Data cleared."

@app.route("/clear_shelf")
# Clears all data from the shelf
def clear_shelf():
	shelf = get_db()
	shelf.clear()
	return "Shelf emptied."

class UpdateValues(Resource):
	def post(self):
		changes = {}
		parser = reqparse.RequestParser()
		parser.add_argument('sell_price', required = False)
		parser.add_argument('buy_price', required = False)
		parser.add_argument('days_fresh', required = False)

		args = parser.parse_args()
		shelf = get_db()
		if args['sell_price'] is not None:
			shelf['sell_price'] = args['sell_price']
			changes['sell_price'] = args['sell_price']
		if args['buy_price'] is not None:
			shelf['buy_price'] = args['buy_price']
			changes['buy_price'] = args['buy_price']
		if args['days_fresh'] is not None:
			shelf['days_fresh'] = args['days_fresh']
			changes['days_fresh'] = args['days_fresh']

		return {'message': 'Changes made' if changes else 'No changes', 'data': changes}, 201

class Purchase(Resource):
	def post(self):
		# get arguments
		parser = reqparse.RequestParser()
		parser.add_argument('total', required = True)
		parser.add_argument('date', required = True)
		args = parser.parse_args()

		# Validate 
		args_error = validate_transaction_entry(args)
		
		if args_error:
			return {'message': args_error, 'data': ''}, 404

		shelf = add_transaction(args['date'], int(args['total']))
		
		return {'message': 'data validated ', 'data': shelf}, 201

class Sell(Resource):
	def post(self):
		# get arguments
		parser = reqparse.RequestParser()
		parser.add_argument('total', required = True)
		parser.add_argument('date', required = True)
		args = parser.parse_args()

		# Validate 
		args_error = validate_transaction_entry(args)
		
		if args_error:
			return {'message': args_error, 'data': ''}, 404

		shelf = add_transaction(args['date'], -1*int(args['total']))

		return {'message': 'data validated ', 'data': shelf}, 201

class Metrics(Resource):
	def get(self):
		# get arguments
		parser = reqparse.RequestParser()
		parser.add_argument('start_date', required = True)
		parser.add_argument('end_date', required = True)
		args = parser.parse_args()

		start_date = datetime.strptime(args['start_date'], '%Y-%m-%d')
		end_date = datetime.strptime(args['end_date'], '%Y-%m-%d')

		shelf = get_db()

		# Make sure data has been loaded
		if 'data' not in shelf or shelf['data'] == []:
			return {'message': 'No data loaded', 'data': ''}, 401

		# Load cost and waste parameters
		sell_price = float(shelf['sell_price']) if 'sell_price' in shelf else SELL
		buy_price = float(shelf['buy_price']) if 'buy_price' in shelf else BUY	
		days_fresh = int(shelf['days_fresh']) if 'days_fresh' in shelf else DAYS

		# sort data by date
		data = shelf['data']
		data.sort(key=lambda x: x[0])

		# Create inventory age matrix - this is used to keep track of each traunche of fruit
		inventory_age = [0 for i in range(0, days_fresh)]

		# Remove any dates past the end date
		end = int(args['end_date'].replace('-',''))
		if end_date < datetime.strptime(str(data[len(data)-1][0]), '%Y%m%d'):
			# Find index of first un-needed date (uses binary search in case data list is large)
			unneeded_index = search(data, end)
			data = data[0:unneeded_index]

		current_date = datetime.strptime(str(data[0][0]), '%Y%m%d')
		daily_total, inventory_index, total_purchased, total_sold, total_waste= 0,0,0,0,0

		# Add dummy date to make sure last day of transaction data is flushed
		dummy = end_date + timedelta(days=1)
		dummy_date = int(str(dummy.year) + str('%02d' % dummy.month) + str('%02d' % dummy.day))
		data = data + [[dummy_date,0]]

		# Loop through dates - earliest -> end date	- and compute profit and waste
		for d in data:
			# if date is in the range in question, add to totals
			if current_date >= start_date and current_date <= end_date:
				if d[1] < 0:
					total_sold += d[1]
				else:
					total_purchased += d[1]

			# If date has changed, complete transaction for prior day, otherwise, aggregate day
			d0_date = datetime.strptime(str(d[0]), '%Y%m%d')
			if d0_date == current_date:
				daily_total += d[1]
			else:
				days_between_xaction = (d0_date - current_date).days
				current_date = d0_date
				
				# If day is net positive (bought more than sold), add to inventory
				if daily_total >= 0:
					inventory_age[inventory_index] = daily_total
				# Day is net negative, so take product from inventory
				else:
					inventory_age, daily_total = take_from_inv(inventory_age, inventory_index - 1, daily_total)

					# We sold more than we had => error in the dataset
					if daily_total < 0:
						return {'message': 'Error in transaction data', 'data': ''}, 401

				daily_total = d[1]

				# If inv buffer is not full, keep filling it
				if days_between_xaction + inventory_index < days_fresh:
					inventory_index += days_between_xaction
				# Otherwise, shift inv buffer
				else:
					shift_val = min(days_between_xaction + inventory_index - days_fresh + 1, days_fresh)
					# calc number of days expiring past start date, if any
					waste_days = max(0, min((d0_date - start_date).days - days_fresh, shift_val))

					inventory_age, waste_count = shift_inv(inventory_age, shift_val, waste_days)
					inventory_index = days_fresh - 1
					total_waste += waste_count

		profit = (-total_sold * sell_price) - (total_purchased * buy_price)

		inventory = sum(inventory_age)
		return {'message': 'Success', 'data': {"inventory": str(inventory),"expired": str(total_waste),"total_sold": str(-total_sold),"profit": str(profit)}}, 201

api.add_resource(UpdateValues, '/update_values')
api.add_resource(Purchase, '/purchase')
api.add_resource(Sell, '/sell')
api.add_resource(Metrics, '/metrics')

if __name__ == "__main__":
	print ("HOWDY Y'ALL " + str(DAYS))
	app.run("0.0.0.0", port=5000, debug=True)

