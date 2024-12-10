import scrapy
from scrapy import FormRequest
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from ..items import ShootingPlace
import os

script_directory = os.path.dirname(os.path.abspath(__file__))

zip_path = 'zip_code.csv'
zip_zip = []
with open(zip_path, newline='') as csvfile:
    zipcodes_reader = csv.reader(csvfile)
    for row in zipcodes_reader:
        zip_zip.append(row[0]) 



class SpidySpider(scrapy.Spider):
    name = 'spidy'
    start_urls = ['https://www.wheretoshoot.org/']
    zip_codes = zip_zip

    def __init__(self):
        self.driver = webdriver.Chrome()

    def start_requests(self):
        for zip_code in self.zip_codes:
            yield FormRequest(
                url=self.start_urls[0],
                formdata={'search': zip_code},
                callback=self.parse,
                meta={'zip_code': zip_code},
            )
    def parse(self, response):
        item = ShootingPlace()
        locations = response.css('#mCSB_1_container .location-item')
        debug_zip = response.meta.get('zip_code')
        print("Current zip code:", debug_zip)
        for loc in locations:
            try:
                id = loc.xpath('.//span[@class="id"]/text()').get()
                name = loc.css(".name::text").get()
                street_address = loc.css('.address::text').get()
                big_address = loc.css('.address1::text').get()
                tem_address_list = big_address.split(",")
                city = tem_address_list[0]
                state = tem_address_list[1]
                zipcode = tem_address_list[2]

                phone_number = loc.css('.phone::text').get()
                nssf_member = loc.css('.is-member::attr(style)').get()
                
                facility_detail = loc.css('.facility-details-list li:not([class="hidden"])::text').extract()
                facility_detail = ', '.join(facility_detail).strip()
                
                service = loc.css('.services-list li:not([class="hidden"])::text').extract()
                service = ', '.join(service).strip()
                
                shooting_avaliable = loc.css('.shooting-av-list li:not([class="hidden"])::text').extract()
                shooting_avaliable = ', '.join(shooting_avaliable).strip()
                
                distance = loc.css('.distance-list li:not([class="hidden"])::text').extract()
                distance = ', '.join(distance).strip()
                
                competition = loc.css('.competitions-available-list li:not([class="hidden"])::text').extract()
                competition = ', '.join(competition).strip()

                website = loc.css('.btn-website::attr(href)').get()

                if not nssf_member:
                    nssf_member = "Yes"
                else:
                    nssf_member = "No"
                item["debug_zip"] = debug_zip
                item["id"] = id
                item["name"] = name
                item["street_address"] = street_address
                item["city"] = city
                item["state"] = state
                item["zipcode"] = zipcode
                item["phone_number"] = phone_number
                item["nssf_member"] = nssf_member
                item["facility_detail"] = facility_detail
                item["service"] = service
                item["shooting_avaliable"] = shooting_avaliable
                item["distance"] = distance
                item["competition"] = competition
                item["website"] = website
                
            except Exception as e:
                self.logger.error(f"Error occurred for debug_zip {debug_zip}: {e}")
                continue  # Add this line to continue with the next iteration in the loop
            yield item
        
        
    def closed(self, reason):
        self.driver.quit()