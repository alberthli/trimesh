import os
import platform

from .generic import MeshScript
from ..constants import log
from ..util import which

_search_path = os.environ['PATH']
if platform.system() == 'Windows':
    # split existing path by delimiter
    _search_path = [i for i in _search_path.split(';') if len(i) > 0]
    _search_path.append(r'C:\Program Files')
    _search_path.append(r'C:\Program Files (x86)')
    _search_path = ';'.join(_search_path)
    log.debug('searching for vhacd in: %s', _search_path)

_vhacd_executable = None
for _name in ['vhacd', 'testVHACD', 'TestVHACD']:
    _vhacd_executable = which(_name, path=_search_path)
    if _vhacd_executable is not None:
        break
exists = _vhacd_executable is not None


def convex_decomposition(mesh, debug=False, **kwargs):
    """
    Run VHACD to generate an approximate convex decomposition
    of a single mesh.

    Parameters
    --------------
    mesh : trimesh.Trimesh
      Mesh to be decomposed into convex components

    Returns
    ------------
    meshes : (n,) trimesh.Trimesh
      List of convex meshes
    """
    if not exists:
        raise ValueError('No vhacd available!')

    argstring = ' $MESH_0'

    # pass through extra arguments from the input dictionary
    for key, value in kwargs.items():
        argstring += ' -{} {}'.format(str(key),
                                       str(value))

    with MeshScript(meshes=[mesh],
                    script='',
                    exchange='obj',
                    group_material=False,
                    split_object=True,
                    debug=debug) as vhacd:
        result = vhacd.run(_vhacd_executable + argstring)

    # if we got a scene back return a list of meshes
    if hasattr(result, 'geometry') and isinstance(result.geometry, dict):
        return list(result.geometry.values())

    return result
