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
    with open('data/topology.yaml', 'r') as file:
        topology = yaml.safe_load(file)
    # Получаем старую топологию
    with open('data/topology_old.yaml', 'r') as file:
        topology_old = yaml.safe_load(file)
    # извлекаем все линки
    all_links = get_all_links(topology)
    # извлекаем все линки старой топологии
    all_links_old = get_all_links(topology_old)
    # удаляем избыточные линки
    unique_links = del_excess_link(all_links)
    # удаляем избыточные линки из старой топологии
    unique_links_old = del_excess_link(all_links_old)
    # рисуем граф
    draw_graph(topology, unique_links, unique_links_old)
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


def draw_graph(full_topology, uniq_links, unique_links_old, out_filename='img/draw_topology'):
    nodes = set(node for link in uniq_links.items() for node, intf in link)
    nodes_old = set(node for link in unique_links_old.items() for node, intf in link)
    new_nodes = nodes - nodes_old
    del_nodes = nodes_old - nodes

    draw = Graph('Network Topology', format='svg')

    draw.attr(rankdir='BT', splines='line')

    for node in nodes:
        if node in new_nodes:
            draw.node(node, shape='box', margin='0.3', color='green')
        elif node in del_nodes:
            draw.node(node, shape='box', margin='0.3', color='red')
        else:
            draw.node(node, shape='box', margin='0.3')

    links_new = set(uniq_links.items()) - set(unique_links_old.items())
    links_old = set(unique_links_old.items()) - set(uniq_links.items())

    for link1, link2 in uniq_links.items():
        head, taillabel = link1
        tail, headlabel = link2
        if (link1, link2) in links_new:
            if full_topology[head]['role'] == full_topology[tail]['role']:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          constraint='false', minlen='10', fontsize='10', color='green')
            else:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          fontsize='10', minlen='4', color='green')
        elif (link1, link2) in links_old:
            if full_topology[head]['role'] == full_topology[tail]['role']:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          constraint='false', minlen='10', fontsize='10', color='red')
            else:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          fontsize='10', minlen='4', color='red')
        else:
            if full_topology[head]['role'] == full_topology[tail]['role']:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          constraint='false', minlen='10', fontsize='10')
            else:
                draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                          fontsize='10', minlen='4')

    draw.render(out_filename)


if __name__ == '__main__':
    draw_topology()
