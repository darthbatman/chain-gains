from bs4 import BeautifulSoup


def get_data_file_name(eatery):
    eatery_data_file_names = {
        'Taco Bell': 'taco_bell.html',
        'Panda Express': 'panda_express.html',
        'Chick Fil A': 'chick_fil_a.html',
        'McDonald\'s': 'mcdonalds.txt'
    }
    return 'data/obtained/' + eatery_data_file_names[eatery]


def save_gains(eatery, item_ratios):
    item_ratios = {k: v for k, v in
                   sorted(item_ratios.items(),
                          key=lambda item: item[1],
                          reverse=True)}

    file_name = 'data/generated/' + '_'.join(eatery.lower().split()) + \
        '_gains.csv'

    with open(file_name, 'w') as f:
        f.write('item,p/c ratio\n')
        for item in item_ratios.keys():
            f.write(item + ',' + str(item_ratios[item]) + '\n')
        f.close()


def get_taco_bell_gains(soup):
    odd = soup.findAll('tr', {'class': 'odd'})
    even = soup.findAll('tr', {'class': 'even'})

    items = odd
    items.extend(even)

    item_ratios = {}

    for item in items:
        name = item.findAll('td')[0].text.replace('[more info]', '').strip() \
            .lower()
        calories = int(item.findAll('td')[1].text.replace(',', ''))
        protein = int(item.findAll('td')[11].text.replace('<', ''))

        ratio = 0
        if calories > 0 and protein > 0:
            ratio = protein / calories
        item_ratios[name] = ratio

    save_gains('Taco Bell', item_ratios)


def get_panda_express_gains(soup):
    items = soup.findAll('tr')

    item_ratios = {}

    for item in items:
        entries = item.findAll('td')
        if len(entries) > 3:
            name = entries[0].text.strip().split('\n')[0].split(' - ')[0] \
                .split('(')[0].lower()
            calories = int(entries[2].text.split('\n')[2]) \
                if entries[2].text.split('\n')[2] else 0
            protein = int(entries[-1].text.split('\n')[2]) \
                if entries[2].text.split('\n')[2] else 0

            ratio = 0
            if calories > 0 and protein > 0:
                ratio = protein / calories
            item_ratios[name] = ratio

    save_gains('Panda Express', item_ratios)


def get_chick_fil_a_gains(soup):
    items = soup.findAll('tr')

    item_ratios = {}

    for item in items:
        entries = item.findAll('td')
        if len(entries) > 11:
            name = entries[0].text.strip().split('\n')[0].lower()
            calories_str = entries[2].text.strip() \
                if 'g' not in entries[2].text.strip() \
                else entries[3].text.strip()
            protein_str = entries[-1].text.strip()

            calories = int(calories_str) if calories_str else 0
            protein = int(protein_str) if calories_str else 0

            ratio = 0
            if calories > 0 and protein > 0:
                ratio = protein / calories
            item_ratios[name] = ratio

    save_gains('Chick Fil A', item_ratios)


def get_mcdonalds_gains(data):
    item_ratios = {}

    last_name = None
    name = None
    numbers = None

    data = data.replace('1\ncookie', '')
    for line in data.split('\n')[8:]:
        if line[:4] == 'cup ':
            line = line[4:]
        if not line:
            continue
        if 'serving size' in line.lower() or \
           'nutrition facts' in line.lower() or \
           'daily value' in line.lower() or \
           'calcium' in line.lower() or \
           '/' in line.lower() or \
           'beverages' in line.lower():
            continue
        if line[0] == '(' and line[1].isdigit() or \
           line[0].isdigit() and line[-1].isdigit():
            if name:
                last_name = name
                name = None
            if numbers:
                numbers += ' ' + line.lower()
            else:
                numbers = line.lower()
        elif not name:
            if numbers and len(numbers.split()) > 5:
                if float(numbers.split()[2]) == 0:
                    item_ratios[last_name] = 0
                else:
                    item_ratios[last_name] = float(numbers.split()[-5]) / \
                        float(numbers.split()[2])
            numbers = None
            name = line.lower()
        elif name:
            name += ' ' + line.lower()
        if ') ' in line and line.split(') ')[1] and not \
           (line[0] == '(' and line[1].isdigit()):
            line = line.split(') ')[1]
            if line[0] == '(' and line[1].isdigit() or \
               line[0].isdigit() and line[-1].isdigit():
                if name:
                    last_name = name
                    name = None
                if numbers:
                    numbers += ' ' + line.lower()
                else:
                    numbers = line.lower()
            elif not name:
                if numbers and len(numbers.split()) > 5:
                    if float(numbers.split()[2]) == 0:
                        item_ratios[last_name] = 0
                    else:
                        item_ratios[last_name] = float(numbers.split()[-5]) / \
                            float(numbers.split()[2])
                numbers = None
                name = line.lower()
            elif name:
                name += ' ' + line.lower()

    save_gains('McDonald\'s', item_ratios)


def get_gains(eatery):
    file_name = get_data_file_name(eatery)
    with open(file_name, 'r') as f:
        data = f.read()
        f.close()

    if eatery == 'Taco Bell':
        soup = BeautifulSoup(data, 'html.parser')
        get_taco_bell_gains(soup)
    elif eatery == 'Panda Express':
        soup = BeautifulSoup(data, 'html.parser')
        get_panda_express_gains(soup)
    elif eatery == 'Chick Fil A':
        soup = BeautifulSoup(data, 'html.parser')
        get_chick_fil_a_gains(soup)
    elif eatery == 'McDonald\'s':
        get_mcdonalds_gains(data)


if __name__ == '__main__':
    get_gains('Taco Bell')
    get_gains('Panda Express')
    get_gains('Chick Fil A')
    get_gains('McDonald\'s')
