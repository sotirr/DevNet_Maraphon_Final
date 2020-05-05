from graphviz import Graph
import yaml


def draw_topology(topology_filename='topology.yaml'):
    '''
    Отрисовывает топологию на основе полученой информации
    из yaml файла.

    На вход ждет название файла

    На выходе рисует граф в формате svg
    '''
    # Получаем полную топологию
    with open(topology_filename, 'r') as file:
        topology = yaml.safe_load(file)
    # извлекаем все линки
    all_links = get_all_links(topology)
    # удаляем избыточные линки
    unique_links = del_excess_link(all_links)
    # рисуем граф
    draw_graph(topology, unique_links)
    print('Топология нарисована')


def get_all_links(topology):
    result = {}
    for host, attr in topology.items():
        neighbors, role = attr.values()
        for neighbor in neighbors:
            local_link = (host, neighbor['local_interface'])
            rem_link = (neighbor['neighbor'], neighbor['neighbor_interface'])
            result.update({local_link: rem_link})
    return result


def del_excess_link(all_links):
    unique_links = all_links.copy()
    for link in all_links:
        if link in unique_links.values():
            del unique_links[link]
    return unique_links


def draw_graph(full_topology, uniq_links, out_filename='img/draw_topology'):
    nodes = set(node for link in uniq_links.items() for node, intf in link)

    draw = Graph('Network Topology', format='svg')

    draw.attr(rankdir='BT', splines='line')

    for node in nodes:
        draw.node(node, shape='box', margin='0.3')

    for link1, link2 in uniq_links.items():
        head, taillabel = link1
        tail, headlabel = link2
        if full_topology[head]['role'] == full_topology[tail]['role']:
            draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                      constraint='false', minlen='10', fontsize='10')
        else:
            draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                      fontsize='10', minlen='4')

    draw.render(out_filename)


if __name__ == '__main__':
    draw_topology()
