def test_run(testdirectory):

    testdirectory.copy_file('test/cpp_library/coffee_machine.hpp')
    testdirectory.copy_file('test/cpp_library/Doxyfile')

    testdirectory.run('sphinx-quickstart --quiet --project cpp_coffee --author steinwurf -v 1.0.0')

    testdirectory.run('doxygen')

    pass
