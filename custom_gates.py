import cirq
import numpy as np
import scipy


class QuditGate(cirq.Gate):
    def __init__(self, dimension=4, num_qubits=1):
        self.d = dimension
        self.n = num_qubits
        self.symbol = None

    def _num_qubits_(self):
        return self.n

    def _qid_shape_(self):
        return (self.d,) * self.n

    def _circuit_diagram_info_(self, args):
        return (self.symbol,) * self.n


class QuquartH(QuditGate):
    def __init__(self):
        super().__init__(dimension=4, num_qubits=1)

    def _unitary_(self):
        matrix_h_2 = np.identity(2, dtype='complex')
        matrix_h_2[0][1] = 1
        matrix_h_2[1][0] = 1
        matrix_h_2[1][1] = -1
        matrix_h_2 = 1 / np.sqrt(2) * matrix_h_2
        matrix_h = np.kron(matrix_h_2, matrix_h_2)
        return matrix_h

    def _circuit_diagram_info_(self, args):
        return "[H4]"


class InnerQuquartZZ(QuditGate):
    def __init__(self, theta=1):
        super().__init__(dimension=4, num_qubits=1)
        self.theta = theta

    def _unitary_(self):
        matrix_zz = np.identity(4, dtype='complex')
        matrix_zz[1][1] = matrix_zz[2][2] = np.exp(1j * self.theta * np.pi)
        return matrix_zz

    def _is_parameterized_(self) -> bool:
        return cirq.protocols.is_parameterized(self.theta)

    def _resolve_parameters_(self, resolver: 'cirq.ParamResolver', recursive: bool):
        return self.__class__(resolver.value_of(self.theta, recursive))

    def _circuit_diagram_info_(self, args):
        return f"[InnerZZ4]^{self.theta}"


class OuterQuquartZZ(QuditGate):
    def __init__(self, theta=1, first_state=0, second_state=1):
        super().__init__(dimension=4, num_qubits=2)
        self.theta = theta
        self.first_state = first_state
        self.second_state = second_state

    def _unitary_(self):
        all_states = ["0" * (4 - len(bin(i)[2:])) + bin(i)[2:] for i in range(16)]
        nums_for_exp = []
        for i, elem in enumerate(all_states):
            if elem[self.first_state] != elem[self.second_state]:
                nums_for_exp.append(i)
        matrix_zz = np.identity(16, dtype='complex')
        for num in nums_for_exp:
            matrix_zz[num][num] = np.exp(1j * self.theta * np.pi)
        return matrix_zz

    def _is_parameterized_(self) -> bool:
        return cirq.protocols.is_parameterized(self.theta)

    def _resolve_parameters_(self, resolver: 'cirq.ParamResolver', recursive: bool):
        return self.__class__(resolver.value_of(self.theta, recursive), self.first_state, self.second_state)

    def _circuit_diagram_info_(self, args):
        return f"[ZZ4-{self.first_state}]^{self.theta % 2}", f"[ZZ4-{self.second_state % 2}]^{self.theta}"


class QuquartX(QuditGate):
    def __init__(self, theta=1):
        super().__init__(dimension=4, num_qubits=1)
        self.theta = theta

    def _unitary_(self):
        return np.kron(scipy.linalg.expm(scipy.linalg.logm(np.array([[0, 1], [1, 0]])) * self.theta),
                       scipy.linalg.expm(scipy.linalg.logm(np.array([[0, 1], [1, 0]])) * self.theta))

    def _is_parameterized_(self) -> bool:
        return cirq.protocols.is_parameterized(self.theta)

    def _resolve_parameters_(self, resolver: 'cirq.ParamResolver', recursive: bool):
        return self.__class__(resolver.value_of(self.theta, recursive))

    def _circuit_diagram_info_(self, args):
        return f"[X4]^{self.theta}"
