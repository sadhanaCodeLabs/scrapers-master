import requests
from bs4 import BeautifulSoup
import json
import time
import csv
from json.decoder import JSONDecodeError


class ExcavatorsScraper():
    results = []
    header = True
    global writer
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'zguid=23|%24d14f0059-d03b-4422-9f57-5862fcd13490; _ga=GA1.2.1741285320.1590755697; zjs_user_id=null; zjs_anonymous_id=%22d14f0059-d03b-4422-9f57-5862fcd13490%22; __gads=ID=1050523ba93d593d:T=1590755700:S=ALNI_MZlJJ_xqSbd51oJisV_HY4g017Ehw; _gcl_au=1.1.2000298647.1590755705; KruxPixel=true; _fbp=fb.1.1590755705919.1815197270; _pxvid=d6c5ec75-a1a8-11ea-b8a9-0242ac120009; KruxAddition=true; JSESSIONID=3E7EBDB1F8931DF7D0DE9992546AE0B3; zgsession=1|200e23e0-9534-4d27-931f-caa3de6b483b; _gid=GA1.2.1328942480.1590858452; _gat=1; DoubleClickSession=true; GASession=true; _uetsid=fdde22d5-862a-8a7d-93e4-a16c574edf91; _pin_unauth=YzUyOGQ2OGMtMmQ3YS00NGZkLTg3MmEtOGJlODM1YWMwMTA1; _px3=026336d3721eec42bcdec3278ad2d3ac2014d5e65707b21624fb2e743d9a89be:mq3WRz2RNL5PBIvbYNHCxq5VfXHXy2YKC+8Lqn97pIw8MiKppH7Cx7AjKzbAFi1zcehKGY36aIgsnE9NiPKwlw==:1000:4U1o3ogIQ0KzfyMd2QYEFGDnD1augezy5bJlzEn9ZHE89B2uEIxDg8BmsGj8szPwyIz1Yv15S2V0TV5P+0jCFisfGk92XM4DM7K13GCtNr0HXhNGftVBFxVrCv8ApRphw/Qwj7AcagCh9i6FPiQGLFruxVASJXLsNpFeWimekVY=; AWSALB=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; AWSALBCORS=ZKAGBcH2BwM6D1bRKOPynbOqyclySGz5U/fZB+wO3MYQ91UR9A5rFVtFsmjOkrMASUJguhtsJRZDM7IlBiWVT/pGw2S0BjxgEZmpFPrBZEqU2lWTE2NMArtecZD2; search=6|1593450465587%7Crect%3D40.843698984643765%252C-73.50417109960938%252C40.567821651427245%252C-74.45174190039063%26rid%3D6181%26disp%3Dmap%26mdm%3Dauto%26p%3D2%26z%3D0%26lt%3Dfsbo%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%09%096181%09%09%09%09%09%09',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }

    def fetch(self, url, page):
        response = requests.get(url+ str(page), headers=self.headers)
        print("{} - {}".format(url+ str(page), response.status_code))
        return response

    def parse(self, response):
        soup = BeautifulSoup(response, 'html.parser')
        divs = soup.findAll(class_='result machine-listing trackImpression')

        for equipment in divs:
            url = self.get_url(equipment, 'machine-model')
            additional_details = requests.get(url, headers=self.headers)
            soup_inner = BeautifulSoup(additional_details.text, 'html.parser')
            script = soup_inner.find('script', {'type': 'application/ld+json'})
            if script:
                try:
                    script_json = json.loads(script.contents[0], strict=False)
                except JSONDecodeError as e:
                    script_json = ''
            machine_location = soup_inner.find("td", text="Machine Location:").find_next_sibling("td").text
            condition = 'Null'
            meta_divs = soup_inner.findAll(class_='meta-descriptions')
            for meta in meta_divs:
                rows = meta.find_all('tr', attrs={'class': 'values'})
                if rows:
                    cells = rows[0].find_all('td');
                    condition = cells[len(cells)-1].text

            specs = soup_inner.findAll('table', {'class': 'category-specs'})
            max_net_power = self.get_max_net_power(specs)
            max_gross_power = self.get_max_gross_power(specs)
            max_power = max(max_net_power, max_gross_power)
            power_hp = 'Null'
            if max_power>0:
                power_hp = str(max_power)+' hp'

            self.results.append({
                'Manufacturer': self.get_manufacturer(self.get_value(equipment, 'machine-model')) if script_json=='' or not script_json['manufacturer']else script_json['manufacturer'],
                'Model': self.get_model(self.get_value(equipment, 'machine-model')) if script_json=='' or not script_json['model'] else script_json['model'],
                'Year': self.get_year(self.get_value(equipment, 'machine-model')),
                'Type': 'Excavators' if script_json=='' else script_json['category'],
                'SubType': self.get_value(equipment, 'machine-type'),
                'Size_Class': power_hp,
                'Price': self.get_value(equipment, 'machine-price') if script_json=='' else script_json['offers']['price'],
                'Currency': 'USD' if script_json=='' else script_json['offers']['priceCurrency'],
                'Serial_Number': self.get_serial(self.get_value(equipment, 'machine-serial-stock'),':'),
                'Meter_Reads': self.get_hours(self.get_value(equipment, 'machine-hours'),':'),
                'Meter_Reads_UOM': self.get_uom(self.get_value(equipment, 'machine-hours'),':'),
                'URL': url if script_json=='' else script_json['url'],
                'Seller_City': self.get_city(machine_location),
                'Seller_State': self.get_state(machine_location),
                'Seller_Zip': self.get_zip(machine_location),
                'Seller_Country': 'US',
                'Seller_Name': self.get_value(equipment, 'machine-dealer'),
                'Condition': condition,
                'Machine_Location': self.get_location(self.get_value(equipment, 'machine-location'),':'),
            })

    def get_url(self, equipment, classname):
        baseurl = 'https://www.constructionequipmentguide.com'
        nodes = equipment.find_all('div', attrs={'class': classname})
        url = 'Null'
        if nodes:
            node = nodes[0]
            if node is not None:
                val = node.find('a')['href']

        if val is not None:
            url = baseurl+val

        return url

    def get_value(self, equipment, classname):
        nodes = equipment.find_all('div', attrs={'class': classname})
        val = 'Null'
        if nodes:
            node = nodes[0];
            if node is not None:
                val = node.get_text()
        return val

    def get_serial(self, value, delimiter):
        val = 'Null'
        if value is not None:
            vals = value.split(delimiter)
            if len(vals)>1:
                val = vals[1]
        return val

    def get_manufacturer(self, value):
        val = 'Null'
        if value is not None:
            vals = value.split(' ')
            if len(vals)>1:
                val = vals[1]
        return val

    def get_model(self, value):
        val = ''
        if value is not None:
            vals = value.split(' ')
            if len(vals)>1:
                i = 2
                while i < len(vals):
                    val += ' '+vals[i]
                    i += 1
        else:
            val = 'Null'
        return val

    def get_year(self, value):
        val = 'Null'
        if value is not None:
            vals = value.split(' ')
            if len(vals)>1:
                val = vals[0]
        return val

    def get_location(self, value, delimiter):
        val = 'Null'
        if value is not None:
            vals = value.split(delimiter)
            if len(vals)>1:
                val = vals[1]
        return val

    def get_city(self, value):
        val = ''
        if value is not None:
            vals = value.split(',')
            if len(vals) > 1:
                i = 0
                vals1 = vals[0].split(' ')
                if len(vals1) > 1:
                    while i < len(vals1)-1:
                        val += ' ' + vals1[i]
                        i += 1
        else:
            val = 'Null'
        return val

    def get_state(self, value):
        val = 'Null'
        if value is not None:
            vals = value.split(',')
            if len(vals) > 1:
                i = 0
                vals1 = vals[0].split(' ')
                if len(vals1) > 1:
                    val = vals1[len(vals1)-1]
        return val

    def get_zip(self, value):
        val = 'Null'
        if value is not None:
            vals = value.split(',')
            if len(vals) > 1:
                val = vals[len(vals)-1]
        return val

    def get_hours(self, value, delimiter):
        val = 'Null'
        if value is not None:
            vals = value.split(delimiter)
            if len(vals)>1:
                val = vals[1]
        return val

    def get_uom(self, value, delimiter):
        val = 'Null'
        if value is not None:
            vals = value.split(delimiter)
            if len(vals)>1:
                val = vals[0]
        return val

    def get_max_net_power(self, specs):
        power = 0
        for spec in specs:
            spec_rows = spec.find_all('tr', attrs={'class': 'values'})
            for spec_row in spec_rows:
                if (spec_row.text.find("Net Power") > -1):
                    spec_cells = spec_row.find_all('td')
                    net_power = spec_cells[len(spec_cells) - 1].text
                    if net_power:
                        net_power_vals = net_power.split(' ')
                        if len(net_power_vals) > 1:
                            net_power_int_value = "".join(net_power_vals[0].split(","))
                            new_power_int = int(net_power_int_value)
                            if power < new_power_int:
                                power = new_power_int
        return power

    def get_max_gross_power(self, specs):
        power = 0
        for spec in specs:
            spec_rows = spec.find_all('tr', attrs={'class': 'values'})
            for spec_row in spec_rows:
                if spec_row.text.find("Gross Power") > -1:
                    spec_cells = spec_row.find_all('td')
                    gross_power = spec_cells[len(spec_cells) - 1].text
                    if gross_power:
                        gross_power_vals = gross_power.split(' ')
                        if len(gross_power_vals) > 1:
                            gross_power_int_value = "".join(gross_power_vals[0].split(","))
                            gross_power_int = int(gross_power_int_value)
                            if power < gross_power_int:
                                power = gross_power_int
        return power

    def to_csv(self):
        if self.header:
            with open('excavators.csv', 'w') as csv_file:
                if self.header:
                    print('Adding header to csv')
                    self.writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
                    self.writer.writeheader()
                    self.header = False

                for row in self.results:
                    self.writer.writerow(row)
        else:
            print('Append csv with data')
            with open('excavators.csv', 'a') as csv_file:
                    self.writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())

                    for row in self.results:
                        self.writer.writerow(row)


    def run(self):
        url = 'https://www.constructionequipmentguide.com/used-excavators-for-sale/'
        batch_size = 50
        batch_list = []
        for page in range(0, 900):
            batch_list.append(page)
            res = self.fetch(url, page)
            self.parse(res.text)
            time.sleep(1)
            if len(batch_list)==batch_size:
                self.to_csv()
                self.results = []
                batch_list.clear()

        if batch_list:
            print('Writing remaining {} pages'.format(len(batch_list)))
            self.to_csv()


if __name__ == '__main__':
    scraper = ExcavatorsScraper()
    scraper.run()