import unittest

from app.src import test as workflow_test


class WorkflowTypingTests(unittest.TestCase):
    def test_rejects_param_value_with_wrong_type(self):
        with self.assertRaises(TypeError):
            workflow_test.validate_task_params(
                task_name="set_val",
                params={"value": "10"},
                param_types={"value": int},
            )

    def test_accepts_param_value_with_matching_type(self):
        workflow_test.validate_task_params(
            task_name="set_val",
            params={"value": 10},
            param_types={"value": int},
        )

    def test_uses_function_annotations_when_types_are_not_explicit(self):
        def sample(value: int):
            return value

        workflow_test.validate_task_params(
            task_name="sample",
            params={"value": 7},
            task_callable=sample,
        )


if __name__ == "__main__":
    unittest.main()
