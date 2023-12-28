import json

def calc_index():

    f = 'merged/sorted.csv'
    data_list = dict()
    key = ''

    with open(f, 'r', newline='', encoding='utf-8') as file:
        byte_position = 0
        start_byte_position = 0
        header = file.readline().strip()
        byte_position += len(header.encode('utf-8')) + len(file.newlines[-1].encode('utf-8')) if file.newlines else len(header.encode('utf-8'))

        while True:

            line = file.readline()
            if not line:
                break

            values = line.strip().split(',')
            row_dict = dict(zip(header.split(','), values))

            if key == '':
                key = row_dict['Name']
                start_byte_position = byte_position

            elif row_dict['Name'] != key:
                data_list[key] = {'start_byte_position': start_byte_position, 'end_byte_position': byte_position}

                key = row_dict['Name']
                start_byte_position = byte_position

            byte_position += len(line.encode('utf-8'))


    with open('indexPos/index_positions.json', 'a') as f:
        json.dump(data_list, f, indent=4)

    return