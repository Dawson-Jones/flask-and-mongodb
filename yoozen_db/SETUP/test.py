import csv

with open('url.csv', 'r', newline='') as f:
    reader = csv.DictReader(f)
    num = 0
    i = dict()
    for csv_url in reader:
        print(csv_url)
        '''
        {
            '192.168.2.25:3000': '192.168.3.131:3000', 
            '192.168.2.26:3000': '192.168.3.131:3001'
        }
        '''
        i = csv_url

    print(type(i))
    print(i.get('192.168.2.25:3000'))
