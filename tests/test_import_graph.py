from tools.build_import_graph import build_graph, find_cycles


def test_import_graph_has_no_cycles():
    cycles = find_cycles(build_graph())
    assert cycles == [], "Genesis local import graph contains cycles"


def test_import_graph_is_nonempty():
    graph = build_graph()
    assert graph
