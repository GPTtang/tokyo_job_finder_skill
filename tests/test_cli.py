from job_finder.cli import build_parser


def test_cli_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["hello world"])
    assert args.query == "hello world"
    assert args.top_n == 5
