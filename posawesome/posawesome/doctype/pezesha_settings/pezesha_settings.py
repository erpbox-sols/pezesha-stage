# Copyright (c) 2024, Youssef Restom and contributors
# For license information, please see license.txt

import frappe
import requests
import json
from frappe.model.document import Document
from frappe import _
from frappe.integrations.utils import (make_get_request, make_post_request, create_request_log)

class PezeshaSettings(Document):
	def validate(self):
		if self.enable:
			try:
				response = make_post_request(
					# url = 'https://gateway.pezesha.com',
					url="https://dev.api.pezesha.com/oauth/token",
					headers = {
						'pezesha-apikey': '9ea7l6xraTJjDAXU6KYogxcArmlDGE1u',
						'Accept-Encoding': 'gzip, deflate'
					},
					data={
						"grant_type": "client_credentials",
						"client_id": self.client_id,
						"client_secret": self.client_secret_id,
						"provider": "users"				
					},
					auth=(
						self.client_id,
						self.get_password(fieldname="client_secret_id", raise_exception=False),
						),
					)
				self.authorization = response['access_token']
			except Exception as e:
				frappe.throw(_("Seems API Key or API Secret is wrong !!!"))



@frappe.whitelist()
def pezesha_loan_offer(customer, pos_profile):
	pos = frappe.get_doc("POS Profile", pos_profile)
	pz_st = frappe.db.get_single_value('Pezesha Settings', 'authorization')
	url = 'https://dev.api.pezesha.com/mfi/v1/borrowers/options'
	headers = {
		'Authorization': f'Bearer {pz_st}',
		'pezesha-apikey': '9ea7l6xraTJjDAXU6KYogxcArmlDGE1u',
		'Accept-Encoding': 'gzip, deflate'
	}
	data = {
		'channel': pos.custom_pezesha_channel_id,
		'identifier': customer
	}
	response = requests.post(url, headers=headers, data=data)
	if response.status_code == 200:
		try:
			dt = response.json()
			ddt = dt['data']
			return dt
		except KeyError:
			frappe.msgprint("You already have a pending loan. Cannot apply for new loan until current one is cleared")
			return "You already have a pending loan. Cannot apply for new loan until current one is cleared"
	else:
		frappe.msgprint(f"Unable To Find Borrower <b>{customer}</b>")
		return response.status_code

@frappe.whitelist()
def pezesha_loan_application(data, pos_profile):
	res = json.loads(data)
	pos = frappe.get_doc("POS Profile", pos_profile)
	pz_st = frappe.db.get_single_value('Pezesha Settings', 'authorization')
	url = 'https://dev.api.pezesha.com/mfi/v1/borrowers/loans'
	headers = {
		'Authorization': f'Bearer {pz_st}',
		'pezesha-apikey': '9ea7l6xraTJjDAXU6KYogxcArmlDGE1u',
		'Accept-Encoding': 'gzip, deflate'
	}
	data = {
		'channel': pos.custom_pezesha_channel_id,
		'pezesha_id': res.get('pezesha_customer_id'),
		'amount': res.get('amount'),
		'duration': res.get('duration'),
		'interest': res.get('interest'),
		'rate': res.get('rate'),
		'fee': res.get('fee')
	}

	response = requests.post(url, headers=headers, data=data)
	return response.json()

@frappe.whitelist()
def pezesha_loan_status(customer, pos_profile):
	pos = frappe.get_doc("POS Profile", pos_profile)
	pz_st = frappe.db.get_single_value('Pezesha Settings', 'authorization')
	url = 'https://dev.api.pezesha.com/mfi/v1/borrowers/latest'
	headers = {
		'Authorization': f'Bearer {pz_st}',
		'pezesha-apikey': '9ea7l6xraTJjDAXU6KYogxcArmlDGE1u',
		'Accept-Encoding': 'gzip, deflate'
	}
	data = {
		'channel': pos.custom_pezesha_channel_id,
		'identifier': customer
	}
	response = requests.post(url, headers=headers, data=data)
	if response.status_code == 200:
		try:
			dt = response.json()
			ddt = dt['data']
			amt = ddt['loan_amount']
			return ddt
		except KeyError:
			frappe.msgprint("Please Apply Loan Application")
			return "Please Apply Loan Application"
	else:
		frappe.msgprint("Please Apply Loan Application")
		
def corn():
	doc = frappe.get_doc('Pezesha Settings')
	if doc.enable:
		try:
			response = make_post_request(
				url="https://dev.api.pezesha.com/oauth/token",
				headers = {
					'pezesha-apikey': '9ea7l6xraTJjDAXU6KYogxcArmlDGE1u',
					'Accept-Encoding': 'gzip, deflate'
				},
				data={
					"grant_type": "client_credentials",
					"client_id": doc.client_id,
					"client_secret": doc.client_secret_id,
					"provider": "users"				
				},
				auth=(
					doc.client_id,
					doc.get_password(fieldname="client_secret_id", raise_exception=False),
					),
				)
			doc.db_set('authorization', response['access_token'])
		except Exception as e:
			frappe.throw(_("Seems API Key or API Secret is wrong !!!"))
