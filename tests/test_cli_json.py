from job_finder.cli import build_parser


def test_cli_parser_json_output():
    parser = build_parser()
    args = parser.parse_args(["hello world", "--output", "json", "--pretty"])
    assert args.output == "json"
    assert args.pretty is True
