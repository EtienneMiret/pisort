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
