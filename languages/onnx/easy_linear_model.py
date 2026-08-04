"""Create and validate a tiny ONNX Add graph."""
import onnx
from onnx import TensorProto, checker, helper

x = helper.make_tensor_value_info("x", TensorProto.FLOAT, [None, 4])
bias = helper.make_tensor("bias", TensorProto.FLOAT, [4], [1.0, 1.0, 1.0, 1.0])
y = helper.make_tensor_value_info("y", TensorProto.FLOAT, [None, 4])
node = helper.make_node("Add", ["x", "bias"], ["y"])
graph = helper.make_graph([node], "easy-linear", [x], [y], [bias])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 18)])
checker.check_model(model)
onnx.save(model, "build/easy_linear.onnx")
print("wrote build/easy_linear.onnx")
