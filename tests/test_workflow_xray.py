import unittest

from workflow_xray import analyse, health, load


class XrayTest(unittest.TestCase):
    def test_broken(self):
        _, acts, edges = load("examples/newsletter_broken.xml")
        f = analyse(acts, edges)
        msgs = " | ".join(f"{a}:{m}" for _, a, m in f)
        self.assertIn("gr_send:dead end", msgs)
        self.assertIn("audience:query has no filter", msgs)
        self.assertIn("old_cleanup:unreachable", msgs)
        self.assertIn("hr_send:delivery has no error branch", msgs)
        self.assertEqual(health(f), 0)

    def test_fixed_is_clean(self):
        _, acts, edges = load("examples/newsletter_fixed.xml")
        self.assertEqual(analyse(acts, edges), [])


if __name__ == "__main__":
    unittest.main()
