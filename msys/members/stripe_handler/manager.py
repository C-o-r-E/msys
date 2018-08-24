import stripe

class manager:
	def __init__(self):
		self.key = " "
		with open("./members/stripe_handler/KeyFile.key", "r") as f:
			self.key = f.readline()
		stripe.api_key = self.key
	
	def get_customer_object(self, cus_code):
		try:
			customer = stripe.Customer.retrieve("cus_D0nTkXIS0gUJ9Z")
			return customer
		except Exception as e:
			print(e)
		return 0
	
	

