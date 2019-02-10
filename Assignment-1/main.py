import math
from functools import cmp_to_key
from tabulate import tabulate

vertex_count = 0
hedge_count = 0
face_count = 0

class Vertex:
    """Vertex on a cartesian plance"""

    def __init__(self, dx, dy):
        self.x = dx
        self.y = dy
        self.hedge_list = []
        global vertex_count
        vertex_count += 1
        self._name = "V" + str(vertex_count)

    def __repr__(self):
        return self._name

    def sortincident(self):
        self.hedge_list.sort(key=cmp_to_key(hedge_sort), reverse=True)

class Hedge:
    """Class for a half edge"""

    def __init__(self, vertex1, vertex2):
        self.origin = vertex2
        self.twin = None
        self.face = None
        self.nextHedge = None
        self.angle = hangle(vertex2.x-vertex1.x, vertex2.y-vertex1.y)
        self.prevHedge = None
        self.length = math.sqrt((vertex2.x-vertex1.x)**2 + (vertex2.y-vertex1.y)**2)

        global hedge_count
        hedge_count += 1
        self._name = "E" + str(hedge_count)

    def __repr__(self):
        return self._name

class Face:
    """Class for a Face in a subdivision"""
    
    def __init__(self):
        self.incident_edge = None
        self.external = None

        global face_count
        face_count += 1
        self._name = "F" + str(face_count)

    def __repr__(self):
        return self._name

    def area(self):
        h = self.incident_edge
        face_area = 0
        
        while(not h.nextHedge is self.incident_edge):
            p1 = h.origin
            p2 = h.nextHedge.origin
            face_area += p1.x*p2.y - p2.x*p1.y
            h = h.nextHedge

        p1 = h.origin
        p2 = self.incident_edge.origin
        face_area = (face_area + p1.x*p2.y - p2.x*p1.y)/2
        return face_area

class DCEL:
    """Class for Doubly Connected Edge List"""
    
    def __init__(self, vertex_list=[], edge_list=[]):
        self.vl = vertex_list
        self.el = edge_list
        self.vertices = []
        self.hedges = []
        self.faces = []

    def build(self):
        for v in self.vl:
            self.vertices.append(Vertex(v[0], v[1]))

        for e in self.el:
            h1 = Hedge(self.vertices[e[0]], self.vertices[e[1]])
            h2 = Hedge(self.vertices[e[1]], self.vertices[e[0]])
            h1.twin = h2
            h2.twin = h1
            self.vertices[e[1]].hedge_list.append(h1)
            self.vertices[e[0]].hedge_list.append(h2)
            self.hedges.append(h2)
            self.hedges.append(h1)

        for v in self.vertices:
            v.sortincident()
            l = len(v.hedge_list)
            for i in range(l-1):
                v.hedge_list[i].nextHedge = v.hedge_list[i+1].twin
                v.hedge_list[i+1].prevHedge = v.hedge_list[i]
            v.hedge_list[l-1].nextHedge = v.hedge_list[0].twin
            v.hedge_list[0].prevHedge = v.hedge_list[l-1]

        provlist = self.hedges[:]
        nf = 0
        nh = len(self.hedges)

        while nh > 0:
            h = provlist.pop()
            nh -= 1
            # Check if face is already present
            if h.face == None:
                f = Face()
                nf += 1
                # Link the hedge to the new face
                f.incident_edge = h
                f.incident_edge.face = f

                # Traverse the boundary of the new face
                while (not h.nextHedge is f.incident_edge):
                    h = h.nextHedge
                    h.face = f

                self.faces.append(f)

        # And finally we have to determine the external face
        for f in self.faces:
            f.external = f.area() < 0

    def print_vertex_record(self):
        vertex_list = self.vertices[:]
        result = []

        for v in vertex_list:
            row = []
            row.append(v)
            row.append([v.x, v.y])
            row.append(v.hedge_list)
            result.append(row)

        print(tabulate(result, headers=["Vertex", "Coordinates", "IncidentEdge"]))

    def print_face_record(self):
        face_list = self.faces[:]
        result = []

        for f in face_list:
            row = []
            row.append(f)
            row.append(f.incident_edge)
            row.append(f.external)
            result.append(row)

        print(tabulate(result, headers=["Face", "IncidentEdge", "External"]))
        

    def print_hedge_list(self):
        hedge_list = self.hedges[:]
        # h = hedge_list.pop()
        # temp = h

        result = []

        for h in hedge_list:
            row = []
            row.append(h)
            row.append(h.origin)
            row.append(h.twin)
            row.append(h.face)
            row.append(h.nextHedge)
            row.append(h.prevHedge)
            result.append(row)

            h = h.nextHedge

        
        print(tabulate(result, headers=["Hedge", "Origin", "Twin", "Face", "Next", "Prev"],
                tablefmt="fancy_grid"))


def hedge_sort(h1, h2):
    """Sorts two half edges counterclockwise"""

    if h1.angle < h2.angle:
        return -1
    elif h1.angle > h2.angle:
        return 1
    else:
        return 0

def hangle(dx,dy):
    """Determines the angle with respect to the x axis of a segment
    of coordinates dx and dy
    """
    l = math.sqrt(dx*dx + dy*dy)
    if dy > 0:
        return math.acos(dx/l)
    else:
        return 2*math.pi - math.acos(dx/l)

def input_graph():
    vertex_num = int(input("Number of vertices: "))

    vertex_list = []
    edge_list = []

    for i in range(vertex_num):
        print("Abscissa of Vertex {}:".format(i+1), end=" ")
        x = int(input())
        print("Ordinate of Vertex {}:".format(i+1), end=" ")
        y = int(input())

        vertex_list.append([x, y])

    adj_matrix = []

    adj_matrix = [[0 for j in range(vertex_num)] for i in range(vertex_num)]

    for i in range(vertex_num-1):
        for j in range(i+1, vertex_num):
            print("EDGE[",i+1, "][",j+1, "] = ", end=" ")
            adj_matrix[i][j] = int(input())

            if (adj_matrix[i][j] == 1):
                edge_list.append([i, j])

    return {
        "vertex_list": vertex_list,
        "edge_list": edge_list
    }

if __name__ == "__main__":
    inp = input_graph()
    g = DCEL(inp["vertex_list"], inp["edge_list"])
    g.build()
    g.print_vertex_record()
    g.print_face_record()    
    g.print_hedge_list()