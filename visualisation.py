from networkx import Graph
import yaml


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


def draw_topology(full_topology, uniq_links, out_filename='img/draw_topology'):
    nodes = set(node for link in uniq_links.items() for node, intf in link)

    draw = Graph('Network Topology', format='svg')

    draw.attr(rankdir='BT', splines='line')

    for node in nodes:
        draw.node(node, shape='box')

    for link1, link2 in uniq_links.items():
        head, headlabel = link1
        tail, taillabel = link2
        if topology[head]['role'] == topology[tail]['role']:
            draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel,
                      constraint='false', label=" " * 30)
        else:
            draw.edge(head, tail, headlabel=headlabel, taillabel=taillabel, minlen='3')

    draw.render(out_filename)
    # print(draw.pipe().decode())


if __name__ == '__main__':
    # Получаем полную топологию
    with open('topology.yaml', 'r') as file:
        topology = yaml.safe_load(file)
    # извлекаем все линки
    all_links = get_all_links(topology)
    # удаляем избыточные линки
    unique_links = del_excess_link(all_links)
    # рисуем граф
    draw_topology(topology, unique_links)

    print(len(unique_links))
