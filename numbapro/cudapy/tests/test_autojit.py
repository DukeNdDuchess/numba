import numpy as np
from numbapro import cuda
from .support import testcase, main, assertTrue

@testcase
def test_autojit():
    @cuda.autojit
    def what(a, b, c):
        pass

    what(np.empty(1), 1.0, 21)
    what(np.empty(1), 1.0, 21)
    what(np.empty(1), np.empty(1, dtype=np.int32), 21)
    what(np.empty(1), np.empty(1, dtype=np.int32), 21)
    what(np.empty(1), 1.0, 21)

    print what.definitions
    assertTrue(len(what.definitions) == 2)

if __name__ == '__main__':
    main()
