"""Tests for dynamic structure factor."""
import numpy as np

from phonopy.spectrum.dynamic_structure_factor import atomic_form_factor_WK1995

# D. Waasmaier and A. Kirfel, Acta Cryst. A51, 416 (1995)
# f(Q) = \sum_i a_i \exp((-b_i Q^2) + c
# Q is in angstron^-1
# a1, b1, a2, b2, a3, b3, a4, b4, a5, b5, c
f_params = {
    "Na": [
        3.148690,
        2.594987,
        4.073989,
        6.046925,
        0.767888,
        0.070139,
        0.995612,
        14.1226457,
        0.968249,
        0.217037,
        0.045300,
    ],  # 1+
    "Cl": [
        1.061802,
        0.144727,
        7.139886,
        1.171795,
        6.524271,
        19.467656,
        2.355626,
        60.320301,
        35.829404,
        0.000436,
        -34.916604,
    ],  # 1-
    "Si": [
        5.275329,
        2.631338,
        3.191038,
        33.730728,
        1.511514,
        0.081119,
        1.356849,
        86.288640,
        2.519114,
        1.170087,
        0.145073,
    ],  # neutral
    "Pb": [
        32.505656,
        1.047035,
        20.014240,
        6.670321,
        14.645661,
        0.105279,
        5.029499,
        16.525040,
        1.760138,
        0.105279,
        4.044678,
    ],  # 4+
    "Pb0": [
        16.419567,
        0.105499,
        32.738592,
        1.055049,
        6.530247,
        25.025890,
        2.342742,
        80.906596,
        19.916475,
        6.664449,
        4.049824,
    ],
    "Te": [
        6.660302,
        33.031656,
        6.940756,
        0.025750,
        19.847015,
        5.065547,
        1.557175,
        84.101613,
        17.802427,
        0.487660,
        -0.806668,
    ],
}  # neutral

data_AFF = """248.850565 475.343599 311.677408   3.366711  36.056296  21.483224
 82.365351  99.110882  83.948752  14.942481  23.782387  21.646822
 11.187047  69.752013  40.711983  36.755913   1.604680  21.908905
 10.893951  35.492508  25.647178   0.015083  38.102914  22.174849
 26.292983   4.990025  19.185649   3.407326  34.395335  22.317923
 23.333359   0.849180  16.551902   1.693118  35.547834  22.156062
  4.345407  17.080822   0.403188  35.756785  16.372371  21.360953
  1.520809  20.821735  33.264292   0.454259  18.712018  19.205742
  2.080764  27.498627  25.906737   0.812446  24.860853  14.174950
 26.905801  22.309616   0.308225   8.702789  35.161038   5.947680"""

data_b = """419.130446 1822.138324 963.242515  13.761210  59.574804  39.950123
197.165487 368.013923 260.035228  13.428822  59.928869  40.951942
  5.179328 248.664406 126.202841   9.703159  64.306530  42.148073
 23.998851 122.153147  79.243864   0.035467  74.818658  43.331628
 97.966965   0.468213  58.692973   1.328661  74.118529  44.206394
 12.580089  62.716603  49.697403   2.831812  72.515311  44.331894
 48.416674  16.811463   4.914526  68.931708  47.766185  42.920032
 65.462476   0.000000   0.000000  68.889885  52.478615  38.287576
 14.660547  66.825066  39.113987  13.994019  66.322994  27.156663
105.091902  19.498305   0.282731  14.487294  89.011152   9.748889"""


def _get_func_AFF(f_params):
    """Return atomic_form_factor function."""

    def func(symbol, Q):
        return atomic_form_factor_WK1995(Q, f_params[symbol])

    return func


def test_IXS_G_to_L(ph_nacl):
    """Test of dynamic structure factor calculation."""
    _test_IXS_G_to_L(ph_nacl)


def _test_IXS_G_to_L(phonon, verbose=True):
    mesh = [5, 5, 5]
    phonon.run_mesh(mesh, is_mesh_symmetry=False, with_eigenvectors=True)

    directions = np.array(
        [
            [0.5, 0.5, 0.5],
        ]
    )
    n_points = 11  # Gamma point is excluded, so will be len(S) = 10.
    G_points_cubic = ([7, 1, 1],)

    # Atomic form factor
    _run(
        phonon,
        G_points_cubic,
        directions,
        func_AFF=_get_func_AFF(f_params),
        n_points=n_points,
    )
    Q, S = phonon.get_dynamic_structure_factor()
    data_cmp = np.reshape([float(x) for x in data_AFF.split()], (-1, 6))
    if verbose:
        for S_at_Q in S:
            print(("%10.6f " * 6) % tuple(S_at_Q))

    # Treatment of degeneracy
    for i in ([0, 1], [2], [3, 4], [5]):
        np.testing.assert_allclose(
            S[:6, i].sum(axis=1), data_cmp[:6, i].sum(axis=1), atol=1e-5
        )
    for i in ([0, 1], [2, 3], [4], [5]):
        np.testing.assert_allclose(
            S[6:, i].sum(axis=1), data_cmp[6:, i].sum(axis=1), atol=1e-5
        )

    # Scattering lengths
    _run(
        phonon,
        G_points_cubic,
        directions,
        scattering_lengths={"Na": 3.63, "Cl": 9.5770},
        n_points=n_points,
    )
    Q, S = phonon.get_dynamic_structure_factor()
    data_cmp = np.reshape([float(x) for x in data_b.split()], (-1, 6))
    if verbose:
        for S_at_Q in S:
            print(("%10.6f " * 6) % tuple(S_at_Q))

    # Treatment of degeneracy
    for i in ([0, 1], [2], [3, 4], [5]):
        np.testing.assert_allclose(
            S[:6, i].sum(axis=1), data_cmp[:6, i].sum(axis=1), atol=1e-5
        )
    for i in ([0, 1], [2, 3], [4], [5]):
        np.testing.assert_allclose(
            S[6:, i].sum(axis=1), data_cmp[6:, i].sum(axis=1), atol=1e-5
        )


def plot_f_Q(f_params):
    """Plot f_Q."""
    import matplotlib.pyplot as plt

    x = np.linspace(0.0, 6.0, 101)
    for elem in ("Si", "Na", "Cl", "Pb", "Pb0", "Te"):
        y = [atomic_form_factor_WK1995(Q, f_params[elem]) for Q in x]
        plt.plot(x, y, label=elem)
    plt.xlim(xmin=0)
    plt.ylim(ymin=0)
    plt.legend()
    plt.show()


def show(phonon):
    """Show the calculation result along many directions."""
    directions = np.array(
        [
            [0.5, 0.5, 0.5],
            [-0.5, 0.5, 0.5],
            [0.5, -0.5, 0.5],
            [0.5, 0.5, -0.5],
            [0.5, -0.5, -0.5],
            [-0.5, 0.5, -0.5],
            [-0.5, -0.5, 0.5],
            [-0.5, -0.5, -0.5],
        ]
    )
    G_points_cubic = ([7, 1, 1],)
    _run(phonon, G_points_cubic, directions, verbose=True)


def _run(
    phonon,
    G_points_cubic,
    directions,
    func_AFF=None,
    scattering_lengths=None,
    n_points=51,
):
    P = [[0, 0.5, 0.5], [0.5, 0, 0.5], [0.5, 0.5, 0]]
    G_to_L = np.array(
        [directions[0] * x for x in np.arange(0, n_points) / float(n_points - 1)]
    )

    phonon.run_band_structure([G_to_L])

    T = 300
    for G_cubic in G_points_cubic:
        G_prim = np.dot(G_cubic, P)
        for direction in directions:
            direction_prim = np.dot(direction, P)
            G_to_L = np.array(
                [
                    direction_prim * x
                    for x in np.arange(1, n_points) / float(n_points - 1)
                ]
            )
            if func_AFF is not None:
                phonon.init_dynamic_structure_factor(
                    G_to_L + G_prim,
                    T,
                    atomic_form_factor_func=func_AFF,
                    freq_min=1e-3,
                )
            elif scattering_lengths is not None:
                phonon.init_dynamic_structure_factor(
                    G_to_L + G_prim,
                    T,
                    scattering_lengths=scattering_lengths,
                    freq_min=1e-3,
                )
            else:
                raise SyntaxError
            dsf = phonon.dynamic_structure_factor
            for i, S in enumerate(dsf):
                pass
