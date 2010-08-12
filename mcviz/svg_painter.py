import re
from time import time
from sys import stderr

from svg import SVGDocument
from svg import Spline, SplineLine, Line
from svg import photon, gluon, boson, fermion, hadron, vertex

def paint_svg(plain, event, options):
    data = PlainOutput(plain)
    data.scale = 1
    doc = SVGDocument(data.width, data.height, data.scale)

    t0 = time()
    for no, spline in data.edge_lines.iteritems():
        particle = event.particles[no]
        gluon_args = {"stroke" : "green", "stroke-width" : 0.02, "scale": 0.4}
        photon_args = {"stroke" : "red", "stroke-width" : 0.1, "scale" : 0.2}
        fermi_args = {"fill" : "blue", "stroke":"blue", "stroke-width": 0.1, "scale" : 0.2}
        boson_args = {"stroke" : "blue", "stroke-width": 0.1, "scale" : 0.2}
        hadron_args = {"fill" : "red", "stroke":"red", "stroke-width": 0.1, "scale" : 0.2}
        if particle.gluon:
            doc.add_object(gluon(0.2, spline, **gluon_args))
        elif particle.photon:
            doc.add_object(photon(0.2, spline, **photon_args))
        elif particle.quark or particle.lepton:
            doc.add_object(fermion(0.5, spline, **fermi_args))
        elif particle.boson:
            doc.add_object(boson(0.5, spline, **boson_args))
        else:
            doc.add_object(hadron(0.5, spline, **hadron_args))

        if data.edge_label[no]:
            x, y = data.edge_label[no]
            doc.add_glyph(particle.pdgid, x, y, options.label_size)

    for vno, pt in data.nodes.iteritems():        
        vx = event.vertices[vno]
        if vx.is_final:
            continue
        vertex_args = {"stroke":"black", "fill":"none", "stroke-width" : "0.05"}
        if vx.hadronization or vx.is_initial:
            r = 0.5
        else:
            r = 0.1
        doc.add_object(vertex(pt, r, **vertex_args))

    t1 = time()
    print >> stderr, t1-t0
    return doc.toprettyxml()

class PlainOutput(object):
    def __init__(self, plain):

        self.scale = None
        self.width, self.height = None, None
        self.nodes = {}
        self.edge_lines = {}
        self.edge_label = {}

        for line in plain.split("\n"):
            tokens = line.strip().split()
            command = tokens[0]
            if command == "graph":
                self.handle_graph(tokens[1:])
            elif command == "node":
                self.handle_node(tokens[1:])
            elif command == "edge":
                self.handle_edge(tokens[1:])
            elif command == "stop":
                break

    def handle_graph(self, parameters):
        self.scale, self.width, self.height = map(float, parameters)

    def handle_node(self, parameters):
        no = int(parameters[0])
        x, y = float(parameters[1]), self.height - float(parameters[2])
        self.nodes[no] = (x,y)

    def handle_edge(self, parameters):
        no_in, no_out = int(parameters[0]), int(parameters[1])

        n_control_points = int(parameters[2])
        spline_parameters = parameters[3:(3 + 2 * n_control_points)]
        remaining = parameters[3 + 2 * n_control_points:]
        control_points = map(float, spline_parameters)
        # flip y coordinate
        for i in range(len(control_points)):
            if i % 2 == 1:
                control_points[i] = self.height - control_points[i]
        splines = self.get_splines(control_points)
        if len(splines) == 0:
            # TODO: Warn of degenerate particle
            return
        elif len(splines) == 1:
            splineline = splines[0]
        else:
            splineline = SplineLine(self.get_splines(control_points))

        if '"' in remaining[0]:
            left, label, right = " ".join(remaining).split('"', 2)
            remaining = right.strip().split()
            label_position = (float(remaining[0]), self.height - float(remaining[1]))
            remaining = remaining[2:]
        else:
            label_position = None

        no = int(remaining[0])

        self.edge_lines[no] = splineline
        self.edge_label[no] = label_position

    def get_splines(self, points):
        if len(points) == 2:
            return []
        pairs = (points[0:2], points[2:4], points[4:6], points[6:8])
        start, c1, c2, end = map(tuple, pairs)
        if start == c1 == c2 == end:
            return []
        return [Spline(start, c1, c2, end)] + self.get_splines(points[6:])
