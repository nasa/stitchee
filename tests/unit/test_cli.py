from concatenator.run_stitchee import parse_args


def test_parser():
    parsed = parse_args(
        ["ncfile1", "ncfile2", "ncfile3", "-o", "outfile", "--concat_dim", "mirror_step"]
    )

    assert parsed.input == ["ncfile1", "ncfile2", "ncfile3"]
    assert parsed.output_path == "outfile"
    assert parsed.concat_dim == "mirror_step"
    assert parsed.concat_method == "xarray-concat"
    assert parsed.verbose is False
