"""Unit tests for the skew symmetric matrices."""

import geomstats.backend as gs
import geomstats.tests
from geomstats.geometry.skew_symmetric_matrices import SkewSymmetricMatrices


class TestSkewSymmetricMatrices(geomstats.tests.TestCase):
    def setUp(self):
        self.n_seq = [2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.skew = {n: SkewSymmetricMatrices(n=n) for n in self.n_seq}

    def test_basis_is_skew_symmetric(self):
        result = []
        for n in self.n_seq:
            skew = self.skew[n]
            result.append(gs.all(skew.belongs(skew.basis)))
        result = gs.stack(result)
        expected = gs.array([True] * len(self.n_seq))
        self.assertAllClose(result, expected)

    def test_basis_has_the_right_dimension(self):
        for n in self.n_seq:
            skew = self.skew[n]
            self.assertEqual(int(n * (n - 1) / 2), skew.dim)

    def test_bch_up_to_fourth_order_works(self):
        for n in self.n_seq[1:]:
            skew = self.skew[n]
            first_base = skew.basis[0]
            second_base = skew.basis[1]

            expected = first_base + second_base
            result = skew.baker_campbell_hausdorff(first_base, second_base, order=1)
            self.assertAllClose(expected, result)

            lb_first_second = skew.bracket(first_base, second_base)
            expected = expected + 0.5 * lb_first_second
            result = skew.baker_campbell_hausdorff(first_base, second_base, order=2)
            self.assertAllClose(expected, result)

            expected = (
                expected
                + 1.0 / 12.0 * skew.bracket(first_base, lb_first_second)
                - 1.0 / 12.0 * skew.bracket(second_base, lb_first_second)
            )
            result = skew.baker_campbell_hausdorff(first_base, second_base, order=3)
            self.assertAllClose(expected, result)

            expected = expected - 1.0 / 24.0 * skew.bracket(
                second_base, skew.bracket(first_base, lb_first_second)
            )
            result = skew.baker_campbell_hausdorff(first_base, second_base, order=4)
            self.assertAllClose(expected, result)

    def test_basis_representation_is_correctly_vectorized(self):
        for n in self.n_seq:
            skew = self.skew[n]
            shape = gs.shape(skew.basis_representation(skew.basis))
            dim = int(n * (n - 1) / 2)
            self.assertAllClose(shape, (dim, dim))

    def test_matrix_and_basis_representation(self):
        for n in self.n_seq:
            skew = self.skew[n]
            vec = gs.random.rand(skew.dim)
            mat = skew.matrix_representation(vec)
            result = skew.basis_representation(mat)
            self.assertAllClose(result, vec)

    def test_belongs(self):
        mat = gs.array([[0.0, -1.0], [1.0, 0.0]])
        result = self.skew[2].belongs(mat)
        self.assertTrue(result)

        mat = gs.array([[0.0, -1.0], [1.0, 0.0], [0.0, 0.0]])
        result = self.skew[2].belongs(mat)
        self.assertFalse(result)

        result = self.skew[3].belongs(mat)
        self.assertFalse(result)

    def test_random_point_and_belongs(self):
        skew = self.skew[3]
        matrices = skew.random_point(4)
        result = skew.belongs(matrices)
        self.assertTrue(gs.all(result))
