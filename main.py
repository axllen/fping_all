import re
import subprocess
import sys
from datetime import datetime
import json
import requests

from log_print import log_print

MAIN_PATH = sys.path[0]


def ping_hosts(hostfile: str) -> list:
    """
    使用 fping 批量测试设备丢包率和时延

    Args:
        hostfile: 一个包含主机 IP 的文本文档

    Returns:
        一个列表，里面的元素是字典，包括ping结果的ip、loss、avg
        如 [{'ip': '10.254.255.1', 'loss': '100', 'avg': '0.66'}]
    """

    result_list = []
    cmd = ['/usr/sbin/fping', '-q', '-c', '1', '-p', '100', '-f', hostfile]
    log_print('info', 'ping', '开始ping设备')
    output = subprocess.run(cmd, stderr=subprocess.PIPE)
    log_print('info', 'ping', 'ping测完成')
    ip_pattern = r'\d+\.\d+\.\d+\.\d+'
    loss_pattern = r'xmt/rcv/%loss = \S+/\S+/(\S+)%'
    avg_pattern = r'min/avg/max = \S+/(\S+)/\S+'

    output_list = output.stderr.decode('utf-8').splitlines()
    output_list.pop(0)
    for line in output_list:
        result_dict = {}
        ip_list = re.findall(ip_pattern, line)
        if ip_list:
            result_dict['ip'] = ip_list[0]
        loss_list = re.findall(loss_pattern, line)
        if loss_list:
            result_dict['loss'] = loss_list[0]
        else:
            result_dict['loss'] = '100'
        avg_list = re.findall(avg_pattern, line)
        if avg_list:
            result_dict['avg'] = avg_list[0]
        else:
            result_dict['avg'] = '-1'

        result_list.append(result_dict)

    return result_list


def write_api(result: json):
    url = 'http://10.254.255.208:8081/ping_mcr'
    data = {
        "action": "write",
        "version": 2,
        "data": result
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, json=data)

    if response.json().get('success'):
        log_print('success', 'write_to_api', 'ping测数据写入成功')
        return True
    else:
        log_print('error', 'write_to_api', 'ping测数据写入失败')
        return False


if __name__ == '__main__':
    now = datetime.now().strftime('%Y-%m-%d-%H-%M')
    ping_result_file = f'{MAIN_PATH}/output/{now}.txt'
    ip_file = f'{MAIN_PATH}/ip.txt'
    ping_result_list = ping_hosts(ip_file)
    log_print('info', 'main', f'ping测的数据总数为{len(ping_result_list)}')
    json_str = json.dumps(ping_result_list)

    try:
        write_api(json_str)
        log_print('success', 'main', '结果已存入数据库')
    except Exception as e:
        print(e)
        log_print('error', 'main', '存入数据库失败')

    with open(ping_result_file, 'w') as f:
        f.write(json_str)
    log_print('success', 'main', '结果已写入文件')
