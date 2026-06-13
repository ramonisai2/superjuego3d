"""Prueba de importador OBJ sin abrir ventana."""

from pathlib import Path

from motor_juegos.obj_asset_loader import (
    DEFAULT_OBJ_ASSET_REGISTRY,
    compact_obj_status,
    load_obj_mesh,
    obj_mesh_to_entity_buffer,
)


def main() -> int:
    root = Path(__file__).resolve().parent
    obj_path = root / "assets" / "models" / "obj_probe_crate.obj"
    mesh = load_obj_mesh(str(obj_path), normalize=True, target_size=1.0)
    buffer = obj_mesh_to_entity_buffer(mesh, mesh_id="obj_probe_crate", kind="probe")

    DEFAULT_OBJ_ASSET_REGISTRY.register("probe_crate", str(obj_path), normalize=True, target_size=1.0)
    cached = DEFAULT_OBJ_ASSET_REGISTRY.load("probe_crate")
    cached_again = DEFAULT_OBJ_ASSET_REGISTRY.load("probe_crate")

    assert mesh.triangle_count == 12, mesh.summary()
    assert mesh.vertex_count == 36, mesh.summary()
    assert buffer.vertex_count == 36, buffer.summary()
    assert cached is cached_again

    print("OBJ importer OK")
    print(compact_obj_status(mesh))
    print("buffer", buffer.summary())
    print("registry", DEFAULT_OBJ_ASSET_REGISTRY.stats())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
