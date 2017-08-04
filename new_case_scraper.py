import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from accountability_console.models import *


# This function takes two arguments: 
# 1. iam_name is a string of the name of the IAM, i.e. 'Inspection Panel'
# 2. scraping_function is a function that returns a list of tuples
# To use this scraper for any IAM, create a scraping_function that grabs the elements, ids, and countries from the IAM's Complaints Registry website,
# and returns them as a list of tuples formated as (element, id, country), where element is the case's name.

def scraper(iam_name, scraping_function):
	pair_list = scraping_function()

	iam = IAM.objects.get(name=iam_name)
	case_ids = Case.objects.filter(iam=iam).values_list('external_id', flat=True)

	new_cases = []
	new_countries = []
	for pair in pair_list:
		if pair[1] not in case_ids:
			country, created = Country.objects.get_or_create(name=pair[2])
			if created:
				new_countries.append(country)
				print 'NEW COUNTRY CREATED: %s' % country
			case_name = 'NEW: %s' % pair[0]
			new_case, created = Case.objects.get_or_create(
				name=case_name, 
				external_id=pair[1], 
				iam=iam, 
				added_by=UserProfile.objects.first()
				)
			if created:
				new_cases.append(new_case)
				new_case.country.add(country)
				new_case.save()
				print 'NEW CASE CREATED: %s' % case_name
		else:
			break

def WBPanel():
	driver = webdriver.Firefox()
	driver.get("http://ewebapps.worldbank.org/apps/ip/Pages/AllPanelCases.aspx")
	time.sleep(3)

	i = 1
	pair_list = []

	elements = driver.find_elements_by_class_name("lasttd")
	ids = driver.find_elements_by_class_name("IPPanelCasestd")
	countries = []
	for n in range(1, len(elements)+1):
		xpath = '//*[@id="tblnewAdd"]/tbody/tr[%s]/td[2]' % n
		country = driver.find_element_by_xpath(xpath)
		countries.append(country)


	for element in elements[1:]:
		pair = (element.text, ids[i].text, countries[i].text)
		pair_list.append(pair)
		i += 1

	return pair_list

def IDBMICI():
	driver = webdriver.Firefox()
	driver.get('http://www.iadb.org/en/mici/mici-idb-chronological-public-registry,1805.html?status=&page=1')
	time.sleep(3)

	elements = []
	ids = []
	countries = []

	print 'ON FIRST PAGE.'
	get_page_info(driver, elements, ids, countries)
	print 'GOT INFO FROM FIRST PAGE.'
	next_button = True
	while next_button == True:
		try:
			driver.find_element_by_class_name('next').click()
			time.sleep(3)
			print 'MOVED TO NEXT PAGE.'
			get_page_info(driver, elements, ids, countries)
			print 'GOT INFO FROM NEXT PAGE.'
		except:
			next_button = False
			print 'ON LAST PAGE - NO MORE INFO TO GATHER.'


	i = 0
	pair_list = []
	for element in elements:
		pair = (element, ids[i], countries[i])
		pair_list.append(pair)
		i += 1

	return pair_list


def get_page_info(driver, elements, ids, countries):
	for n in range(2, 17):
		try:
			xpath = '//*[@id="container_2"]/div[2]/div/div/table/tbody/tr[%s]/td[3]' % n
			element = driver.find_element_by_xpath(xpath)
			elements.append(element.text)
		except:
			break
	print 'Elements gathered.'

	for n in range(2, 17):
		try:
			xpath = '//*[@id="container_2"]/div[2]/div/div/table/tbody/tr[%s]/td[1]' % n
			case_id = driver.find_element_by_xpath(xpath)
			ids.append(case_id.text)
		except:
			break
	print 'IDs gathered.'

	for n in range(2, 17):
		try:
			xpath = '//*[@id="container_2"]/div[2]/div/div/table/tbody/tr[%s]/td[4]' % n
			country = driver.find_element_by_xpath(xpath)
			countries.append(country.text)
		except:
			break
	print 'Countries gathered.'
