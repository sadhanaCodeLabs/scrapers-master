import requests
from bs4 import BeautifulSoup
import csv

url = "https://forecast.weather.gov/MapClick.php?lon=-74.01214599609375&lat=40.71655807771725#.YKMtFC1h1bU"
response = requests.get(url)
print("Response - {}".format(response))
soup = BeautifulSoup(response.content, 'html.parser')
week_forecast = soup.find('ul', attrs={'id': 'seven-day-forecast-list'})
results = []
print("week_forecast - {}".format(week_forecast.contents))
for forecast in week_forecast.contents:
    results.append({
        'period_name': forecast.find('p', attrs={'class': 'period-name'}).get_text(),
        'short_desc': forecast.find('p', attrs={'class': 'short-desc'}).get_text(),
        'temp': forecast.find('p', attrs={'class': 'temp'}).get_text()
    })
with open('weather.csv', 'w') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=results[0].keys())
    writer.writeheader()
    for row in results:
        writer.writerow(row)
