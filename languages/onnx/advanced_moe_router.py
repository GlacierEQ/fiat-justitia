"""Build and execute a portable ONNX top-k Mixture-of-Experts router graph."""
from pathlib import Path

import numpy as np
import onnx
from onnx import TensorProto, checker, helper
from onnx.reference import ReferenceEvaluator

Path("build").mkdir(exist_ok=True)
tokens = helper.make_tensor_value_info("tokens", TensorProto.FLOAT, ["batch", "hidden"])
weights = helper.make_tensor_value_info("router_weights", TensorProto.FLOAT, ["hidden", "experts"])
values = helper.make_tensor_value_info("top_values", TensorProto.FLOAT, ["batch", 2])
indices = helper.make_tensor_value_info("top_indices", TensorProto.INT64, ["batch", 2])
k = helper.make_tensor("k", TensorProto.INT64, [1], [2])
nodes = [
    helper.make_node("MatMul", ["tokens", "router_weights"], ["logits"]),
    helper.make_node("Softmax", ["logits"], ["probabilities"], axis=-1),
    helper.make_node("TopK", ["probabilities", "k"], ["top_values", "top_indices"], axis=-1, largest=1, sorted=1),
]
graph = helper.make_graph(nodes, "portable-moe-router", [tokens, weights], [values, indices], [k])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
model.metadata_props.add(key="tower.evidence_state", value="tested")
model.metadata_props.add(key="tower.purpose", value="portable top-k expert routing")
checker.check_model(model)

runtime = ReferenceEvaluator(model)
representative_tokens = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
representative_weights = np.array(
    [[3.0, 1.0, 0.0], [0.0, 1.0, 3.0]],
    dtype=np.float32,
)
top_values, top_indices = runtime.run(
    None,
    {
        "tokens": representative_tokens,
        "router_weights": representative_weights,
    },
)
expected_indices = np.array([[0, 1], [2, 1]], dtype=np.int64)
if top_values.shape != (2, 2):
    raise RuntimeError(f"unexpected top-value shape: {top_values.shape}")
if not np.array_equal(top_indices, expected_indices):
    raise RuntimeError(f"unexpected expert ordering: {top_indices.tolist()}")
if not np.all(top_values[:, 0] >= top_values[:, 1]):
    raise RuntimeError("TopK output is not sorted by routing probability")

output = Path("build/advanced_moe_router.onnx")
onnx.save(model, output)
print(f"wrote and verified {output}")
