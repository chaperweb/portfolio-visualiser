import gspread

from oauth2client.service_account import ServiceAccountCredentials


			
			
def load_data_from_url(SheetUrl):
	try:
		scope = ['https://spreadsheets.google.com/feeds']
		credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
		gc = gspread.authorize(credentials)
		Sheet = gc.open_by_url(SheetUrl)
		worksheet = Sheet.get_worksheet(0)
		values_list = worksheet.get_all_values()
		return values_list
		
	except gspread.exceptions.SpreadsheetNotFound:
		# url is broken or service account doesnt have rights to access the sheet
		return [[]]
		


if __name__ == '__main__':
    load_data_from_url('https://docs.google.com/spreadsheets/d/1lNuG43KgUNDR48VxJUlNNW7fvvaQW7gRyv9Qrc7Ihy0/edit')

