# This source code is part of the Biotite package and is distributed
# under the 3-Clause BSD License. Please see 'LICENSE.rst' for further
# information.

from tempfile import TemporaryFile
import glob
import itertools
from os.path import join, splitext
import numpy as np
import pytest
from pytest import approx
import biotite.structure as struc
import biotite.structure.io.mmtf as mmtf
import biotite.structure.io.pdbx as pdbx
from ..util import data_dir


@pytest.mark.parametrize(
    "path", glob.glob(join(data_dir("structure"), "*.mmtf"))
)
def test_codecs(path):
    mmtf_file = mmtf.MMTFFile.read(path)
    for key in mmtf_file:
        if mmtf_file.get_codec(key) is not None:
            codec = mmtf_file.get_codec(key)
            param = mmtf_file.get_param(key)
            array1 = mmtf_file[key]
            mmtf_file.set_array(key, array1, codec, param)
            array2 = mmtf_file[key]
            if array1.dtype == np.float32:
                if param != 0:
                    tol = 1/param
                else:
                    tol = 0
                assert np.isclose(array1, array2, atol=tol).all()
            else:
                assert (array1 == array2).all()


@pytest.mark.parametrize(
    "path, single_model",
    itertools.product(
        glob.glob(join(data_dir("structure"), "*.mmtf")),
        [False, True]
    )
)
def test_array_conversion(path, single_model):
    model = 1 if single_model else None
    mmtf_file = mmtf.MMTFFile.read(path)
    a1 = mmtf.get_structure(mmtf_file, model=model, include_bonds=True)
    
    mmtf_file = mmtf.MMTFFile()
    mmtf.set_structure(mmtf_file, a1)
    temp = TemporaryFile("w+b")
    mmtf_file.write(temp)

    temp.seek(0)
    mmtf_file = mmtf.MMTFFile.read(temp)
    temp.close()
    a2 = mmtf.get_structure(mmtf_file, model=model, include_bonds=True)
    
    for category in a1.get_annotation_categories():
        assert a1.get_annotation(category).tolist() == \
               a2.get_annotation(category).tolist()
    assert a1.coord.flatten().tolist() == \
           approx(a2.coord.flatten().tolist(), abs=1e-3)
    assert a1.bonds == a2.bonds
    if a1.box is not None:
        assert np.allclose(a1.box, a2.box)


@pytest.mark.parametrize(
    "path, single_model",
    itertools.product(
        glob.glob(join(data_dir("structure"), "*.mmtf")),
        [False, True]
    )
)
def test_pdbx_consistency(path, single_model):
    model = None if single_model else 1
    cif_path = splitext(path)[0] + ".cif"
    mmtf_file = mmtf.MMTFFile.read(path)
    a1 = mmtf.get_structure(mmtf_file, model=model)
    pdbx_file = pdbx.PDBxFile.read(cif_path)
    a2 = pdbx.get_structure(pdbx_file, model=model)
    # Sometimes mmCIF files can have 'cell' entry
    # but corresponding MMTF file has not 'unitCell' entry
    # -> Do not assert for dummy entry in mmCIF file
    # (all vector elements = {0, 1})
    if a2.box is not None and not ((a2.box == 0) | (a2.box == 1)).all():
        assert np.allclose(a1.box, a2.box)
    for category in a1.get_annotation_categories():
        assert a1.get_annotation(category).tolist() == \
               a2.get_annotation(category).tolist()
    assert a1.coord.flatten().tolist() == \
           approx(a2.coord.flatten().tolist(), abs=1e-3)


def test_extra_fields():
    path = join(data_dir("structure"), "1l2y.mmtf")
    mmtf_file = mmtf.MMTFFile.read(path)
    stack1 = mmtf.get_structure(
        mmtf_file,
        extra_fields=[
            "atom_id", "b_factor", "occupancy", "charge"
        ]
    )

    mmtf_file == mmtf.MMTFFile()
    mmtf.set_structure(mmtf_file, stack1)
    
    stack2 = mmtf.get_structure(
        mmtf_file,
        extra_fields=[
            "atom_id", "b_factor", "occupancy", "charge"
        ]
    )
    
    assert stack1.atom_id.tolist() == stack2.atom_id.tolist()
    assert stack1.b_factor.tolist() == approx(stack2.b_factor.tolist())
    assert stack1.occupancy.tolist() == approx(stack2.occupancy.tolist())
    assert stack1.charge.tolist() == stack2.charge.tolist()


def test_numpy_objects():
    """
    Test whether the Msgpack encoder is able to handle NumPy values
    (e.g. np.float32) properly.

    Only check if no error occurs.
    """
    mmtf_file = mmtf.MMTFFile()
    mmtf_file["A float"] = np.float32(42.0)
    mmtf_file["A list"] = [np.int64(1), np.int64(2), np.int64(3)]
    mmtf_file["A dictionary"] = {"a": np.bool(True), "b": np.bool(False)}
    temp = TemporaryFile("w+b")
    mmtf_file.write(temp)
    temp.close()
