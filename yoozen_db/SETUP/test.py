import csv

with open('url.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    num = 0
    for csv_url in reader:
        print(csv_url)
        '''
        {
            '192.168.2.25:3000': '192.168.3.131:3000', 
            '192.168.2.26:3000': '192.168.3.131:3001'
        }
        '''
        print(num)  # 0
        num += 1
