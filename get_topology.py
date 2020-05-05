from nornir import InitNornir
from nornir.plugins.tasks.networking import (netmiko_send_command,
                                             netmiko_save_config,
                                             netmiko_send_config)
import os
import yaml

os.environ['NET_TEXTFSM'] = './ntc-templates/templates'


def get_topology(filename='topology.yaml'):
    '''
    Парсит вывод команды sh lldp neighbors.
    Предварительно проверяет включен ли lldp на устройствах
    и если нет то включает.

    На входе ждет названия yaml файла для записи топологии.

    Записывает топологию в yaml файл:
    {'role': host1: [рапарсенный вывод команды sh lldp neighbors],
             host2: [рапарсенный вывод команды sh lldp neighbors],
     ...}

    '''
    with InitNornir(config_file='config.yaml') as nr:
        # проверяем включен ли lldp и если нет то включаем
        nr.run(check_and_conf_lldp, command='lldp run')
        # парсим вывод sh lldp neig
        output = nr.run(netmiko_send_command, command_string='show lldp neighbors', enable=True, use_textfsm=True)
    # превращаем обьекты норнира в удобноваримый словарь
    topology = normilize_data(output, nr.inventory.hosts)
    with open(filename, 'w') as file:
        yaml.dump(topology, file)


def check_and_conf_lldp(task, command):
    '''
    Проверяет есть ли команда lldp run в
    running config. Если нет то применяет ее
    на хочту.
    '''
    run_config = task.run(netmiko_send_command,
                          command_string='sh run',
                          enable=True)

    if command not in run_config.result:
        task.run(netmiko_send_config, config_commands=[command])
        task.run(netmiko_save_config)


def normilize_data(nornir_output, hosts_inventory):
    '''
    Преобразует информацию из nornir обьектов в словарь:
    {'role': host1: [рапарсенный вывод команды sh lldp neighbors],
             host2: [рапарсенный вывод команды sh lldp neighbors],
     ...}
    '''
    result = {}

    for host, pars in nornir_output.items():
        host = hosts_inventory[host]
        hostname = f'{host.name}.{host["domain"]}'
        role = host['role']
        result.update({hostname: {}})
        result[hostname].update({'neighbors': pars.result, 'role': role})

    return result


if __name__ == '__main__':
    get_topology()
