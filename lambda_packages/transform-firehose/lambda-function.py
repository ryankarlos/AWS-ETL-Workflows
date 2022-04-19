import base64

output = []


def lambda_handler(event, context):
    for record in event['records']:
        payload = base64.b64decode(record['data']).decode('utf-8')
        row_w_newline = payload + "\n"
        print(f"{record['data']} converted back to json str with added end line separator: {row_w_newline}")
        row_w_newline = base64.b64encode(row_w_newline.encode('utf-8'))

        output_record = {
            'recordId': record['recordId'],
            'result': 'Ok',
            'data': row_w_newline
        }
        print(f"output record dict with b64 encoded data value: {output_record}")
        output.append(output_record)

    print('Processed {} records.'.format(len(event['records'])))

    return {'records': output}