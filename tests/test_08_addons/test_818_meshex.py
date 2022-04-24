#  Copyright (c) 2022, Manfred Moitzi
#  License: MIT License

import pytest
from ezdxf.addons import meshex
from ezdxf.render import MeshBuilder
from ezdxf.render.forms import cube
from ezdxf.version import __version__


class TestStlLoader:
    def test_empty_file_returns_empty_mesh(self):
        mesh = meshex.stl_loads("")
        assert len(mesh.vertices) == 0

    def test_load_a_single_face(self):
        """This is the minimum required format accuracy the parser needs"""
        mesh = meshex.stl_loads(
            "vertex 0 0 0\nvertex 1 0 0\nvertex 1 1 0\nendloop\n"
        )
        assert mesh.vertices[0] == (0, 0, 0)
        assert mesh.vertices[1] == (1, 0, 0)
        assert mesh.vertices[2] == (1, 1, 0)
        assert mesh.faces[0] == (0, 1, 2)

    def test_parsing_error_too_few_axis(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0 0")

    def test_parsing_error_invalid_coordinate_format(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0, 0, 0")

    def test_parsing_error_invalid_floats(self):
        with pytest.raises(meshex.ParsingError):
            meshex.stl_loads("vertex 0 0 z")


OFF_VALID_1 = """OFF
# just a comment
8 6 0
-0.500000 -0.500000 0.500000  #  ignor this
0.500000 -0.500000 0.500000
-0.500000 0.500000 0.500000
0.500000 0.500000 0.500000
-0.500000 0.500000 -0.500000
0.500000 0.500000 -0.500000
-0.500000 -0.500000 -0.500000
0.500000 -0.500000 -0.500000
4 0 1 3 2  # ignore this
4 2 3 5 4
4 4 5 7 6
4 6 7 1 0
4 1 7 5 3
4 6 0 2 4
"""

OFF_VALID_2 = """OFF 8 6 0  # ignore this
-0.500000 -0.500000 0.500000  #  ignore this
0.500000 -0.500000 0.500000
-0.500000 0.500000 0.500000
0.500000 0.500000 0.500000
-0.500000 0.500000 -0.500000
0.500000 0.500000 -0.500000
-0.500000 -0.500000 -0.500000
0.500000 -0.500000 -0.500000
4 0 1 3 2  # ignore this
4 2 3 5 4
4 4 5 7 6
4 6 7 1 0
4 1 7 5 3
4 6 0 2 4


# ignore this
"""


class TestOFFLoader:
    @pytest.mark.parametrize("data", [OFF_VALID_1, OFF_VALID_2])
    def test_valid_data(self, data):
        mesh = meshex.off_loads(data)
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 6

    def test_minimal_data(self):
        mesh = meshex.off_loads("3 1 0\n0 0 0\n 0 1 0\n1 1 0\n3 0 1 2")
        assert len(mesh.vertices) == 3
        assert len(mesh.faces) == 1

    @pytest.mark.parametrize(
        "data",
        [
            "",  # no data
            "OFF",  # no data
            "OFF 8 6 0",  # invalid data count
            "OFF 8 6 0\n1 2 3",  # invalid data count
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 Z\n3 0 1 2\n ",  # vertex parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0\n3 0 1 2\n ",  # vertex parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 0\n3 0 1\n ",  # face parsing error
            "OFF 3 1 0\n0 0 0\n 0 0 0\n0 0 0\n3 0 1 z\n ",  # face parsing error
        ],
    )
    def test_parsing_error_invalid_data_raises_parsing_error(self, data):
        with pytest.raises(meshex.ParsingError):
            meshex.off_loads(data)


class TestOBJLoader:
    def test_empty_file_returns_empty_mesh(self):
        meshes = meshex.obj_loads("")
        assert len(meshes) == 0

    @pytest.mark.parametrize(
        "s",
        [
            "v 0 0 0\nv 1 0 0\nv 1 1 0\nf 1 2 3\n",
            "g\nv 0 0 0\nv 1 0 0\nv 1 1 0\ng\nf 1 2 3\n",
        ],
    )
    def test_load_a_single_face(self, s):
        meshes = meshex.obj_loads(s)  # OBJ is 1-indexed
        mesh = meshes[0]
        assert mesh.vertices[0] == (0, 0, 0)
        assert mesh.vertices[1] == (1, 0, 0)
        assert mesh.vertices[2] == (1, 1, 0)
        assert mesh.faces[0] == (0, 1, 2)

    def test_parsing_error_too_few_axis(self):
        with pytest.raises(meshex.ParsingError):
            meshex.obj_loads("v 0 0")

    def test_parsing_error_invalid_coordinate_format(self):
        with pytest.raises(meshex.ParsingError):
            meshex.obj_loads("v 0, 0, 0")

    def test_parsing_error_invalid_floats(self):
        with pytest.raises(meshex.ParsingError):
            meshex.obj_loads("v 0 0 z")


STL_SINGLE_TRIANGLE = f"""solid STL generated by ezdxf {__version__}
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 1.0 0.0 0.0
      vertex 1.0 1.0 0.0
    endloop
  endfacet
endsolid
"""


class TestSTLDumpString:
    def test_single_face(self):
        mesh = MeshBuilder()
        mesh.add_face([(0, 0), (1, 0), (1, 1)])
        result = meshex.stl_dumps(mesh)
        assert result == STL_SINGLE_TRIANGLE

    def test_dump_and_load_cube_ascii(self):
        mesh = meshex.stl_loads(meshex.stl_dumps(cube()))
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 12

    def test_dump_and_load_cube_binary(self):
        mesh = meshex.stl_loadb(meshex.stl_dumpb(cube()))
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 12


OFF_SINGLE_TRIANGLE = """OFF
3 1 0
0.0 0.0 0.0
1.0 0.0 0.0
1.0 1.0 0.0
3 0 1 2
"""


class TestOFFDumpString:
    def test_single_face(self):
        mesh = MeshBuilder()
        mesh.add_face([(0, 0), (1, 0), (1, 1)])
        result = meshex.off_dumps(mesh)
        assert result == OFF_SINGLE_TRIANGLE

    def test_dump_and_load_cube(self):
        mesh = meshex.off_loads(meshex.off_dumps(cube()))
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 6


OBJ_SINGLE_TRIANGLE = f"""# OBJ generated by ezdxf {__version__}
v 0.0 0.0 0.0
v 1.0 0.0 0.0
v 1.0 1.0 0.0
f 1 2 3
"""


class TestOBJDumpString:
    def test_single_face(self):
        mesh = MeshBuilder()
        mesh.add_face([(0, 0), (1, 0), (1, 1)])
        result = meshex.obj_dumps(mesh)
        assert result == OBJ_SINGLE_TRIANGLE

    def test_dump_and_load_cube(self):
        mesh = meshex.obj_loads(meshex.obj_dumps(cube()))[0]
        assert len(mesh.vertices) == 8
        assert len(mesh.faces) == 6


OPENSCAD_SINGLE_TRIANGLE = """polyhedron(points = [
  [0.0, 0.0, 0.0],
  [1.0, 0.0, 0.0],
  [1.0, 1.0, 0.0],
], faces = [
  [0, 1, 2],
], convexity = 10);
"""

OPENSCAD_INVERTED_CUBE = """polyhedron(points = [
  [-0.5, -0.5, -0.5],
  [0.5, -0.5, -0.5],
  [0.5, 0.5, -0.5],
  [-0.5, 0.5, -0.5],
  [-0.5, -0.5, 0.5],
  [0.5, -0.5, 0.5],
  [0.5, 0.5, 0.5],
  [-0.5, 0.5, 0.5],
], faces = [
  [1, 2, 3, 0],
  [7, 6, 5, 4],
  [4, 5, 1, 0],
  [5, 6, 2, 1],
  [2, 6, 7, 3],
  [3, 7, 4, 0],
], convexity = 10);
"""


class TestOpenSCADDumpString:
    def test_single_face(self):
        mesh = MeshBuilder()
        mesh.add_face([(0, 0), (1, 0), (1, 1)])
        result = meshex.scad_dumps(mesh)
        assert result == OPENSCAD_SINGLE_TRIANGLE

    def test_inverted_cube(self):
        """OpenSCAD expects inward pointing normals, make sure to flip normals
        before exporting to OpenSCAD! The import by OpenSCAD works also with
        outwards pointing normals but boolean operations will fail.
        """
        mesh = cube()
        mesh.flip_normals()
        result = meshex.scad_dumps(mesh)
        assert result == OPENSCAD_INVERTED_CUBE


def test_ifc_guid_compression():
    guid_hex = "a1207e36d39f4c629e6544dc9d6e27c9"
    ifc_guid = meshex._guid_compress(guid_hex)
    assert len(ifc_guid) == 22
    assert ifc_guid == "2X87usqvzCOfvbHDoTRYV9"


class TestRecords:
    @pytest.fixture
    def records(self):
        return meshex.Records()

    def test_add_record_returns_record_number(self, records):
        rec = records.add("IFCSHAPEREPRESENTATION(#31,'Body','Brep',#32);")
        assert rec == "#1"
        assert records.prev_num == 0
        assert records.last_num == 1
        assert records.next_num == 2

    def test_add_record_check_expected_record_number(self, records):
        with pytest.raises(ValueError):
            records.add("IFCSHAPEREPRESENTATION(#31,'Body','Brep',#32);", 7)

    def test_update_one_tag(self, records):
        records.add("IFCSHAPEREPRESENTATION($ENTITY$);")
        rec = records.add("IFCENTITY();")
        records.update("$ENTITY$", rec)
        assert records.get(1) == "IFCSHAPEREPRESENTATION(#2);"

    def test_update_multiple_tags(self, records):
        records.add("IFCSHAPEREPRESENTATION($ENTITY$,$XREF$);")
        rec1 = records.add("IFCENTITY();")
        rec2 = records.add("IFCXREF();")
        records.update("$ENTITY$", rec1)
        records.update("$XREF$", rec2)
        assert records.get(1) == "IFCSHAPEREPRESENTATION(#2,#3);"

    def test_dumps(self, records):
        records.add("IFCTAG1();")
        records.add("IFCTAG2();")
        assert records.dumps() == "#1= IFCTAG1();\n#2= IFCTAG2();"


if __name__ == "__main__":
    pytest.main([__file__])
