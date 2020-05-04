from nornir import InitNornir
from nornir.plugins.tasks.networking import (netmiko_send_command,
                                             netmiko_save_config,
                                             netmiko_send_config)
import os
import yaml

os.environ['NET_TEXTFSM'] = './ntc-templates/templates'


def get_topology():
    '''
    Парсит вывод команды sh lldp neighbors.
    Предварительно проверяет включен ли lldp на устройствах
    и если нет то включает.
    
    Возвращает словарь вида:
    {host1: [рапарсенный вывод команды sh lldp neighbors],
     host2: [рапарсенный вывод команды sh lldp neighbors],
     ...}
    '''
    with InitNornir(config_file='config.yaml') as nr:
        # проверяем включен ли lldp и если нет то включаем
        nr.run(check_and_conf_lldp, command='lldp run')
        output = nr.run(netmiko_send_command, command_string='show lldp neighbors', enable=True, use_textfsm=True)

    return {host: result.result for host, result in output.items()}


def check_and_conf_lldp(task, command):

    run_config = task.run(netmiko_send_command, command_string='sh run', enable=True)

    if command not in run_config.result:
        task.run(netmiko_send_config, config_commands=[command])
        task.run(netmiko_save_config)


def get_all_link(topology):
    result = {}
    for host, neighpors in topology.items():
        for entry in neighpors:
            result.update({(host, entry['local_interface']): (entry['neighbor'], entry['neighbor_interface'])})
    return result


def del_excess_link(all_links):
    unique_links = all_links.copy()
    for link in all_links:
        if link in unique_links.values():
            del unique_links[link]
    return unique_links


if __name__ == '__main__':
    # Получаем полную топологию
    topology = get_topology()
    # извлекаем все линки
    all_links = get_all_link(topology)
    # удаляем избыточные линки
    unique_links = del_excess_link(all_links)

    with open('topology.yaml', 'w') as file:
        yaml.dump(unique_links, file)
