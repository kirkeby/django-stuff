import email

def test_empty():
    assert email.indent_lines('', None) == ''

def test_one_line():
    assert email.indent_lines('[test]', None) == '[test]'

def test_two_lines():
    assert email.indent_lines('[test]\nthis', None) == '[test]\n    this'
