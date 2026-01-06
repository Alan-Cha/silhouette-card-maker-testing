import os
from click.testing import CliRunner
from commands.create_pdf import create_pdf_cli

def test_basic_create_pdf():
  runner = CliRunner()
  result = runner.invoke(create_pdf_cli, "--front_dir_path test/basic/front --back_dir_path test/basic/back --output_path test/basic/output/game.pdf")
  assert result.exit_code == 0
  assert os.path.exists("test/basic/output/game.pdf")