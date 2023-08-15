import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from pisort import Arguments


class Exit(Exception):
    pass


def mock_exit():
    return Mock(side_effect=Exit())


@patch("pisort.exit", new_callable=mock_exit)
@patch("pisort.print")
class ArgumentsTest(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_default_directory(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test"])

        self.assertEqual(Path(), arguments.directory)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_parsed_directory(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", self.temp_dir.name])

        self.assertEqual(Path(self.temp_dir.name), arguments.directory)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_reject_non_existent(self, print_mock: Mock, exit_mock: Mock) -> None:
        path = Path(self.temp_dir.name) / "foo"

        self.assertRaises(Exit, Arguments, ["test", str(path)])

        print_mock.assert_called_once_with(f"test: No such directory: {str(path)}", file=sys.stderr)
        exit_mock.assert_called_once_with(1)

    def test_reject_file(self, print_mock: Mock, exit_mock: Mock) -> None:
        file = Path(self.temp_dir.name) / "foo"
        file.touch()

        self.assertRaises(Exit, Arguments, ["test", str(file)])

        print_mock.assert_called_once_with(f"test: Not a directory: {str(file)}", file=sys.stderr)
        exit_mock.assert_called_once_with(1)

    def test_reject_too_many_args(self, print_mock: Mock, exit_mock: Mock) -> None:
        self.assertRaises(Exit, Arguments, ["test", "a", "b", "c", "c"])

        print_mock.assert_called_once_with("test: Too many arguments", file=sys.stderr)
        exit_mock.assert_called_once_with(1)

    def test_support_dash_dash_terminator(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--"])

        self.assertEqual(Path(), arguments.directory)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_dash_dast_terminates_options(self, print_mock: Mock, exit_mock: Mock) -> None:
        self.assertRaises(Exit, Arguments, ["test", "--", "--name=Vacations"])

        print_mock.assert_called_once_with("test: No such directory: --name=Vacations", file=sys.stderr)
        exit_mock.assert_called_once_with(1)

    def test_can_specify_name_using_space(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--name", "Holidays"])

        self.assertEqual("Holidays", arguments.name)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_can_specify_name_using_equal(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--name=New York trip"])

        self.assertEqual("New York trip", arguments.name)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_name_is_None_by_default(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--"])

        self.assertIsNone(arguments.name)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_can_specify_name_and_directory(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--name", "New home", "--", self.temp_dir.name])

        self.assertEqual(Path(self.temp_dir.name), arguments.directory)
        self.assertEqual("New home", arguments.name)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_keep_good_name_by_default(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test"])

        self.assertTrue(arguments.keep_good_names)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_no_keep(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--no-keep"])

        self.assertFalse(arguments.keep_good_names)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_keep(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--keep"])

        self.assertTrue(arguments.keep_good_names)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_keep_good_names_if_keep_is_last(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--keep", "--no-keep", "--no-keep", "--keep"])

        self.assertTrue(arguments.keep_good_names)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()

    def test_rename_all_if_no_keep_is_last(self, print_mock: Mock, exit_mock: Mock) -> None:
        arguments = Arguments(["test", "--keep", "--no-keep", "--keep", "--no-keep"])

        self.assertFalse(arguments.keep_good_names)
        print_mock.assert_not_called()
        exit_mock.assert_not_called()
